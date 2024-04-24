import ast
import tensorflow as tf
from layerscale import LayerScale

def deserialize_model(model_name, class_names_name, path='./models/', use_layerscale=False):
    """
    Function to deserialize a previously trained and serialized tensorflow model (for Vehicle Make Recognition)
    :param path: string representation of the path to a folder containing the files - default is './models/'
    :param model_name: the file name and extension of the model to deserialze
    :param class_names_name: the file name and extension of the class names for the model
    :param use_layerscale: boolean value to include the layerscale class when deserializing the model
    :return: tensorflow model and array of class names for the VMR model
    """

    # define the location for the model and class name
    model_location = path + model_name
    class_name_location = path + class_names_name

    # read the class name file and convert the data into an array
    f = open(class_name_location, "r")
    class_names = ast.literal_eval(f.read())

    custom_objects = {}
    if use_layerscale == True:
        # layerscale needs to be provided due to a bug with tensorflow and the ConvNeXtLarge serialization
        custom_objects = {"LayerScale": LayerScale}

    model = tf.keras.models.load_model(model_location, custom_objects=custom_objects)

    # Output some information to console
    print('Deserialized ' + model_name +' \nClass Names: ')
    print(class_names)
    print('')

    return model, class_names