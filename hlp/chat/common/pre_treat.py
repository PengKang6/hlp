import os
import json
import jieba
import numpy as np
from common.utils import log_operator

'''
对话数据集预处理模块
raw_data保存原数据集路径
tokenized_data保存分词后的数据集路径
'''


def check_file(raw_file: str, treat_file: str, if_remove: bool = True):
    """
    对原始文本进行检查是否存在
    删除已存在的分词文本
    Args:
        raw_file: 原始数据路径
        treat_file: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    if not os.path.exists(raw_file):
        print('数据集不存在，请添加数据集!')
        exit(0)
    # 如果if_remove为True且已经分词的文件存在，要删除，因为后面的读写操作是边读边写
    if os.path.exists(treat_file) and if_remove:
        os.remove(treat_file)


def preprocess_raw_data_qa_single(raw_data: str, qa_data: str, if_remove: bool = True):
    """
    单轮对话数据集处理模块
    用于处理已经分词好的多轮次数据集的方法，将数据集处理成问答对的形式
    Args:
        raw_data: 原始数据路径
        qa_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """

    check_file(raw_file=raw_data, treat_file=qa_data, if_remove=if_remove)

    count = 0
    sentences_count = 0
    max_len = 0
    min_len = 10000
    sentence_len = []
    one_pair = []

    # 对每一轮对话上下文进行配对，形成一问一答两个部分，如果遇到下一轮对话，直接跳过
    with open(raw_data, encoding="utf-8") as raw_file, open(qa_data, 'w', encoding="utf-8") as tokenized_file:
        for line in raw_file:
            line = line.strip('\n').replace('/', '')
            # line = re.sub(r"[%s]+" % punctuation, "", line)
            # 因为原始数据集中，是一轮一轮的对话排列的，所以需要注意的是
            # 在一轮对话结束之后，最后一句不能作为问句，需要跳到下一轮进行处理
            if line == '':
                one_pair = []
                count += 1
                continue
            elif len(one_pair) == 1:
                one_pair.append(line)
                tokenized_file.write(one_pair[0] + "\t" + one_pair[1] + "\n")
                one_pair = [line]
                sentences_count += 1
                if sentences_count % 10000 == 0:
                    print('已处理：', sentences_count, '个问答对')
            else:
                one_pair.append(line)

            length = len(line)
            max_len = max(max_len, length)
            min_len = min(min_len, length)
            sentence_len.append(length)

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，整理出{}对" \
              "问答对，语句最大长度：{}，语句最短长度{}，语句平均长度{:.3f}".format(count, sentences_count,
                                                           max_len, min_len, np.mean(sentence_len))
    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def preprocess_raw_xiao_huang_ji_data(raw_data: str, tokenized_data: str, if_remove: bool = True):
    """
    用于处理小黄鸡数据集的方法，将小黄鸡数据集处理成多轮次对话的形式，并分词
    Args:
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    check_file(raw_file=raw_data, treat_file=tokenized_data, if_remove=if_remove)

    count = 1
    max_len = 0
    min_len = 10000
    sentence_len = []

    with open(raw_data, 'r', encoding="utf-8") as raw_file, open(tokenized_data, 'a',
                                                                 encoding="utf-8") as tokenized_file:
        for line in raw_file:
            line = line.strip('\n').replace('/', '')
            if line == "":
                tokenized_file.write("\n")
                count += 1
                if count % 10000 == 0:
                    print("已读取：{}轮对话数据".format(count))
                continue

            length = len(line)
            sentence_len.append(length)
            max_len = max(max_len, length)
            min_len = min(min_len, length)
            tokenized_file.write(" ".join(jieba.cut(line)) + "\n")

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，语句最大长度：{}，语" \
              "句最短长度{}，语句平均长度{:.3f}".format(count, max_len, min_len, np.mean(sentence_len))

    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def preprocess_raw_lccc_data(raw_data: str, tokenized_data: str, if_remove: bool = True):
    """
    用于处理LCCC数据集的方法，将LCCC数据集处理成多轮次对话的形式，并分词
    Args:
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    check_file(raw_file=raw_data, treat_file=tokenized_data, if_remove=if_remove)

    count = 0
    max_len = 0
    min_len = 10000
    sentence_len = []

    with open(raw_data, 'r', encoding="utf-8") as raw_file, open(tokenized_data, 'a',
                                                                 encoding="utf-8") as tokenized_file:
        raw_data = json.load(raw_file)
        for data in raw_data:
            for sentence in data:
                length = len(sentence)
                sentence_len.append(length)
                max_len = max(max_len, length)
                min_len = min(min_len, length)
                tokenized_file.write(sentence + "\n")
            tokenized_file.write("\n")
            count += 1
            if count % 10000 == 0:
                print("已读取：{}轮对话数据".format(count))

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，语句最大长度：{}，语" \
              "句最短长度{}，语句平均长度{:.3f}".format(count, max_len, min_len, np.mean(sentence_len))

    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def preprocess_raw_douban_data(raw_data: str, tokenized_data: str, repeat_data: int = 10, if_remove: bool = True):
    """
    用于处理douban数据集的方法，将douban数据集处理成多轮次对话的形式，并分词
    Args:
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        repeat_data: 每轮对话重复数据条数
        if_remove: 是否移除原有分词文本
    Returns:
    """
    check_file(raw_file=raw_data, treat_file=tokenized_data, if_remove=if_remove)

    count = 0
    max_len = 0
    min_len = 10000
    sentence_len = []

    with open(raw_data, 'r', encoding='utf-8') as raw_file, open(tokenized_data, 'a',
                                                                 encoding='utf-8') as tokenized_file:
        iter_count = -1
        for line in raw_file:
            iter_count += 1
            if iter_count % repeat_data != 0:
                continue
            line = line.strip('\n').replace('/', '')
            if line == "":
                continue

            # 因为原始数据集中，是一轮一轮的对话排列的，所以需要注意的是在一轮对话结束之后，最后
            # 一句不能作为问句，需要跳到下一轮进行处理去掉最前面的标签和最后面的不正确语句
            utterances = line.split('\t')[1:-1]
            for utterance in utterances:
                length = len(utterance)
                sentence_len.append(length)
                max_len = max(max_len, length)
                min_len = min(min_len, length)
                tokenized_file.write(utterance + "\n")
            tokenized_file.write("\n")
            count += 1
            if count % 10000 == 0:
                print("数据处理进度：{}".format(count))

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，语句最大长度：{}，语" \
              "句最短长度{}，语句平均长度{:.3f}".format(count, max_len, min_len, np.mean(sentence_len))

    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def preprocess_raw_cross_woz_data(raw_data: str, tokenized_data: str, if_remove: bool = True):
    """
    用于处理crossWOZ数据集的方法，将crossWOZ数据集处理成多轮次对话的形式，并分词
    Args:
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    check_file(raw_file=raw_data, treat_file=tokenized_data, if_remove=if_remove)

    count = 0
    max_len = 0
    min_len = 10000
    sentence_len = []

    with open(raw_data, 'r', encoding='utf-8') as raw_file, open(tokenized_data, 'a',
                                                                 encoding='utf-8') as tokenized_file:
        raw_data = json.load(raw_file)
        for data in raw_data:
            turn_utterances = raw_data[data]["messages"]
            for content in turn_utterances:
                sentence = content["content"]
                length = len(sentence)
                sentence_len.append(length)
                max_len = max(max_len, length)
                min_len = min(min_len, length)
                tokenized_file.write(" ".join(jieba.cut(sentence)) + "\n")
            tokenized_file.write("\n")
            count += 1
            if count % 10000 == 0:
                print("已读取：{}轮对话数据".format(count))

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，语句最大长度：{}，语" \
              "句最短长度{}，语句平均长度{:.3f}".format(count, max_len, min_len, np.mean(sentence_len))

    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def preprocess_raw_tie_ba_data(raw_data: str, tokenized_data: str, if_remove: bool = True):
    """
    用于处理TieBa数据集的方法，将TieBa数据集处理成多轮次对话的形式，并分词
    Args:
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    check_file(raw_file=raw_data, treat_file=tokenized_data, if_remove=if_remove)

    count = 0
    max_len = 0
    min_len = 10000
    sentence_len = []

    with open(raw_data, 'r', encoding='utf-8') as raw_file, open(tokenized_data, 'a',
                                                                 encoding='utf-8') as tokenized_file:
        for line in raw_file:
            line = line.strip("\n").replace("/", " ")
            if line == '':
                continue

            line = line.split("\t")
            for sentence in line:
                length = len(sentence)
                sentence_len.append(length)
                max_len = max(max_len, length)
                min_len = min(min_len, length)
                tokenized_file.write(" ".join(jieba.cut(sentence)) + "\n")
            tokenized_file.write("\n")

            count += 1
            if count % 10000 == 0:
                print("已读取：{}轮对话数据".format(count))

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，语句最大长度：{}，语" \
              "句最短长度{}，语句平均长度{:.3f}".format(count, max_len, min_len, np.mean(sentence_len))

    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def preprocess_raw_ppt_gossiping_data(raw_data: str, tokenized_data: str, if_remove: bool = True):
    """
    用于处理PPT-Gossiping数据集的方法，将PPT-Gossiping数据集处理成多轮次对话的形式，并分词
    Args:
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    # 由于原始数据格式和贴吧格式一致，直接调用贴吧数据处理方法
    preprocess_raw_tie_ba_data(raw_data, tokenized_data, if_remove=if_remove)


def preprocess_raw_wei_bo_data(raw_post_data: str, raw_response_data,
                               tokenized_data: str, if_remove: bool = True):
    """
    用于处理weibo数据集的方法，将weibo数据集处理成多轮次的形式，并分词
    Args:
        raw_post_data: 微博的post原始文本数据中的路径
        raw_response_data: 微博的response原始文本数据中的路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    check_file(raw_file=raw_post_data, treat_file=tokenized_data, if_remove=if_remove)
    if not os.path.exists(raw_response_data):
        print('数据集不存在，请添加数据集!')
        exit(0)

    count = 0
    max_len = 0
    min_len = 10000
    sentence_len = []

    with open(raw_post_data, 'r', encoding='utf-8') as post_file, open(
            raw_response_data, 'r', encoding='utf-8') as response_file, \
            open(tokenized_data, 'a', encoding='utf-8') as tokenized_file:
        for post_data, response_data in zip(post_file, response_file):
            post_data = post_data.strip("\n").replace("/", " ")
            response_data = response_data.strip("\n").replace("/", " ")
            if post_data == "" or response_data == "":
                continue

            post_len = len(post_data)
            response_len = len(response_data)
            max_len = max(max_len, post_len, response_len)
            min_len = min(min_len, post_len, response_len)
            sentence_len.append(post_len)
            sentence_len.append(response_len)
            tokenized_file.write(post_data + "\n" + response_data + "\n\n")

            count += 1
            if count % 10000 == 0:
                print("已读取：{}轮对话数据".format(count))

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，语句最大长度：{}，语" \
              "句最短长度{}，语句平均长度{:.3f}".format(count, max_len, min_len, np.mean(sentence_len))

    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def preprocess_raw_qin_yun_data(raw_data: str, tokenized_data: str, if_remove: bool = True):
    """
    用于处理青云数据集的方法，将青云数据集处理成多轮次的形式，并分词
    Args:
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    check_file(raw_file=raw_data, treat_file=tokenized_data, if_remove=if_remove)

    count = 0
    max_len = 0
    min_len = 10000
    sentence_len = []

    with open(raw_data, 'r', encoding='utf-8') as raw_file, open(
            tokenized_data, 'a', encoding='utf-8') as tokenized_file:
        for line in raw_file:
            line = line.strip().strip("\n").replace("/", " ")
            if line == "":
                continue

            for sentence in line.split("|"):
                sentence = sentence.strip()

                length = len(sentence)
                sentence_len.append(length)
                max_len = max(max_len, length)
                min_len = min(min_len, length)
                tokenized_file.write(" ".join(jieba.cut(sentence)) + "\n")
            tokenized_file.write("\n")

            count += 1
            if count % 10000 == 0:
                print("已读取：{}轮对话数据".format(count))

    message = "数据处理完毕，数据信息统计：共处理{}轮对话数据，语句最大长度：{}，语" \
              "句最短长度{}，语句平均长度{:.3f}".format(count, max_len, min_len, np.mean(sentence_len))

    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def combine_tokenized_data_single(standby_data: list, combine_data: str, if_remove: bool = True):
    """
    *单轮对话数据集处理模块*
    将所有已经分词好的问答对集中整合到一个文件中
    Args:
        standby_data: 分词好的数据文本路径
        combine_data: 汇总数据的文本路径
        if_remove: 是否移除原有分词文本
    Returns:
    """
    if os.path.exists(combine_data) and if_remove:
        os.remove(combine_data)

    count = 0
    file_count = 0

    for file_fn in standby_data:
        if not os.path.exists(file_fn):
            print("{}文件不存在，请检查之后再次运行".format(file_fn))
            exit(0)
        with open(file_fn, 'r', encoding='utf-8') as tokenized_file, open(combine_data, 'a',
                                                                          encoding='utf-8') as combine_file:
            for line in tokenized_file:
                line = line.strip().strip("\n").replace("/", " ")
                combine_file.write(line + "\n")
                count += 1
                if count % 10000 == 0:
                    print("数据处理进度：{}".format(count))

        file_count += 1

    message = "数据处理完毕，数据信息统计：共处理{}个分词文件，整理出{}条数据".format(file_count, count)
    print(message)
    logger = log_operator(level=10)
    logger.info(message)


def dispatch_tokenized_func_dict_single(operator: str, raw_data: str,
                                        tokenized_data: str, if_remove: bool = True, reserve_data: str = None):
    """
    *单轮对话数据集处理模块*
    用来整合目前所有数据处理方法，通过字典匹配进行调用，默认使用preprocess_raw_data_single
    Args:
        operator: 对应分词方法的名称，作为key，目前有：xiaohuangji，tieba，ppt_gossiping，lccc，douban，cross_woz
        raw_data: 原始数据路径
        tokenized_data: 生成token数据保存路径
        if_remove: 是否移除原有分词文本
        reserve_data: 原始文本备用参数
    Returns:
    """
    operation = {
        "xiao_huang_ji": lambda: preprocess_raw_xiao_huang_ji_data(raw_data, tokenized_data, if_remove),
        "tie_ba": lambda: preprocess_raw_tie_ba_data(raw_data, tokenized_data, if_remove),
        "ppt_gossiping": lambda: preprocess_raw_ppt_gossiping_data(raw_data, tokenized_data, if_remove),
        "lccc": lambda: preprocess_raw_lccc_data(raw_data, tokenized_data, if_remove),
        "dou_ban": lambda: preprocess_raw_douban_data(raw_data, tokenized_data, 2, if_remove),
        "cross_woz": lambda: preprocess_raw_cross_woz_data(raw_data, tokenized_data, if_remove),
        "wei_bo": lambda: preprocess_raw_wei_bo_data(raw_data, reserve_data, tokenized_data, if_remove),
        "qin_yun": lambda: preprocess_raw_qin_yun_data(raw_data, tokenized_data, if_remove)
    }

    operation.get(operator, "xiao_huang_ji")()


def raw_to_tokenized_and_combine_single(standby_data: dict, combine_data: str, if_save_tokenized: bool = False):
    """
    *单轮对话数据集处理模块*
    提供一次性将所有原始数据文本转换成分词文件，并整合到一个文件中
    Args:
        standby_data: 分词好的数据文本路径，分词方法匹配字典，key为对应的数据库名称，value为原始文本路径
                        目前提供的的方法有：{"xiao_huang_ji":"path","tie_ba":"path","ppt_gossiping":"path","lccc":"path",
                                            "dou_ban":"path","cross_woz":"path","wei_bo":"path","qin_yun":"path"}
        combine_data: 汇总数据的文本路径
        if_save_tokenized: 是否保留过程分词文件，如果为True，保留的各分词文件名直接在原始文件名后加tokenized，如lccc_tokenized.txt
    Returns:
    """
    tokenized_files = []
    for file in standby_data:
        print("正在处理{}语料".format(file))
        if if_save_tokenized:
            data_dir = "\\".join(standby_data[file].split("\\")[:-1])
            tokenized_dir = data_dir + "\\tokenized_data"
            tokenized_file = tokenized_dir + "\\" + file + "_tokenized.txt"
            if not os.path.exists(tokenized_dir):
                os.makedirs(tokenized_dir)
            dispatch_tokenized_func_dict_single(operator=file, raw_data=standby_data[file],
                                                tokenized_data=tokenized_file, if_remove=True)
            tokenized_files.append(tokenized_file)
            print("已保存{}语料的分词文本".format(file))
        else:
            dispatch_tokenized_func_dict_single(operator=file, raw_data=standby_data[file],
                                                tokenized_data=combine_data, if_remove=False)
            print("已合成{}语料".format(file))

    if if_save_tokenized:
        combine_tokenized_data_single(standby_data=tokenized_files, combine_data=combine_data)
    else:
        print("数据合成完毕，已保存至{}文件中，相关单文本信息已保存至日志文件中".format(combine_data))
