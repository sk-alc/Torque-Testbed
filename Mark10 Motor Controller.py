import pyserial as serial

# Open the serial port
ser = serial.Serial('COM1', 9600)  # Replace 'COM1' with the appropriate port name

# Write a command to the serial port
command = b'Hello, World!'  # Convert the command to bytes
ser.write(command)

# Read the response from the serial port
response = ser.readline()
print(response)

# Close the serial port
ser.close()