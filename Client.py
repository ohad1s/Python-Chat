import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog



class Client:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 55000))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("NickName", "please enter your nickname", parent=msg)

        self.gui_play = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.title("Ciiii Chat")
        self.win.configure(bg="lightgray")

        self.chat_lable = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_lable.config(font=('Helvetica', 12))
        self.chat_lable.pack(padx=20, pady=5)

        self.txt_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.txt_area.pack(padx=20, pady=5)
        self.txt_area.config(state="disabled")

        self.msg_lable = tkinter.Label(self.win, text="Message", bg="lightgray")
        self.msg_lable.config(font=('Helvetica', 12))
        self.msg_lable.pack(padx=20, pady=5)

        self.msg_box = tkinter.Text(self.win, height=8)
        self.msg_box.pack(padx=20, pady=5)

        self.send_but = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_but.config(font=('Helvetica', 12))
        self.send_but.pack(padx=20, pady=5)

        self.gui_play = True
        self.win.protocol("WM_DELETE_WINDOW",self.stop)
        self.win.mainloop()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)


    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICKNAME':
                    self.sock.send(self.nickname.encode('utf-8'))
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
        message = f"{self.nickname}: {self.msg_box.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.msg_box.delete('1.0','end')

client=Client()
