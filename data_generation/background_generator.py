#!/usr/bin/env python

__author__ = "Ivan Gruber"
__version__ = "1.0.0"
__maintainer__ = "Ivan Gruber"
__email__ = "ivan.gruber@seznam.cz"

"""
Background generator based on VAE.
"""

import numpy as np
from tensorflow.keras.layers import Input, Dense, Lambda, Flatten, Reshape, Layer, BatchNormalization
from tensorflow.keras.layers import Conv2D, Conv2DTranspose
from tensorflow.keras.models import Model
from tensorflow.keras import backend as k
from tensorflow.keras import metrics
from tensorflow.keras import optimizers
import cv2


def load_model(model_path):
    """
    Function which load the model.

    :type model_path: path to the h5 f

    :return generator: model of generator
    """
    # input image dimensions
    img_rows, img_cols, img_chns = 128, 96, 3
    filters = 64
    num_conv = 3

    # batch_size = 32
    if k.image_data_format() == 'channels_first':
        original_img_size = (img_chns, img_rows, img_cols)
    else:
        original_img_size = (img_rows, img_cols, img_chns)
    latent_dim = 250
    intermediate_dim = 500
    epsilon_std = 1.0

    x = Input(batch_shape=(None,) + original_img_size)

    # x = Input(batch_shape=(batch_size,) + (28,28,1))
    conv_1 = Conv2D(img_chns,
                    kernel_size=(2, 2),
                    padding='same', activation='relu')(x)
    conv_2 = BatchNormalization()(Conv2D(filters,
                                         kernel_size=(2, 2),
                                         padding='same', activation='relu',
                                         strides=(2, 2))(conv_1))
    conv_3 = Conv2D(filters,
                    kernel_size=num_conv,
                    padding='same', activation='relu',
                    strides=1)(conv_2)
    conv_4 = BatchNormalization()(Conv2D(filters,
                                         kernel_size=num_conv,
                                         padding='same', activation='relu',
                                         strides=1)(conv_3))
    flat = Flatten()(conv_4)
    hidden = Dense(intermediate_dim, activation='tanh')(flat)

    z_mean = Dense(latent_dim)(hidden)
    z_log_var = Dense(latent_dim)(hidden)

    def sampling(args):
        z_mean, z_log_var = args
        sh = k.shape(z_mean)
        epsilon = k.random_normal(shape=(sh[0], latent_dim),
                                  mean=0., stddev=epsilon_std)
        return z_mean + k.exp(z_log_var) * epsilon

    # note that "output_shape" isn't necessary with the TensorFlow backend
    # so you could write `Lambda(sampling)([z_mean, z_log_var])`
    z = Lambda(sampling, output_shape=(latent_dim,))([z_mean, z_log_var])

    # we instantiate these layers separately so as to reuse them later
    decoder_hid = Dense(intermediate_dim, activation='tanh')
    decoder_upsample = Dense(filters * img_rows // 2 * img_cols // 2, activation='relu')

    if k.image_data_format() == 'channels_first':
        output_shape = (None, filters, img_rows // 2, img_cols // 2)
    else:
        output_shape = (None, img_rows // 2, img_cols // 2, filters)

    decoder_reshape = Reshape(output_shape[1:])
    decoder_deconv_1 = Conv2DTranspose(filters,
                                       kernel_size=num_conv,
                                       padding='same',
                                       strides=1,
                                       activation='relu')
    decoder_deconv_2 = Conv2DTranspose(filters,
                                       kernel_size=num_conv,
                                       padding='same',
                                       strides=1,
                                       activation='relu')
    if k.image_data_format() == 'channels_first':
        output_shape = (None, filters, 29, 29)
    else:
        output_shape = (None, 29, 29, filters)
    decoder_deconv_3_upsamp = Conv2DTranspose(filters,
                                              kernel_size=(3, 3),
                                              strides=(2, 2),
                                              padding='valid',
                                              activation='relu')
    decoder_mean_squash = Conv2D(img_chns,
                                 kernel_size=2,
                                 padding='valid',
                                 activation='sigmoid')

    hid_decoded = decoder_hid(z)
    up_decoded = decoder_upsample(hid_decoded)
    reshape_decoded = decoder_reshape(up_decoded)
    deconv_1_decoded = decoder_deconv_1(reshape_decoded)
    deconv_2_decoded = decoder_deconv_2(deconv_1_decoded)
    x_decoded_relu = decoder_deconv_3_upsamp(deconv_2_decoded)
    x_decoded_mean_squash = decoder_mean_squash(x_decoded_relu)

    # Custom loss layer
    class CustomVariationalLayer(Layer):
        def __init__(self, **kwargs):
            self.is_placeholder = True
            super(CustomVariationalLayer, self).__init__(**kwargs)

        def vae_loss(self, x, x_decoded_mean_squash):
            x = k.flatten(x)
            x_decoded_mean_squash = k.flatten(x_decoded_mean_squash)
            xent_loss = img_rows * img_cols * metrics.binary_crossentropy(x, x_decoded_mean_squash)
            kl_loss = - 0.5 * k.mean(1 + z_log_var - k.square(z_mean) - k.exp(z_log_var), axis=-1)
            return k.mean(xent_loss + kl_loss)

        def call(self, inputs):
            x = inputs[0]
            x_decoded_mean_squash = inputs[1]
            loss = self.vae_loss(x, x_decoded_mean_squash)
            self.add_loss(loss, inputs=inputs)
            # We don't use this output.
            return x

    y = CustomVariationalLayer()([x, x_decoded_mean_squash])

    vae = Model(x, y)
    rms = optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)
    # sgd = optimizers.SGD(lr=0.0000001, momentum=0.0, decay=0.0, nesterov=True)
    vae.compile(optimizer=rms, loss=None)

    vae.load_weights(model_path)

    decoder_input = Input(shape=(latent_dim,))
    _hid_decoded = decoder_hid(decoder_input)
    _up_decoded = decoder_upsample(_hid_decoded)
    _reshape_decoded = decoder_reshape(_up_decoded)
    _deconv_1_decoded = decoder_deconv_1(_reshape_decoded)
    _deconv_2_decoded = decoder_deconv_2(_deconv_1_decoded)
    _x_decoded_relu = decoder_deconv_3_upsamp(_deconv_2_decoded)
    _x_decoded_mean_squash = decoder_mean_squash(_x_decoded_relu)
    generator = Model(decoder_input, _x_decoded_mean_squash)

    return generator


def get_background(generator, scale=0.15):
    """
    Generate one background image.

    :type generator: model object
    :type scale: parameter scale for numpy.random.normal, adjust texture of input images, original images scale = 0.15
    """
    z_sample = np.random.normal(scale=scale, size=(1, 250))
    x_decoded = generator.predict(z_sample, batch_size=1)
    background = cv2.resize(np.uint8(x_decoded[0] * 255), (2480, 3504), interpolation=cv2.INTER_LINEAR)

    return background
