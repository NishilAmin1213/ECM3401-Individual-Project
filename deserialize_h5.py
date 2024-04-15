import ast
import tensorflow as tf
from layerscale import LayerScale


def deserialize_VMR(path='./models/'):
    # define the location for the model and class name
    model_location = path + "VMR.h5"
    class_name_location = path + "class_names_VMR.txt"

    # read the class name file and convert the data into an array
    f = open(class_name_location, "r")
    class_names = ast.literal_eval(f.read())

    model = tf.keras.models.load_model(model_location, custom_objects={"LayerScale": LayerScale})

    print('Deserialized VMR\nClass Names: ')
    print(class_names)
    print('')

    return model, class_names


def deserialize_VCOR(path='./models/'):
    # define the location for the model and class name
    model_location = path + "VCOR.h5"
    class_name_location = path + "class_names_VCOR.txt"

    # read the class name file and convert the data into an array
    f = open(class_name_location, "r")
    class_names = ast.literal_eval(f.read())

    model = tf.keras.models.load_model(model_location)

    print('Deserialized VCOR\nClass Names: ')
    print(class_names)
    print('')

    return model, class_names
