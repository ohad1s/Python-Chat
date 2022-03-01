# Python-Chat

## Written by Ohad Shirazi & Dvir Biton.


## About This Project:

In this project we implemented a Python Chat based on TCP connection. The Chat also include an option to download files from the Server, this option based on UDP connection with RDT (that we implemented).

## More about the chat:
The project work on your local host.
The project has 2 main classes:
Server and Client
The server running 2 sockets (TCP and UDP). He handles the messages of the chat, enables clients to see the connected nicknames,
enables clients to see the files of the server and also download files.
The messages of the chat going through the TCP connection.
File download works on the UDP connection, but with RDT:
It means using realible principles for congestion control (to prevent packet loss).

## File Download Algorithm:
The server has UDP connection
When a client wants to download a file from the server he have to ask for it (write in the chat: "download *file_name*" )
The server accepts the request and asks the server to open a UDP connection.
When the client is ready (opened the UDP connection) he start the "3 hand shake" procedure
Then the Server sends information about the file, and get a confirmation from the client to start sending.
The server sends the file "Go Back N" style.
It means he have a congestion window, if the pact was received successfully, the cwnd is doubled, if not the cwnd is divided by 2.
When a packet loss- we send all the cwnd again.
The server and the Client also have a timer, when they got timeout and they didn't receive the packet, they sending again.
After the server sent the last packet of the file and got an acknowledgement for it, he sends "end" message to the client
Then the client close the UDP socket

## State Diagram of the Algorithm:


![צילום מסך 2022-03-01 180840](https://user-images.githubusercontent.com/92723105/156204947-b921c043-e93d-4668-8193-f41a590bcb6c.png)



## How to run the project
Enter the project directory, open cmd (windows) or terminal (linux) through project's path and run the following commands:
python3 Server.py
Then for any client you want  to connect run the following commands:
python3 Client.py
For the project we used tkinter and tqdm (python libraries).
so first of all make sure you have them:

To install tkinter run the following command:
* sudo apt-get install python3-tk (linux)
* pip install tk (windows)

To install tqdm run the following command:
* sudo apt install python3-tqdm (linux)
* pip install tqdm (windows)

* python3 Server.py
![img_1.png](img_1.png)
* python3 Client.py
![img_2.png](img_2.png)
