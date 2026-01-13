# PSCAD-GFM
PSCAD studies into behaviour of grid-forming inverters for power system stability.

This PSCAD model was based on a model I received was from Farid at PSCAD, after inquiring about GFM-VSM models. The model was then modified to add functionality such as RoCoF frequency ramps and automation capabilities. To speed up simulations multiprocessing is used to run multiple instances of PSCAD, where each instance can be adjusted in the main.py file. All the data is collected and can be plotted against eachother in the python notebook. This can be adapted to change variables. Matplotlib is currently used for plotting, but the CSV files are saved so any other software or library can be used instead.

## Requirements
* Python 3.10 or above

## TO USE
* In the main.py file create a new test case by creating a new Sim object with the desired name of the test case as a variable. Parameters of these test cases can then be adjusted for the desired test, finally append this test case to the SIMULATIONS array.
* Once the simulation ends (the terminal will notify you, it may take a while for the csv to load depending on the sample time step) run the plotting.ipynb file to visualise results.
* pscad_utils.py should not be touched unless you are adding additional functionality that is not yet available.
<img width="1684" height="910" alt="{8BDD64A0-6768-49DC-BA56-F7D70D4D8DBE}" src="https://github.com/user-attachments/assets/33983e39-b380-41f8-9285-8839f1ccc1b4" />
<img width="2560" height="1327" alt="Figure_1" src="https://github.com/user-attachments/assets/767297af-750b-40df-beaa-c1d6f915cf25" />
