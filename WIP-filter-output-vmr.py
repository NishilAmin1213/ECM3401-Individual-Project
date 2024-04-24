import matplotlib.pyplot as plt
from deserialize_h5 import *
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Flatten, Dense, Dropout
from keras.layers import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import SGD
import numpy as np
from matplotlib import pyplot as plt
from keras.models import Model


vmr_model, vmr_class_names = deserialize_model('VMR.h5', 'class_names_VMR.txt', use_layerscale=True)

model = vmr_model

model.summary()
print('SUMMARY COMPLETE')
quit()

# convolutional layers at 1, 3, 5, and 7
layer = model.layers

# only look at the first layer
filters, biases = model.layers[1].get_weights()
print(layer[1].name, filters.shape)

fig1=plt.figure(figsize=(8, 12))
columns=6
rows=8
n_filters = columns*rows
for i in range(1, n_filters+1):
    f=filters[:,:,:,i-1]
    fig1=plt.subplot(rows,columns,i)
    fig1.set_xticks([])
    fig1.set_yticks([])
    plt.imshow(f[:,:,0], cmap='gray')
plt.show()


conv_later_index = [1, 3, 5, 7]
#                  48, 32, 16, 10
dims = [[6, 8],
        [6, 4],
        [4, 4],
        [5, 2]]

outputs = [model.layers[i].output for i in conv_later_index]
model_short = Model(inputs=model.inputs, outputs=outputs)
print(model_short.summary())

# Input shape to the model is 224 x 224. SO resize input image to this shape.
from keras.preprocessing.image import load_img, img_to_array


# green - 3ef4a8e36b3e4500b501b7a6801476ee
# red - fb5cd94e7e0e4abfae602cf1803d28e1
# blue - 625c7db6c6b641c0a182151208ac4f97

img = load_img('./nptest1nobg.png', target_size=(224, 224))  # VGG user 224 as input

# convert the image to an array
img = img_to_array(img)
# expand dimensions to match the shape of model input
img = np.expand_dims(img, axis=0)

# Generate feature output by predicting on the input image
feature_output = model_short.predict(img)

columns = 5
rows = 2
for ftr in feature_output:
    # pos = 1
    fig = plt.figure(figsize=(12, 12))
    for i in range(1, columns * rows + 1):
        fig = plt.subplot(rows, columns, i)
        fig.set_xticks([])  # Turn off axis
        fig.set_yticks([])
        plt.imshow(ftr[0, :, :, i - 1], cmap='gray')
        # pos += 1
    plt.show()

