##########################################################################
#  Distributed Systems Summative: Front-End Program, implemented
#  using Pyro4
#
##########################################################################
#  THIS SCRIPT SHOULD BE RUN FIRST, BEFORE THE SERVER AND CLIENT, AS IT
#  IS USED TO BEGIN THE NAMESERVER.
#
##########################################################################

import sys
import _thread
import socket
import json
from select import select

import Pyro4.util

sys.excepthook = Pyro4.util.excepthook


#####################################################################
#                    SOCKET-SPECIFIC FUNCTIONS                      #
#####################################################################

# Reads UDP data packets; you can ignore this!
def read_udp(serverSocket):
    data, addr = serverSocket.recvfrom(1024)


def read_tcp(serverSocket):
    connectionSocket, addr = serverSocket.accept()
    _thread.start_new_thread(handler, (connectionSocket, addr))


def handler(clientsock, addr):
    # Establish Proxy only where needed to ensure it is up-to-date
    server = Pyro4.Proxy("PYRONAME:pyro.server")
    data = clientsock.recv(1024)
    if data:
        username = data.decode("utf-8")
        userExists = False
        if server.userExists(username):
            usernameIndex = server.getUsernameIndex(username)
            authenticated = False
            while not authenticated:
                clientsock.sendto(bytes("nonauth", "utf-8"), addr)
                passwordGiven = clientsock.recv(1024)
                passwordGiven = bytes.decode(passwordGiven, "utf-8")
                authenticated = server.authenticate(usernameIndex, passwordGiven)
            clientsock.sendto(bytes("auth", "utf-8"), addr)
            userExists = True
            clientsock.sendto(bytes(str(usernameIndex), "utf-8"), addr)
        if not userExists:
            clientsock.sendto(bytes("create", "utf-8"), addr)
            passwordGiven = bytes.decode(clientsock.recv(1024), "utf-8")
            server.createUser(username, passwordGiven)
            usernameIndex = server.getUsernameIndex(username)
            clientsock.sendto(bytes(str(usernameIndex), "utf-8"), addr)
        usernameIndex = server.getUsernameIndex(username)
        while True:
            # Establish Proxy before every command, to ensure that it connects to a server
            server = Pyro4.Proxy("PYRONAME:pyro.server")
            command = clientsock.recv(1024)
            if command:
                command = bytes.decode(command, "utf-8")
                if command == "1":
                    orderToMake = bytes.decode(clientsock.recv(1024))
                    if server.placeOrder(orderToMake, usernameIndex):
                        clientsock.sendto(bytes("True", "utf-8"), addr)
                    else:
                        clientsock.sendto(bytes("False", "utf-8"), addr)
                elif command == "2":
                    serialized = json.dumps(server.viewOrders(usernameIndex))
                    clientsock.sendto(bytes(serialized, "utf-8"), addr)
                elif command == "3":
                    serialized = json.dumps(server.viewOrders(usernameIndex))
                    clientsock.sendto(bytes(serialized, "utf-8"), addr)
                    orderToCancel = bytes.decode(clientsock.recv(1024))
                    server.cancelOrder(usernameIndex, orderToCancel)
                    # Send feedback to client
                    clientsock.sendto(bytes("True", "utf-8"), addr)
            if not (data):
                break
    clientsock.close()


# Creates new sockets for every thread that connects to the server
def createSocket():
    serverPort = 12500
    serverAddress = ('', 10000)
    # Create socket for TCP
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', serverPort))
    tcp.listen(1)
    print("Listening on Port " + str(serverPort))

    # Create socket for UDP; you can ignore this!
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(('', serverPort))

    input = [tcp, udp]

    while True:
        inputready, outputready, exceptready = select(input,[],[])

        for s in inputready:
            if s == tcp:
                read_tcp(s)
            elif s == udp:
                read_udp(s)
            else:
                print("Error: Unknown socket type ", s)


##########################################################################
#                            MAIN METHOD                                 #
##########################################################################

if __name__ == '__main__':
    # Spin off a new thread to run the nameserver
    _thread.start_new_thread(Pyro4.naming.startNSloop, ())
    createSocket()
