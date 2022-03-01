from socket import SocketKind
from unittest import TestCase
from Client import Client

class Test(TestCase):
    """
    in order to run this test class you need to activate the server from the terminal before playing the tests
    and also put in comment the "client = Client()" line in Client class (this line activate a Client)
    """

    def test_connection(self):
        """
        this method test the connection between client and server
        """
        client = Client()
        self.assertEqual(client.sock.type,SocketKind.SOCK_STREAM)
        self.assertEqual(client.sock.getpeername()[1],55000)

    def test_nickname(self):
        """
        this method test the nickname of client
        """
        client1= Client()
        self.assertEqual("ohad",client1.nickname)

    def test_is_running(self):
        """
        this method test the main loop of client chat
        """
        client2 = Client()
        self.assertTrue(client2.running)