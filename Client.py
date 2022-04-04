import socket
from telnetlib import IP
import threading
import sys

# Client side of the system

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
QUIT_FUNCTION = "0x0"
SEND_FUNCTION = "0x1"
CLIENTLIST_FUNCTION = "0x2"

connected = True
client = ''

def send(msg):

    message = msg.encode(FORMAT)

    #create a header from the message length
    msg_length = len(message)                           
    send_length = str(msg_length).encode(FORMAT)        
    send_length += b' ' * (HEADER - len(send_length))   

    #send header and the message
    client.send(send_length)                            
    client.send(message)                                
    
#listens for any messages from the server
def server_listener():
    global connected
    while connected:
        try:
            msg = client.recv(2048).decode(FORMAT)
            if msg:
                print(msg)
        except Exception:
            #catch disconnect event
            connected = False
            print("Disconnected")
            break
         
        

def input_listener():
    global connected
    
    while connected:

        message = input()           #wait for keyboard input
        args = message.split()      #split message into arguments
        #handle input and send message to server
        if args:
            if args[0] == "quit":
                send(QUIT_FUNCTION)
            elif args[0] == "send":
                message = ''
                for x in args[2:]:
                    message += str(x) + ' '
                send(SEND_FUNCTION + ' ' + args[1] + ' ' + message)
            elif args[0] == "clientlist":
                send(CLIENTLIST_FUNCTION)
            elif args[0] == "help":
                print("commands:\n\nclientlist\n	-prints out all clients in the network\n\nsend {reciever ID} {message}\n	- sends the message to a specified client\n	- reciever ID = all sends the message to all clients\n\nquit\n	- disconnects the client\n")
            else:
                send(message)


    

def start():
    #start listening and input threads
    listen_thread = threading.Thread(target=server_listener)
    listen_thread.start()
    input_thread = threading.Thread(target=input_listener)
    input_thread.start()

while True:
    print("Server IP: ")
    server = input()
    try:
        addr = (server, PORT)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(addr)
        connected = True
        break
    except Exception:
        print("Can't connect :(, Try again\n")
        continue
    
print("Client Started")
start()
    