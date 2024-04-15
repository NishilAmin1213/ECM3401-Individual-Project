import os
import rembg
import tkinter as tk
import tensorflow as tf
from PIL import ImageTk, Image
from tkinter import filedialog, messagebox

from plate_detection import get_plate
from deserialize_h5 import deserialize_VCOR, deserialize_VMR
from plate_processor import process_plate


def VCOR_predict(file_path):
    """
    Function to predict the color of a vehicle
    :param file_path: string representation of the absolute file path to the image
    :return: string representation of the color of the vehicle
    """
    # load and preprocess the input image
    image = tf.keras.utils.load_img(
        # resize the image to the global variable, and ensure that the file has all 3 color channels as RGB
        file_path,
        color_mode='rgb',
        target_size=(vcor_IMAGE_SIZE, vcor_IMAGE_SIZE),
        keep_aspect_ratio=False
    )

    # adds a 'batch' dimension to the image and returns a Tensor object
    # (224, 224, 3) ----> (1, 224, 224, 3)
    image = tf.expand_dims(image, 0)

    # send the image through the VCOR model to get a Tensor holding an array of numeric predictions
    prediction = vcor_model(image)
    # extract the array from the Tensor and turn it into a list of numerical predictions
    prediction = prediction.numpy()[0].tolist()
    # find the index of the greatest value in the prediction array
    class_index = prediction.index(max(prediction))

    # return the class name belonging to that index - the predicted color of the input image
    return vcor_class_names[class_index]


def VMR_predict(file_path):
    """
    Function to predict the make of a vehicle
    :param file_path: string representation of the absolute file path to the image
    :return: string representation of the make of the vehicle
    """
    # load in and preprocess the input image
    image = tf.keras.utils.load_img(
        # resize the image to the global variable, and ensure that the file has all 3 color channels as RGB
        file_path,
        color_mode='rgb',
        target_size=(vmr_IMAGE_SIZE, vmr_IMAGE_SIZE),
        keep_aspect_ratio=False
    )

    # adds a 'batch' dimension to the image and returns a Tensor object
    # (224, 224, 3) ----> (1, 224, 224, 3)
    image = tf.expand_dims(image, 0)

    # send the image through the VCOR model to get a Tensor holding an array of numeric predictions
    prediction = vmr_model(image)
    # extract the array from the Tensor and turn it into a list of numerical predictions
    prediction = prediction.numpy()[0].tolist()
    # find the index of the greatest value in the prediction array
    class_index = prediction.index(max(prediction))

    # return the class name belonging to that index - the predicted color of the input image
    return vmr_class_names[class_index]


def process_input(file_path):
    """
    Function to process the file path taken in my the tkinter GUI
    :param file_path: string representation of the absolute file path to the image
    :return: a dictionary containing all the information about the vehicle in the image
    """
    tmp_location = './temp.png'

    # remove background from image and save it to a temporary location
    # do this using the rembg library
    rembg.remove(Image.open(file_path)).save(tmp_location)

    # get the predictions of the vehicle color and make
    predicted_color = VCOR_predict(tmp_location).title()
    predicted_make = VMR_predict(tmp_location).title()

    # get the text and location of the number plate
    plate_data = get_plate(tmp_location)
    print(plate_data)

    # delete the temporary image as it is no longer needed
    os.remove(tmp_location)

    # add the predicted color and predicted make to the 'res' dictionary
    res = {'predicted_color': predicted_color, 'predicted_make': predicted_make}

    # this block uses the res array and ves.py
    # as long as we do not directly write to variables in main.py, this block of code can be put into
    # a function in plate_processor.py

    plate_data, ves_data, plate_status = process_plate(res, plate_data)

    # Uppdate the res array with the read in plate, ves details of the predicted plate and status of the msg
    res.update(plate_data)
    res.update(ves_data)
    res.update({'plate_status': plate_status})

    # return res - the dictionary containing all the information about the image
    return res


def check_file_path(file_path):
    """
    Function to check the file path provided by the user
    :param file_path: string representation of the absolute file path to the image
    :return: Boolean, True for a valid file path, False for an invalid file path
    """
    # declare an array of supported file types
    filetypes = ['jpg', 'jpeg', 'png']
    # split the filename into the file path
    if file_path.split('.')[-1] in filetypes:
        # return True if the file type is supported
        return True
    else:
        # return False if the file type is not supported
        return False


def input_window():
    """
    Tkinter GUI Function
    """
    # Define a font style
    my_font = ('Comic Sans MS', 12)
    bg_color = '#79A7D3'
    bg_dark = '#6883BC'

    # Configure and Set-Up up the general window
    master = tk.Tk()
    master.title("Nishil's Machine Learning ANPR Camera")
    master.configure(bg=bg_color)
    master.geometry("675x250+200+200")

    def get_inputs():
        """
        Function to take in the inputs from the GUI, pass them to the relevant functions, and display the output
        :return: None, however this refreshes the window with the relevant information and images displayed
        """
        # Get the image path from the image_path_input entry field
        image_path = str(image_path_input.get())

        # ensure that the image path is valid
        if check_file_path(image_path):

            # Process the Image using the process_input function
            prediction = process_input(image_path)

            # Resize the window as it will now display more information
            master.geometry("675x550+200+200")

            if prediction['reg_found']:
                # if a registration is found, place the color, make and observed registration number into the window
                observation_label.config(text='Color: ' + prediction['predicted_color'] + ', Make: ' + prediction['predicted_make'] + ', Reg No: ' + prediction['reg_text'])

                # Place the cropped number plate into the window
                img = prediction['reg_image']
                img.thumbnail((100, 550))
                img = ImageTk.PhotoImage(img)
                reg_image.config(image=img)
            else:
                # no registration number was found, plate the color and make into the window
                observation_label.config(text='Color: ' + prediction['predicted_color'] + ', Make: ' + prediction['predicted_make'] + ', Reg No: Not Found')
                reg_image.config(image="")

            if prediction['ves_found']:
                # if data from VES is found, place the color, make, MOT and tax status from VES into the window
                ves_label.config(text='Color: ' + prediction['ves_color'] + ', Make: ' + prediction['ves_make'] + ', MOT: ' + prediction['ves_mot'] + ', Tax: ' + prediction['ves_tax'])
            else:
                # no data was found on VES, place a mesage in the window to highlight this
                ves_label.config(text='Not Found')

            # plate a message regarding the status of the plate
            plate_label.config(text=prediction['plate_status'])

            # Place full image provided by the used into the window
            tmp_img = Image.open(image_path)
            tmp_img.thumbnail((250, 250))
            tmp_img = ImageTk.PhotoImage(tmp_img)
            full_image.config(image=tmp_img)

            # Refresh the window
            master.mainloop()
        else:
            # if the image path is not valid, pop up a warning box
            tk.messagebox.showwarning(title='WARNING',
                                      message="Incorrect file type.\nPlease select a '.jpg', '.jpeg' or '.png'.")

    def file_selector():
        """
        Function to open the file dialog provided by the OS
        :return: None, the selected file is placed into the input field if it is valid
        """
        # use the tkinter filedialog to open file explorer and let the user choose a file
        chosen_path = str(filedialog.askopenfilename())
        if check_file_path(chosen_path):
            # if the image path is valid, then delete the existing input path and then insert the new path
            image_path_input.delete(0, len(str(image_path_input.get())))
            image_path_input.insert(0, chosen_path)
        else:
            # if the image path is nt valid, pop up a warning box
            tk.messagebox.showwarning(title='WARNING',
                                      message="Incorrect file type.\nPlease select a '.jpg', '.jpeg' or '.png'.")

    # Specify Window Title
    tk.Label(master, text="Nishil's Machine Learning ANPR Camera", font=my_font, bg=bg_color).grid(row=0, columnspan=4, sticky=tk.W+tk.E)

    # Image Selection Output
    tk.Label(master, text="Image Path", font=my_font, bg=bg_color).grid(row=1)
    image_path_input = tk.Entry(master, font=my_font, bg=bg_dark, width=45)
    image_path_input.insert(0, "Please Select Image ---------> ---------> ---------> --------->")
    image_path_input.grid(row=1, column=1, sticky="ew")

    # Image Select Button
    image_select_btn = tk.Button(master, text="Select File", command=file_selector, font=('Comic Sans MS', 10), bg=bg_dark)
    image_select_btn.grid(row=1, column=2, sticky="ew")

    # Quit Button
    quit_btn = tk.Button(master, text="Quit", command=quit, font=('Comic Sans MS', 10), bg='#FF6961')
    quit_btn.grid(row=3, column=0, pady=2, sticky="ew")

    # Enter Button
    enter_btn = tk.Button(master, text="Start", command=get_inputs, font=('Comic Sans MS', 10), bg='#77DD77')
    enter_btn.grid(row=3, column=1, pady=2, sticky="ew", columnspan=2)

    # Observation Label
    tk.Label(master, text="Observed Data", font=my_font, bg=bg_color).grid(row=4, column=0)
    observation_label = tk.Label(master, text='', font=my_font, bg=bg_color)
    observation_label.grid(row=4, column=1, columnspan=3)

    # Plate Prediction Label
    tk.Label(master, text="Plate Prediction(s)", font=my_font, bg=bg_color).grid(row=5, column=0)
    plate_label = tk.Label(master, text='', font=my_font, bg=bg_color)
    plate_label.grid(row=5, column=1, columnspan=3)

    # VES Label
    tk.Label(master, text="VES Data", font=my_font, bg=bg_color).grid(row=6, column=0)
    ves_label = tk.Label(master, text='', font=my_font, bg=bg_color)
    ves_label.grid(row=6, column=1, columnspan=3)

    # Cropped Number Plate Output Block
    reg_image = tk.Label(master, bg=bg_color)
    reg_image.grid(row=7, column=0, columnspan=3)

    # Full Image Output Block
    full_image = tk.Label(master, bg=bg_color)
    full_image.grid(row=8, column=0, columnspan=3)

    # Repurposing the Escape and Enter key
    def close_win():
        master.destroy()
    master.bind('<Escape>', lambda event: close_win())
    master.bind('<Return>', lambda event: get_inputs())

    # Starting the Window
    master.mainloop()


if __name__ == '__main__':

    print("Program Started - ML ANPR CAMERA GUI")

    global vcor_IMAGE_SIZE, vmr_IMAGE_SIZE
    vcor_IMAGE_SIZE = vmr_IMAGE_SIZE = 224

    global vcor_model, vcor_class_names
    vcor_model, vcor_class_names = deserialize_VCOR()

    global vmr_model, vmr_class_names
    vmr_model, vmr_class_names = deserialize_VMR()

    input_window()
