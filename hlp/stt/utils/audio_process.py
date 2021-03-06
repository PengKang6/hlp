'''
Author: PengKang6
Description: 本模块主要作用
'''
import tensorflow as tf
from features import wav_to_feature


# 基于语音路径序列，处理成模型的输入tensor,以及获取输入的时间步长
def get_input_and_length(audio_data_path_list, audio_feature_type, maxlen):
    audio_feature_list = []
    input_length_list = []
    for audio_path in audio_data_path_list:
        audio_feature = wav_to_feature(audio_path, audio_feature_type)
        audio_feature_list.append(audio_feature)
        input_length_list.append([audio_feature.shape[0]])

    input_tensor = tf.keras.preprocessing.sequence.pad_sequences(
        audio_feature_list,
        maxlen=maxlen,
        dtype='float32',
        padding='post'
    )
    input_length = tf.convert_to_tensor(input_length_list)

    return input_tensor, input_length


# 获取最长的音频length(timesteps)
def get_max_audio_length(audio_data_path_list, audio_feature_type):
    return max(wav_to_feature(audio_path, audio_feature_type).shape[0] for audio_path in audio_data_path_list)


if __name__ == "__main__":
    pass
