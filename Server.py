import time
from datetime import datetime
import os
import socket
import threading
import tkinter
from tkinter import *

# global is_open
# is_open = False
import tqdm

Client_BUFFER_SIZE = 65527
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096  # send 4096 bytes each time step

# nicknames_list = []
# clients_list = []
# files_list = ["files/air.jpeg", "files/cii.txt", "files/DO.txt", "files/try.txt"]
# files_names = ["air", "Cii", "names", "try"]
# data_names = "files: " + ",".join(files_names)
# continue_download=True

host = '127.0.0.1'
port_tcp = 55000
port_udp = 44000

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4 -TCP
# server.bind((host, port_tcp))
#
# server_2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPV4 -UDP
# server_2.bind((host, port_udp))

class Server:


    def __init__(self) :
        """
        this method is the constructor of the server chat
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4 -TCP
        self.server.bind((host, port_tcp))

        self.server_2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPV4 -UDP
        self.server_2.bind((host, port_udp))
        self.nicknames_list = []
        self.clients_list = []
        self.files_list = ["files/air.jpeg", "files/cii.txt", "files/DO.txt", "files/try.txt"]
        self.files_names = ["air", "Cii", "names", "try"]
        self.data_names = "files: " + ",".join(self.files_names)
        self.continue_download=True

        server_thread = threading.Thread(target=self.startChat())
        server_thread.start()


    def startChat(self):
        """
        this method allows the clients to connect the chat
        and append them to the clients list
        """
        print("server is working on " + host)
        self.server.listen()

        while True:
            client, address = self.server.accept()
            print("Connected with {}".format(str(address)))
            client.send('NICKNAME'.encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            self.nicknames_list.append(nickname)
            self.clients_list.append(client)
            print("Nickname is {}".format(nickname))
            client.send("Connected to server!\n".encode("utf-8"))
            self.send_msg("{} joined!\n".format(nickname).encode("utf-8"))
            self.send_msg_to_someone("Connected to server!\n".encode("utf-8"), nickname)

            thread = threading.Thread(target=self.send, args=(client,))
            thread.start()


    def send_msg(self,message):
        """
        :param: message
        this method broadcast the message of each client to the chat
        """
        for client in self.clients_list:
            client.send(message)


    def send_msg_to_someone(self,message, someone):
        """
        :param: message
        this method broadcast the message of a specific client to other client
        """
        nickname_index = self.nicknames_list.index(someone)
        client_to_send = self.clients_list[nickname_index]
        client_to_send.send(message)


    def send(self,client):
        """
        :param client:
        this method handle the incoming messages
        """
        while True:
            try:
                # data = "accounts|" + "|".join(nicknames_list)
                # send_msg(data.encode("utf-8"))
                message = client.recv(1024).decode("utf-8")
                msg_arr = message.split(" ")
                if msg_arr[1] == "to":
                    someone = msg_arr[2]
                    if someone in self.nicknames_list:
                        self.send_msg_to_someone(message.encode("utf-8"), someone)
                    else:
                        self.send_msg(message.encode("utf-8"))
                elif msg_arr[1] == "nicknames\n":
                    data_nicknames = "nicknames: " + ",".join(self.nicknames_list)
                    self.send_msg_to_someone((data_nicknames + "\n").encode("utf-8"), msg_arr[0][:-1])
                elif msg_arr[1] == "files\n":
                    self.send_msg_to_someone((self.data_names + "\n").encode("utf-8"), msg_arr[0][:-1])
                elif msg_arr[1] == "download":
                    if msg_arr[2][:-1] in self.files_names:
                        file_index = self.files_names.index(msg_arr[2][:-1])
                        path_to_send = self.files_list[file_index]
                        self.send_msg_to_someone("con_udp".encode("utf-8"), msg_arr[0][:-1])
                        thread_udp = threading.Thread(target=self.download_file, args=(path_to_send, msg_arr))
                        thread_udp.start()
                    else:
                        self.send_msg_to_someone("file not found!\n".encode("utf-8"), msg_arr[0][:-1])
                elif msg_arr[1] == "Downloading:":
                    print(msg_arr)
                    self.send_msg_to_someone(msg_arr, msg_arr[0][:-1])
                elif msg_arr[1]== "STOP\n":
                    print("Stop!!!!!!!!!!!!!!!!!!")
                    self.continue_download = False
                else:
                    self.send_msg(message.encode("utf-8"))
            except:
                client_index = self.clients_list.index(client)
                self.clients_list.remove(client)
                client.close()
                nickname = self.nicknames_list[client_index]
                self.send_msg('{} left!\n'.format(nickname).encode("utf-8"))
                self.nicknames_list.remove(nickname)
                break


    def download_file(self,path, msg_arr):
        """
        this method sends the file to the client
        using the udp socket with realible principles (FAST reliable UDP) using congestion control
        """
        # global continue_download
        # continue_download == True
        self.continue_download = True
        mid=1
        filesize=0
        cwnd = 1
        file_queue = []
        file_dict = {}
        sent_list = []
        j = 0
        # start_flag = False
        flag = True
        last_index_got = 0
        # start_time=datetime.now()
        while flag:
            # if datetime.now()-start_time >
            msg = "null"
            while (msg == "null"):
                msg, client_addr = self.server_2.recvfrom(1024)
                if msg.decode("utf-8") == "ack":
                    print(msg)
                    # start_for_rtt=time.time()
                    self.server_2.sendto(msg, client_addr)
                elif msg.decode("utf-8") == "ACK":
                    # end_for_rtt=time.time()-start_for_rtt #sec
                    # print(end_for_rtt)
                    print(msg)
                    filesize = os.path.getsize(path)
                    progress = tqdm.tqdm(range(filesize), f"Sending {path}", unit="B", unit_scale=True, unit_divisor=1024)
                    with open(path, "rb") as f:
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            file_queue.append(bytes_read)
                            file_dict[j] = False
                            j += 1
                            # update the progress bar
                            progress.update(len(bytes_read))
                    print(len(file_queue), "loops")
                    self.server_2.sendto(f"{path}{SEPARATOR}{filesize}{SEPARATOR}{len(file_queue)}".encode(), client_addr)
                elif msg.decode("utf-8") == "START":
                    print(msg)
                    self.server_2.sendto(file_queue[0], client_addr)
                    sent_list = [0]
                    last_index = 0
                    timer_flag = True
                    timeout = 0.05
                    timeout_start = time.time()
                    # while self.continue_download:
                    #     if len(file_queue) / 2 < mid:
                    #         self.send_msg_to_someone(
                    #             "would you like to proceed download the file?\nif not: write STOP in the chat\nelse the download continue within 15 seconds\n".encode(
                    #                 "utf-8"), msg_arr[0][:-1])
                    #         time.sleep(15)
                    #         if not self.continue_download:
                    #             self.send_msg_to_someone(("You got 50%|████████████████████████████████████████████| from file: " + str(msg_arr[2][:-1]) + " ,last byte: " + str(filesize/2) + "\n").encode("utf-8"), msg_arr[0][:-1])
                    #             return
                    while timer_flag:
                        while time.time() < timeout_start + timeout:
                            msg, client_addr = self.server_2.recvfrom(1024)
                            print(msg, "timeout_msg")
                            break
                        if len(file_queue) / 2 < mid:
                            self.send_msg_to_someone((
                                                                 "You got 50%|███████████████████████                     | from file: " + str(
                                                             msg_arr[2][:-1]) + "\n ,last byte: " + str(
                                                             filesize / 2) + "\n").encode("utf-8"), msg_arr[0][:-1])
                            self.send_msg_to_someone(
                                "would you like to proceed download the file?\nif not: write STOP in the chat\nelse the download continue within 15 seconds\n".encode(
                                    "utf-8"), msg_arr[0][:-1])
                            time.sleep(15)
                            if not self.continue_download:
                                return
                        if msg.decode("utf-8").startswith("GOT"):
                            print(msg)
                            got_index = msg.decode("utf-8")[3]
                            if got_index != last_index_got:
                                last_index_got = got_index
                                for i in sent_list:
                                    file_dict[i] = True
                                    mid+=1
                                cwnd = cwnd * 2
                                # timeout -= 0.01
                                if False in file_dict.values():
                                    to_sent = b''.join(
                                        file_queue[last_index + 1:min(last_index + cwnd + 1, len(file_queue))])
                                    print(to_sent.__sizeof__())
                                    if to_sent.__sizeof__() <= Client_BUFFER_SIZE:
                                        self.server_2.sendto(to_sent, client_addr)
                                        sent_list = []
                                        print(last_index + 1)
                                        print(min(last_index + cwnd + 1, len(file_queue)))
                                        for seq in range(last_index + 1, min(last_index + cwnd + 1, len(file_queue))):
                                            print(seq)
                                            sent_list.append(seq)
                                        last_index = min(last_index + cwnd, len(file_queue) - 1)
                                    else:
                                        cwnd = int(cwnd / 2)
                                        if cwnd < 1:
                                            cwnd = 1
                                        to_sent = b''.join(
                                            file_queue[last_index + 1:min(last_index + cwnd + 1, len(file_queue))])
                                        self.server_2.sendto(to_sent, client_addr)
                                        sent_list = []
                                        print(last_index + 1)
                                        print(min(last_index + cwnd + 1, len(file_queue)))
                                        for seq in range(last_index + 1, min(last_index + cwnd + 1, len(file_queue))):
                                            print(seq)
                                            sent_list.append(seq)
                                        last_index = min(last_index + cwnd, len(file_queue) - 1)
                                else:
                                    self.server_2.sendto("end".encode("utf-8"), client_addr)
                                    flag = False
                                    timer_flag = False
                                    continue_download=False
                                    self.send_msg_to_someone((
                                                                    "You got 100%|████████████████████████████████████████████| from file: " + str(
                                                                msg_arr[2][:-1]) +" ,last byte: "+str(filesize)+ "\n").encode("utf-8"), msg_arr[0][:-1])
                            else:
                                cwnd = int(cwnd / 2)
                                if cwnd < 1:
                                    cwnd = 1
                                # timeout += 0.01
                                if False in file_dict.values():
                                    to_sent = b''.join(
                                        file_queue[last_index + 1:min(last_index + cwnd + 1, len(file_queue))])
                                    self.server_2.sendto(to_sent, client_addr)
                                    sent_list = []
                                    print(last_index + 1)
                                    print(min(last_index + cwnd + 1, len(file_queue)))
                                    for seq in range(last_index + 1, min(last_index + cwnd + 1, len(file_queue))):
                                        print(seq)
                                        sent_list.append(seq)
                                    last_index = min(last_index + cwnd, len(file_queue) - 1)
                                else:
                                    self.server_2.sendto("end".encode("utf-8"), client_addr)
                                    flag = False
                                    timer_flag = False
                                    self.continue_download = False
                                    self.send_msg_to_someone((
                                                                    "You got 100%|████████████████████████████████████████████| from file:" + str(
                                                                msg_arr[2][:-1]) +", last byte: "+str(filesize)+ "\n").encode("utf-8"), msg_arr[0][:-1])


server= Server()
