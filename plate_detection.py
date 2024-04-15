import cv2
import asyncio
from fastanpr import FastANPR
from PIL import Image

async def run_anpr(image):
    # create FastANPR object
    fast_anpr = FastANPR()

    # run fast_anpr on the image and wait for a response
    plate = await fast_anpr.run(image)

    # return information regarding the plate found
    return plate

def get_plate(file_path):
    # Load the image and ensure that the color is RGB
    image = cv2.imread(file_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # use the run_anpr function and wait for a repsonse using async
    try:
        async_loop = asyncio.get_event_loop()
        plate = async_loop.run_until_complete(run_anpr(image))[0][0]
        if plate.rec_text is None:
            return {'reg_found': False}
    except IndexError:
        return {'reg_found': False}

    # get the plate coordinates and crop the image to the number plate
    plate_coords = plate.det_box
    cropped_image = image[plate_coords[1]:plate_coords[3], plate_coords[0]:plate_coords[2]]
    # convert image to a PIL compatible image
    cropped_image = Image.fromarray(cropped_image)

    # return a dictionary containing the plate text and the cropped image
    return {'reg_found': True, 'reg_text': plate.rec_text, 'reg_image': cropped_image}




