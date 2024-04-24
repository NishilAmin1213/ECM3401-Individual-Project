from deserialize_h5 import *
import visualkeras
from PIL import ImageFont


model = tf.keras.applications.ConvNeXtLarge(
    include_top=True,
    weights='imagenet',
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation=None
)


#vcor_model, vcor_class_names = deserialize_VCOR()
#vmr_model, vmr_class_names = deserialize_VMR()

font = ImageFont.truetype("arial.ttf", 60)
visualkeras.layered_view(model, legend=True, font=font, to_file='vmr-cnl-out.png').show()

#visualkeras.layered_view(vcor_model, legend=True, font=font, scale_xy=1, scale_z=1, max_z=250, to_file='vcor-fcn-out.png').show()
#visualkeras.layered_view(vmr_model, legend=True, font=font, scale_xy=1, scale_z=1, max_z=250, to_file='vmr-fcn-out.png').show()


