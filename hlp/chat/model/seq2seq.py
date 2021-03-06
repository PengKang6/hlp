import tensorflow as tf
import utils.layers as layers
import common.utils as utils


def cell_layer(units: int, input_feature_dim: int, cell_type: str = 'lstm',
               if_bidirectional: bool = True) -> tf.keras.Model:
    """
    RNNCell层，其中可定义cell类型，是否双向
    Args:
        units: cell单元数
        input_feature_dim: 输入的特征维大小
        cell_type: cell类型，lstm/gru， 默认lstm
        if_bidirectional: 是否双向
    Returns:
    """
    inputs = tf.keras.Input(shape=(None, input_feature_dim))
    if cell_type == 'lstm':
        rnn = tf.keras.layers.LSTM(units=units, return_sequences=True, return_state=True,
                                   recurrent_initializer='glorot_uniform')
    elif cell_type == 'gru':
        rnn = tf.keras.layers.GRU(units=units, return_sequences=True, return_state=True,
                                  recurrent_initializer='glorot_uniform')
    else:
        print('cell执行了类型执行出错，定位细节参见log')
        utils.log_operator(level=10).info("cell执行了类型执行出错")

    if if_bidirectional:
        rnn = tf.keras.layers.Bidirectional(rnn)

    rnn_outputs = rnn(inputs)
    outputs = rnn_outputs[0]
    states = outputs[:, -1, :]

    return tf.keras.Model(inputs=inputs, outputs=[outputs, states])


def encoder(vocab_size: int, embedding_dim: int, enc_units: int, layer_size: int,
            cell_type: str, if_bidirectional: bool = True) -> tf.keras.Model:
    """
    seq2seq的encoder，主要就是使用Embedding和GRU对输入进行编码，
    这里需要注意传入一个初始化的隐藏层，随机也可以，但是我这里就
    直接写了一个隐藏层方法。
    Args:
        vocab_size: 词汇量大小
        embedding_dim: 词嵌入维度
        enc_units: 单元大小
        layer_size: encoder中内部RNN层数
        cell_type: cell类型，lstm/gru， 默认lstm
        if_bidirectional: 是否双向
    Returns:
    """
    inputs = tf.keras.Input(shape=(None,))
    outputs = tf.keras.layers.Embedding(vocab_size, embedding_dim)(inputs)

    for i in range(layer_size):
        outputs, states = cell_layer(units=enc_units, input_feature_dim=outputs.shape[-1],
                                     cell_type=cell_type, if_bidirectional=if_bidirectional)(outputs)

    return tf.keras.Model(inputs=inputs, outputs=[outputs, states])


def decoder(vocab_size: int, embedding_dim: int, dec_units: int, enc_units: int,
            layer_size: int, cell_type: str) -> tf.keras.Model:
    """
    seq2seq的decoder，将初始化的x、隐藏层和encoder的输出作为
    输入，encoder的输入用来和隐藏层进行attention，得到的上下文
    向量和x进行整合然后丢到gru里去，最后Dense输出一下
    Args:
        vocab_size: 词汇量大小
        embedding_dim: 词嵌入维度
        dec_units: decoder单元大小
        enc_units: encoder单元大小
        layer_size: encoder中内部RNN层数
        cell_type: cell类型，lstm/gru， 默认lstm
    Returns:
    """
    inputs = tf.keras.Input(shape=(None,))
    enc_output = tf.keras.Input(shape=(None, enc_units))
    hidden = tf.keras.Input(shape=(enc_units,))

    embeddings = tf.keras.layers.Embedding(vocab_size, embedding_dim)(inputs)
    context_vector, attention_weight = layers.BahdanauAttention(dec_units)(hidden, enc_output)
    outputs = tf.concat([tf.expand_dims(context_vector, 1), embeddings], axis=-1)

    for i in range(layer_size):
        # Decoder中不允许使用双向
        outputs, states = cell_layer(units=dec_units, input_feature_dim=outputs.shape[-1],
                                     cell_type=cell_type, if_bidirectional=False)(outputs)

    outputs = tf.reshape(outputs, (-1, outputs.shape[-1]))
    outputs = tf.keras.layers.Dense(vocab_size)(outputs)

    return tf.keras.Model(inputs=[inputs, enc_output, hidden], outputs=[outputs, states, attention_weight])
