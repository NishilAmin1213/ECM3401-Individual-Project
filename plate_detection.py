import cv2
import asyncio
from fastanpr import FastANPR
from PIL import Image


#    Title: fastanpr
#    Author: Arvind Rajan
#    Date: 16/04/2024
#    Code version: 0.1.13 *At time of writing this
#    Availability: https://pypi.org/project/fastanpr/
async def _run_anpr(image):
    """
    Function to use the FastANPR Library to detect and read number plate from an image - only for use within this module
    :param image: numpy.ndarray representing the image to process
    :return: A List containing a List of NumberPlate objects
    """
    print('IMAGE TYPE')
    print(type(image))

    # create FastANPR object
    fast_anpr = FastANPR()

    # run fast_anpr on the image and wait for a response
    plate = await fast_anpr.run(image)

    # return information regarding the plate found
    return plate

def get_plate(file_path):
    """
    Function to call the _run_anpr function to run FastANPR on an image- for use by other modules - for use by other modules
    :param file_path: string representation of the absolute file path to the image
    :return: Dictionary containing the text and cropped image of the number plate found in the image
    """
    # Load the image and ensure that the color is RGB
    image = cv2.imread(file_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # use the run_anpr function and wait for a repsonse using async
    try:
        async_loop = asyncio.get_event_loop()
        plate = async_loop.run_until_complete(_run_anpr(image))[0][0]
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




