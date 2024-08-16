import PySimpleGUI as sg
import pandas as pd
import serial
import time
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot
from datetime import datetime

def printf(*arg, **kwarg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(timestamp, *arg, **kwarg)

matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# initialize serial port
ser = serial.Serial('COM4', 9600, timeout=0.1)

def setSpeed(speed):
    # the value of speed can be either in deg/sec or rpm. shouldn't matter tbh.
    speed = float(120.00)
    # printf(f'set speed to {speed} deg/sec')
    data = f"e{speed}\n"
    print("Setting speed to: " + data)
    ser.write(data.encode('ascii'))

# Define the layout of the GUI
layout = [
    [sg.Text("Drag and drop a CSV file here:")],
    [sg.Input(key="-FILE-", enable_events=True, visible=False), sg.FileBrowse()],
    [sg.Button("Start"), sg.Button("Stop")],
    [sg.Text("Enter a Value (Deg/Sec):"), sg.Input(key="-NUMBER-"), sg.Button("Send")],
    [sg.Button("Reset Rotational Travel Position"), sg.Button("Set Travel Unit to Degrees")],
    [sg.Button("Max the CW/CCW Travel Limit")],
    [sg.Canvas(key="-CANVAS-")],
    [sg.Button("Close")]
]

# Create the window
window = sg.Window(
    "GUI",
    layout,
    #location=(0,0),
    finalize=True)

# maximize window size

window.Maximize()
# Event loop
while True:
    event, values = window.read()

    # Exit the program if the window is closed or "Close" button is clicked
    if event == sg.WINDOW_CLOSED or event == "Close":
        ser.close()
        break

    # Handle file drop event
    if event == "-FILE-":
        file_path = values["-FILE-"]
        # Parse the file into a pandas dataframe
        df = pd.read_csv(file_path)

        first_column = df.iloc[1:,3]

        print(df.head())

        # set initial speed to zero
        speed = "e000.00\n"
        print("Setting Initial Speed to: " + speed)
        ser.write(speed.encode('ascii'))

        # start motor

        print('Starting Clockwise Movement')
        data = "u\n"
        ser.write(data.encode('ascii'))

        # initialize dataframe
        # dict = {'Torque' : [], 'Rotations' : []}
        # torqueRotCSV = pd.DataFrame(data = dict)

        # temp initialize of stop counter
        abcd = 0

        # initialize empty list to store incoming torque and rotation values
        updatingTorque = []
        updatingRotation = []

        # update motor speed
        for entry in first_column:

            # early stop counter
            # abcd += 1
            # if abcd == 100:
            #     break

            # send the speed value to the controller
            speed = f"e{entry}0\n"
            printf("Setting speed to: " + speed)
            ser.write(speed.encode('ascii'))

            # request the torque value
            requestTorque = "n\n"
            ser.write(requestTorque.encode('ascii'))

            # parse the torque value and save to a CSV
            incomingTorque = ser.readline().decode('ascii')
            # print("Torque: " + incomingTorque)
            updatingTorque.append(incomingTorque)

            incomingRot = ser.readline().decode('ascii')
            # print("Rotations: " + incomingRot)
            updatingRotation.append(incomingRot)

            # sleep for the remainder of the time, since data is collected in 0.1s intervals
            time.sleep(0.035)

        if len(updatingTorque) == len(updatingRotation):
            torqueRotDF = pd.DataFrame({'Torque': updatingTorque, 'Rotations': updatingRotation})
            print(torqueRotDF.head())
            print("Saving CSV")
            torqueRotDF.to_csv('torqueRotCSV.csv')

            # draw the collected torque values
            fig = matplotlib.pyplot.figure(figsize=(5, 4), dpi=100)
            t = df.iloc[1:, 0]
            fig.add_subplot(111).plot(torqueRotDF.iloc[:, 0])
            draw_figure(window["-CANVAS-"].TKCanvas, fig)

        # stop the motor
        print('Stopping Motor')
        data = "s\n"
        ser.write(data.encode('ascii'))

    # Handle start button click
    if event == "Start":
        print("Start Clicked")
        # Start the process here
        print('start move cw')
        data = "u\n"
        ser.write(data.encode('ascii'))

    # Handle stop button click
    if event == "Stop":
        print('Stopping Motor')
        data = "s\n"
        ser.write(data.encode('ascii'))

    # Handle number input
    if event == "-NUMBER-":
        number = values["-NUMBER-"]
        print(f"number: {number}")
        # Process the entered number here

    if event == "Send":
        number = values["-NUMBER-"]
        print(f"setting speed to: {number}")
        data = f"e{number}\n"
        print(data)
        ser.write(data.encode('ascii'))
        # Stop the process here

    if event == "Reset Rotational Travel Position":
        print('resetting rotational travel position to zero')
        data = "z\n"
        ser.write(data.encode('ascii'))

    if event == "Set Travel Unit to Degrees":
        print('setting travel unit to degrees')
        data = "i\n"
        ser.write(data.encode('ascii'))

    if event == "Max the CW/CCW Travel Limit":
        print('Setting CW/CCW Travel Limit to 9999.99')
        data = "l"
        ser.write(data.encode('ascii'))
        data = "h999999.99"
        ser.write(data.encode('ascii'))
        data = "g-999999.99"
        ser.write(data.encode('ascii'))

        data = "v"
        ser.write(data.encode('ascii'))

        data = ser.readline().decode('ascii')
        print(data)

# Close the window
window.close()
