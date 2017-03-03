##########################################################################
#  Distributed Systems Summative: The Front-End Program, implemented
#  using Pyro4
##########################################################################
#
#
##########################################################################

import client_pyro
import sys
import _thread
import socket
from select import select

import Pyro4.util

sys.excepthook = Pyro4.util.excepthook

#####################################################################
#                    SOCKET-SPECIFIC FUNCTIONS                      #
#####################################################################

# # Reads UDP data packets; you can ignore this!
# def read_udp(serverSocket):
#     data, addr = serverSocket.recvfrom(2048)
#
#
# def read_tcp(serverSocket):
#     connectionSocket, addr = serverSocket.accept()
#     _thread.start_new_thread(handler, (connectionSocket, addr))


# def handler(clientsock, addr):
#     data = clientsock.recv(1024)
#     if data:
#         # TODO: Fix this up
#         while True:
#             data = clientsock.recv(1024)
#             if data:
#                 # TODO: Add actions
#             if not (data):
#                 break
#     clientsock.close()

#
# # Creates new sockets for every thread that connects to the server
# def createSocket(registeredUsers):
#     serverPort = 12500
#     serverAddress = ('', 10000)
#     # Create socket for TCP
#     tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     tcp.bind(('', serverPort))
#     tcp.listen(1)
#     print("Listening on Port " + str(serverPort))
#
#     # Create socket for UDP; you can ignore this!
#     udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     udp.bind(('', serverPort))
#
#     input = [tcp, udp]
#
#     while True:
#         inputready, outputready, exceptready = select(input,[],[])
#
#         for s in inputready:
#             if s == tcp:
#                 read_tcp(s)
#             elif s == udp:
#                 read_udp(s)
#             else:
#                 print("Error: Unknown socket type ", s)


##########################################################################
#                            MAIN METHOD                                 #
##########################################################################

if __name__ == '__main__':
    # ns = Pyro4.locateNS()
    # uri = ns.lookup('pyro.server')

    server = Pyro4.Proxy("PYRONAME:pyro.server")
    username = "jrvh15"
    print(server.login(username))

