import os
import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import *
from tkinter.filedialog import askopenfilename
import tqdm

host = '127.0.0.1'
port_tcp = 55000
port_udp = 44000

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


class Client:


    def __init__(self):
        """
        this method is the constructor of the client chat
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port_tcp))

        msg = tkinter.Tk()
        msg.withdraw()


        self.nickname = simpledialog.askstring("NickName", "please enter your nickname", parent=msg)
        self.gui_play = False
        self.running = True
        self.users=[]


        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        receive_thread.start()


    def gui_loop(self):
        """
        this method is the gui loop for the chat
        """
        self.win = tkinter.Tk()
        self.win.title("Ciiii Chat")
        self.win.configure(bg="lightgray")

        self.Frame3txt = Frame(master=self.win)
        self.Frame3txt.grid(row = 0, column = 1, rowspan = 5, columnspan = 3, \
                            sticky = W+E+N+S)
        self.Frame4msg = Frame(master=self.win)
        self.Frame4msg.grid(row = 5, column = 1, rowspan = 1, columnspan = 3, \
                            sticky = W+E+N+S)

        self.chat_lable = tkinter.Label(self.Frame3txt, text="Chat:", bg="lightgray")
        self.chat_lable.config(font=('Ariel', 12))
        self.chat_lable.pack(padx=20, pady=5)

        self.txt_area = tkinter.scrolledtext.ScrolledText(self.Frame3txt)
        self.txt_area.pack(padx=20, pady=5)
        self.txt_area.config(state="disabled")

        self.msg_lable = tkinter.Label(self.Frame4msg, text="Message", bg="lightgray")
        self.msg_lable.config(font=('Ariel', 12))
        self.msg_lable.pack(padx=20, pady=5)

        self.msg_box = tkinter.Text(self.Frame4msg, height=8)
        self.msg_box.pack(padx=20, pady=5)

        self.send_but = tkinter.Button(self.Frame4msg, text="Send", command=self.write)
        self.send_but.config(font=('Ariel', 12))
        self.send_but.pack(padx=20, pady=5)

        # self.nicknamesFrame1 = Frame(master=self.win)
        # self.nicknamesFrame1.grid(row = 0, column = 0, rowspan = 3, columnspan = 1, sticky = W+E+N+S)
        # self.user_list=Listbox(master=self.nicknamesFrame1)
        # self.user_list.pack(side="left",expand=1,fill="both")
        # self.userlist_scrollbar = Scrollbar(self.nicknamesFrame1,orient="vertical")
        # self.userlist_scrollbar.config(command=self.user_list.yview)
        # self.userlist_scrollbar.pack(side="left",fill="both")
        # self.user_list.config(yscrollcommand=self.userlist_scrollbar.set)

        # for nick in self.users:
        #     self.user_list.insert(END,nick)

        self.gui_play = True
        self.win.protocol("WM_DELETE_WINDOW",self.stop)
        self.win.mainloop()

    def stop(self):
        """
        this method close the chat for a client
        and also close the socket of the client
        """
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)


    def receive(self):
        """
        this method handle the incoming messages in the client gui
        """
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICKNAME':
                    self.sock.send(self.nickname.encode('utf-8'))
                # elif message.startswith("accounts"):
                #     self.users = message.split("|")
                #     self.users.remove("accounts")
                elif message == 'con_udp':
                    print(message)
                    self.open_udp_sock()
                    thread_dowmload = threading.Thread(target=self.download_file)
                    thread_dowmload.start()
                else:
                    if (self.gui_play):
                        self.txt_area.config(state='normal')
                        self.txt_area.insert('end', message)
                        self.txt_area.yview('end')
                        self.txt_area.config(state='disabled')
            except:
                print("An error occured!")
                self.sock.close()
                break

    def write(self):
        """
        this method handle the outgoing messages in the client gui
        """
        message = f"{self.nickname}: {self.msg_box.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.msg_box.delete('1.0','end')

    def open_udp_sock(self):
        """
        this method open a udp socket for the client in order to download a file
        """
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def download_file(self):
        """
        this method downloading a file got from the server
        """
        self.udp_sock.sendto("ack".encode("utf-8"), (host, port_udp))
        msg_ack, serv_addr = self.udp_sock.recvfrom(1024)
        print(msg_ack)
        if msg_ack.decode("utf-8") == "ack":
            print(msg_ack)
            self.udp_sock.sendto("ACK".encode("utf-8"), (host, port_udp))
            received = self.udp_sock.recv(BUFFER_SIZE).decode()
            print(received)
            filename, filesize = received.split(SEPARATOR)
            filename = os.path.basename(filename)
            filesize = int(filesize)

            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True,
                                 unit_divisor=1024)
            with open(filename, "wb") as f:
                while True:
                    bytes_read = self.udp_sock.recv(BUFFER_SIZE)
                    try:
                        if bytes_read.decode("utf-8") == "end":
                            break
                        else:
                            self.udp_sock.sendto("Got".encode("utf-8"), serv_addr)
                    except:
                        self.udp_sock.sendto("Got".encode("utf-8"),serv_addr)
                    f.write(bytes_read)
                    progress.update(len(bytes_read))

            self.udp_sock.close()


client=Client()