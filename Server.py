import socket 
import threading
import hashlib
import random
from typing import NamedTuple

HEADER = 64                            #header in front of every message containing the message length
PORT = 5050                        
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
QUIT_FUNCTION = "0x0"
SEND_FUNCTION = "0x1"
CLIENTLIST_FUNCTION = "0x2"


#bind server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clientlist = []     #stores all client objects in the network
socketlist = []     #stores all client sockets (same index as in clientlist)

#container to link address and id of clients 
class client(NamedTuple):
    address: int
    id: str

#handles every new client in the network
def handle_client(conn, addr, id):
    print(str(addr) + " connected")
    conn.send("Connected to server. Type \"help\" to see the command list".encode(FORMAT))

    connected = True
    while connected:
        try:
            #recieve header of the message
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except ConnectionResetError:
            #handle client disconnecting from the server 
            print(str(addr) + " Disconnected")

            #remove disconnected client from the list
            delete_client(id)

            break

        #based on recieved header, decode and handle the rest of the message
        if msg_length:

            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            #split message for arguments
            args = msg.split();

            if args:
                #quit
                if args[0] == QUIT_FUNCTION:
                    conn.send("Disconnecting".encode(FORMAT))
                    #remove disconnected client from the list
                    delete_client(id)
                    print(str(addr) + " Disconnected")
                    connected = False
                #send
                elif args[0] == SEND_FUNCTION:
                    if args[1] == "all":
                        message = get_message(args[2:])
                        send_all(str(id) + " : " + message)
                    else:
                        message = get_message(args[2:])
                        send_message(conn, addr, args[1], message)
                    conn.send("message sent".encode(FORMAT))
                #clientlist
                elif args[0] == CLIENTLIST_FUNCTION:
                    list = print_clients()
                    conn.send(list.encode(FORMAT))
                #bad input handler
                else:
                    conn.send("wrong command".encode(FORMAT))

            print(str(addr) + " : " + str(msg))

            
    #end the connection if the loop is broken
    conn.close()

#stiches the rest of the message together into a single string
def get_message(args):
    result = ''
    for x in args:
        result += str(x) + ' '
    return result 

#start function for the server
def start():
    server.listen()
    print("Server started")
    print("Server is listening on " + str(SERVER) + " - add clients using this ip")

    while True:
        conn, addr = server.accept()
        newid = generate_id(addr)   #generate new ID for the client
        #add clients to server lists
        clientlist.append(client(id= newid, address = addr))
        socketlist.append(conn)
        #create new client handler
        thread = threading.Thread(target=handle_client, args=(conn, addr, newid))
        thread.start()
        print("connected clients: " + str(threading.active_count() - 1))

#generates a unique hash for every new client
def generate_id(addr):
    
    _value = str(addr) + str(random.randint(1, 99999999))
    result = hashlib.sha256(_value.encode(FORMAT))
    return  result.hexdigest()

#prints list of clients
def print_clients():
    list = '\nConnected clients:\n'
    for x in clientlist:
        list = list  + str(x.id) + "\n"
    return str(list)

def send_all(message):
    for x in socketlist:
        if x:
            x.send(message.encode(FORMAT))

def send_message(conn, addr, recieverID, message):
    reciever = ''

    #find client to send to in the list
    for x in clientlist:
        if x.id == recieverID:
            peer_index = clientlist.index(x)
            reciever = socketlist[peer_index]
        if x.address == addr:
            senderID = x.id
    
    #if found send message
    if reciever:
        reciever.send(('\n' + senderID + " : " + message).encode(FORMAT))
    else:
        conn.send("There is no user of that ID".encode(FORMAT))

def delete_client(id):
    #search and delete the client from list
            i = 0   #index of the client in question
            for x in clientlist:
                if x.id == id:
                    #remove from lists
                    clientlist.pop(i)
                    socketlist.pop(i)
                    #notify all peers about disconnect
                    send_all(str(x.id) + " Disconnected")
                i+=1

start()