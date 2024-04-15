import ast
import tensorflow as tf
from layerscale import LayerScale


def deserialize_VMR(path='./models/'):
    """
    Function to deserialize a previously trained and serialized tensorflow model (for Vehicle Make Recognition)
    :param path: string representation of the path to a folder containing the files - default is './models/'
    :return: tensorflow model and array of class names for the VMR model
    """
    # define the location for the model and class name
    model_location = path + "VMR.h5"
    class_name_location = path + "class_names_VMR.txt"

    # read the class name file and convert the data into an array
    f = open(class_name_location, "r")
    class_names = ast.literal_eval(f.read())

    # load in the model, specifying the custom 'layerscale' object
    # the layerscale class must be passed in as there is a bug with tensorflow when
    # carrying out transfer learning with a ConvNeXt base model
    model = tf.keras.models.load_model(model_location, custom_objects={"LayerScale": LayerScale})

    # Output some information to console
    print('Deserialized VMR\nClass Names: ')
    print(class_names)
    print('')

    return model, class_names


def deserialize_VCOR(path='./models/'):
    """
    Function to deserialize a previously trained and serialized tensorflow model (for Vehicle Color Recognition)
    :param path: string representation of the path to a folder containing the files - default is './models/'
    :return: tensorflow model and array of class names for the VCOR model
    """
    # define the location for the model and class name
    model_location = path + "VCOR.h5"
    class_name_location = path + "class_names_VCOR.txt"

    # read the class name file and convert the data into an array
    f = open(class_name_location, "r")
    class_names = ast.literal_eval(f.read())

    # load in the model
    model = tf.keras.models.load_model(model_location)

    # Output some information to console
    print('Deserialized VCOR\nClass Names: ')
    print(class_names)
    print('')

    return model, class_names
