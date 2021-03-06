# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 15:37:32 2020

@author: 九童
使用训练集进行模型评估
"""
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from model import las, las_d_w
from config import config
from hlp.utils import beamsearch
from hlp.stt.utils.metric import lers
from data_processing import load_dataset
from data_processing.generator import data_generator

if __name__ == "__main__":

    # 用测试集wav文件语音识别出中文 
    # 测试集wav文件
    wav_path = config.test_wav_path

    # 测试集文本标签
    label_path = config.test_label_path

    # 尝试实验不同大小的数据集
    test_num = config.test_num

    # 每一步mfcc所取得特征数
    n_mfcc = config.n_mfcc

    # 确定使用的model类型
    model_type = config.model_type

    embedding_dim = config.embedding_dim
    units = config.units
    d = config.d
    w = config.w
    emb_dim = config.emb_dim
    dec_units = config.dec_units
    batch_size = config.test_batch_size
    dataset_name = config.dataset_name
    audio_feature_type = config.audio_feature_type
    num_examples = config.test_num

    print("获取训练语料信息......")
    dataset_information = config.get_dataset_information()
    test_vocab_tar_size = dataset_information["vocab_tar_size"]
    optimizer = tf.keras.optimizers.Adam()

    # 选择模型类型
    if model_type == "las":
        model = las.las_model(test_vocab_tar_size, embedding_dim, units, batch_size)
    elif model_type == "las_d_w":
        model = las_d_w.las_d_w_model(test_vocab_tar_size, d, w, emb_dim, dec_units, batch_size)

    # 检查点
    checkpoint_dir = config.checkpoint_dir
    checkpoint_prefix = os.path.join(checkpoint_dir, config.checkpoint_prefix)
    checkpoint = tf.train.Checkpoint(optimizer=optimizer, model=model)

    # 恢复检查点目录 （checkpoint_dir） 中最新的检查点
    checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))

    results = []
    labels_list = []

    # 加载测试集数据生成器
    test_data = load_dataset.load_data(dataset_name, wav_path, label_path, "test", num_examples)
    batchs = len(test_data[0]) // batch_size
    print("构建数据生成器......")
    test_data_generator = data_generator(
        test_data,
        "test",
        batchs,
        batch_size,
        audio_feature_type,
        dataset_information["max_input_length"],
        dataset_information["max_label_length"]
    )

    word_index = dataset_information["word_index"]
    index_word = dataset_information["index_word"]
    max_label_length = dataset_information["max_label_length"]
    beam_search_container = beamsearch.BeamSearch(
        beam_size=config.beam_size,
        max_length=max_label_length,
        worst_score=0)

    for batch, (inp, targ) in zip(range(1, batchs + 1), test_data_generator):
        hidden = model.initialize_hidden_state()
        dec_input = tf.expand_dims([word_index['<start>']] * batch_size, 1)
        beam_search_container.reset(inputs=inp, dec_input=dec_input)
        inputs, decoder_input = beam_search_container.get_search_inputs()

        result = ''  # 识别结果字符串

        for t in range(max_label_length):  # 逐步解码或预测
            # predictions, dec_hidden = model(inp, hidden, dec_input)
            decoder_input = decoder_input[:, -1:]
            predictions, dec_hidden = model(inputs, hidden, decoder_input)

            beam_search_container.expand(predictions=predictions, end_sign=word_index['<end>'])
            if beam_search_container.beam_size == 0:
                break
            inputs, decoder_input = beam_search_container.get_search_inputs()

        beam_search_result = beam_search_container.get_result()
        beam_search_result = tf.squeeze(beam_search_result)
        for i in range(len(beam_search_result)):
            idx = str(beam_search_result[i].numpy())
            if index_word[idx] == '<end>':
                break
            elif index_word[idx] != '<start>':
                result += index_word[idx]

        results.append(result)
        labels_list.append(targ[0])
    print('results: {}'.format(results))
    print('labels_list: {}'.format(labels_list))
    rates_lers, aver_lers, norm_rates_lers, norm_aver_lers = lers(labels_list, results)

    print("字母错误率: ")
    print("每条语音字母错误数: ", rates_lers)
    print("所有语音平均字母错误数: ", aver_lers)
    print("每条语音字母错误率，错误字母数/标签字母数: ", norm_rates_lers)
    print("所有语音平均字母错误率: ", norm_aver_lers)
