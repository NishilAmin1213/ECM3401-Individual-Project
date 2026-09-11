Please Note - The serialized models are no longer available at the link below 

#### Quick Start
This section contains commands to start the project, more description and information can be read below starting from the introduction section.
1) Open the terminal and navigate to the '' directory containing the python files, readme and requirements.txt
2) Ensure Python 3.9 is installed - 'python --version' (other versions of python may not guarantee functioning of the code)
   Python 3.12 is KNOWN not to work with this program, 32bit python versions are KNOWN not to work with this program.
3) Create a venv - 'python -m venv anpr-project-venv'
4) Activate the venv - Windows: 'anpr-project-venv\Scripts\activate'        Unix or MacOS: 'source anpr-project-venv/bin/activate'
5) Verify that pip is installed - 'python -m ensurepip --upgrade'
6) Install libraries - 'pip install -r ./requirements.txt'
7) Install fastanpr ignoring warnings from protobuf - 'pip install fastanpr'
8) Models are stored in in OneDrive - A link is also at the end of the Presentation Slides PDF
   https://universityofexeteruk-my.sharepoint.com/:f:/g/personal/na510_exeter_ac_uk/EmbuYXV4ZfRNi6j4tiKZe_kBQ88MG2Y0DXZJtO6Rc_7miA?e=sv1nmp
9) Place models in './models'
   you will need the files (VCOR.h5, VMR.h5, class_names_VCOR.txt, and , class_names_VMR.txt)
   and place them into the directory.
10) Run main.py - 'python.exe main.py'

##### Introduction
This README.txt contains information about getting started with my Machine Learning ANPR Camera Program.

##### Opening The Terminal
Open the Terminal and navigate to the folder containing the product code, readme and reqirements.txt
This folder will be called ''

##### Checking Python
The python environment can be different on different machines, all my python code has been run and tested in Python 3.9
It may not ben neccessary to update Python however if you experience issues running the code, please try using Python 3.9
Using the 'python --version' command, you can verify if python is installed and its version.

##### Creating The Python VENV
Create a python virtual environment to install libraries into, this can be deleted easily afterwards, the command for this is below:
'python -m venv anpr-project-venv'

##### Activate the VENV
Activate the virtual environment you just created, this will allow you to install libraries using pip and run the program
Windows      : 'anpr-project-venv\Scripts\activate'
Unix or MacOS: 'source anpr-project-venv/bin/activate'

##### Verify Pip
Verify that pip is installed and updated
'python -m ensurepip --upgrade'

##### Install Libraries
The majority of libraries and versions used in this project are stored in the 'requirements.txt' file, you will already be
in the directory containing the code and requirements.txt file so the libraries can all be installed using the following command:
'pip install -r ./requirements.txt'
The 'fastanpr' library will also need to be installed, this can be installed using the command:
'pip install fastanpr'
Please ignore any errors regarding the protobuf version

##### Running the program
The program can be run by running main.py by executing the command below:
'python.exe main.py'
This will open the GUI in a new window which may pop up open or appear on the taskbar

#### If you have any questions or problems, please get in touch at na510@exeter.ac.uk
