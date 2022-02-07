import socket
import threading
import tkinter
from tkinter import *

nicknames_list=[]
clients_list=[]

host = '127.0.0.1'
port = 55000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # IPV4 -TCP
server.bind((host, port))

def startChat():
    """
    this method allows the clients to connect the chat
    and append them to the clients list
    """
    print("server is working on " + host)
    server.listen()
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        client.send('NICKNAME'.encode("utf-8"))
        nickname = client.recv(1024).decode("utf-8")
        nicknames_list.append(nickname)
        clients_list.append(client)
        print("Nickname is {}".format(nickname))
        client.send("Connected to server!\n".encode("utf-8"))
        send_msg("{} joined!\n".format(nickname).encode("utf-8"))
        send_msg_to_someone("Connected to server!\n".encode("utf-8"),nickname)


        thread = threading.Thread(target=send, args=(client,))
        thread.start()


def send_msg(message):
    """
    :param: message
    this method broadcast the message of each client to the chat
    """
    for client in clients_list:
        client.send(message)

def send_msg_to_someone(message,someone):
    """
    :param: message
    this method broadcast the message of a specific client to other client
    """
    nickname_index=nicknames_list.index(someone)
    client_to_send=clients_list[nickname_index]
    client_to_send.send(message)

def send(client):
    """
    :param client:
    this method handle the incoming messages
    """
    while True:
        try:
            data = "accounts|" + "|".join(nicknames_list)
            send_msg(data.encode("utf-8"))
            message = client.recv(1024).decode("utf-8")
            msg_arr = message.split(" ")
            if msg_arr[1]=="to":
                someone=msg_arr[2]
                if someone in nicknames_list:
                    send_msg_to_someone(message.encode("utf-8"),someone)
                else:
                    send_msg(message.encode("utf-8"))
            else:
                send_msg(message.encode("utf-8"))
        except:
            client_index = clients_list.index(client)
            clients_list.remove(client)
            client.close()
            nickname = nicknames_list[client_index]
            send_msg('{} left!\n'.format(nickname).encode("utf-8"))
            nicknames_list.remove(nickname)
            break

startChat()