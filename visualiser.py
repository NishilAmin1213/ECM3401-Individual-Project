from deserialize_h5 import *
import visualkeras
from PIL import ImageFont

#vcor_model, vcor_class_names = deserialize_VCOR()
#vmr_model, vmr_class_names = deserialize_VMR()
#model = vmr_model

model = tf.keras.applications.ConvNeXtLarge(
    include_top=True,
    weights='imagenet',
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation=None
)

model.summary()

font = ImageFont.truetype("arial.ttf", 32)
visualkeras.layered_view(model, legend=True, font=font).show()
#visualkeras.layered_view(model, legend=True, font=font, scale_xy=1, scale_z=1, max_z=250).show()


