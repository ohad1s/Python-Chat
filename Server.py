import socket
import threading

host = '127.0.0.1'
port = 55000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # IPV4 -TCP
server.bind((host, port))
clients = []
nicknames = []

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
        nicknames.append(nickname)
        clients.append(client)
        print("Nickname is {}".format(nickname))
        send_msg("{} joined!\n".format(nickname).encode("utf-8"))
        client.send('Connected to server!\n'.encode("utf-8"))
        thread = threading.Thread(target=send, args=(client,))
        thread.start()

def send_msg(message):
    """
    :param: message
    this method broadcast the message of each client to the chat
    """
    for client in clients:
        client.send(message)
        server.sendto()

def send(client):
    """
    :param client:
    this method handle the incoming messages
    """
    while True:
        try:
            message = client.recv(1024)
            send_msg(message)
        except:
            client_index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[client_index]
            send_msg('{} left!\n'.format(nickname).encode("utf-8"))
            nicknames.remove(nickname)
            break

startChat()