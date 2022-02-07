import os
import socket
import threading
import tkinter
from tkinter import *
import tqdm


SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

nicknames_list=[]
clients_list=[]
files_list=["files/air.jpeg","files/cii.txt","files/DO.txt"]
files_names=["air","Cii","names"]
data_names="files: ," + ",".join(files_names)


host = '127.0.0.1'
port_tcp = 55000
port_udp = 44000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # IPV4 -TCP

server.bind((host, port_tcp))


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
            elif msg_arr[1]=="files\n":
                send_msg_to_someone(data_names+"\n".encode("utf-8"),msg_arr[0][:-1])
            elif msg_arr[1]=="download":
                if msg_arr[2] in data_names:
                    file_index= files_names.index(msg_arr[2])
                    path_to_send=files_list[file_index]
                    thread_udp = threading.Thread(target=open_udp_sock, args=path_to_send)
                    thread_udp.start()
                    send_msg_to_someone("con_udp".encode("utf-8"),msg_arr[0][:-1])
                else:
                    send_msg_to_someone("file not found!".encode("utf-8"),msg_arr[0][:-1])

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

def open_udp_sock(path):
    """

    """
    flag=True
    server_2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPV4 -UDP
    server_2.bind((host, port_udp))
    while flag:
        msg, client_addr= server_2.recvfrom(1024)
        if msg=="ack":
            server_2.sendto(msg,client_addr)
        if msg=="ACK":

            filesize = os.path.getsize(path)
            progress = tqdm.tqdm(range(filesize), f"Sending {path}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(path, "rb") as f:
                while True:
                    # read the bytes from the file
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in
                    # busy networks
                    server_2.sendall(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))
            # close the socket
            server_2.close()
            flag=False




startChat()