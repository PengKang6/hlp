import re
import tensorflow as tf


# 基于数据文本规则的行获取
def text_row_process(line, text_row_style):
    if text_row_style == 1:
        # 当前数据文本的每行为'index string\n'
        return line.strip().split(" ", 1)[1].lower()
    elif text_row_style == 2:
        # 当前数据文本的每行为'index\tstring\n'
        return line.strip().split("\t", 1)[1].lower()
    elif text_row_style == 3:
        # 当前数据文本的每行为"string\n"
        return line.strip().lower()


# 此方法依据文本是中文文本还是英文文本，若为英文文本是按字符切分还是按单词切分
def split_sentence(line, mode):
    if mode.lower() == "cn":
        return split_sentence_cn(line)
    elif mode.lower() == "en_word":
        return split_sentence_en_word(line)
    elif mode.lower() == "en_char":
        return split_sentence_en_char(line)


# 获取最长的label_length
def get_max_label_length(text_int_sequences):
    max_label_length = 0
    for seq in text_int_sequences:
        max_label_length = max(max_label_length, len(seq))
    return max_label_length


def build_text_int_sequences(sentences, mode, word_index):
    # 基于文本按照某种mode切分文本
    splitted_sentences = split_sentences(sentences, mode)

    # 基于预处理时dataset_information中写入的word_index构建文本整形序列list
    text_int_sequences_list = get_text_int_sequences(splitted_sentences, word_index)

    return text_int_sequences_list


# 读取文本文件，并基于某种row_style来处理原始语料
def get_text_list(text_path, text_row_style):
    text_list = []
    with open(text_path, "r") as f:
        sentence_list = f.readlines()
    for sentence in sentence_list:
        text_list.append(text_row_process(sentence, text_row_style))
    return text_list


# 基于word_index和切割好的文本list得到数字序列list
def get_text_int_sequences(splitted_sentences, word_index):
    text_int_sequences = []
    for process_text in splitted_sentences:
        text_int_sequences.append(text_to_int_sequence(process_text, word_index))
    return text_int_sequences


# 对单行文本进行process_text转token整形序列
def text_to_int_sequence(process_text, word_index):
    int_sequence = []
    for c in process_text.split(" "):
        int_sequence.append(int(word_index[c]))
    return int_sequence


def split_sentences(sentences, mode):
    text_list = []
    for text in sentences:
        text_list.append(split_sentence(text, mode))
    return text_list


def get_label_and_length(text_int_sequences_list, max_label_length):
    target_length_list = []
    for text_int_sequence in text_int_sequences_list:
        target_length_list.append([len(text_int_sequence)])
    target_tensor_numpy = tf.keras.preprocessing.sequence.pad_sequences(
        text_int_sequences_list,
        maxlen=max_label_length,
        padding='post'
    )
    target_length = tf.convert_to_tensor(target_length_list)
    return target_tensor_numpy, target_length


def split_sentence_en_word(s):
    s = s.lower().strip()
    # 在单词与跟在其后的标点符号之间插入一个空格
    # 例如： "he is a boy." => "he is a boy ."
    s = re.sub(r"([?.!,])", r" \1 ", s)  # 切分断句的标点符号
    s = re.sub(r'[" "]+', " ", s)  # 合并多个空格

    # 除了 (a-z, A-Z, ".", "?", "!", ",")，将所有字符替换为空格
    s = re.sub(r"[^a-zA-Z?.!,]+", " ", s)
    s = s.strip()
    return s


def split_sentence_en_char(s):
    s = s.lower().strip()

    result = ""
    for i in s:
        if i == " ":
            result += "<space> "
        else:
            result += i + " "
    return result.strip()


def split_sentence_cn(s):
    s = s.lower().strip()

    s = [c for c in s]
    s = ' '.join(s)
    s = re.sub(r'[" "]+', " ", s)  # 合并多个空格
    s = s.strip()

    return s