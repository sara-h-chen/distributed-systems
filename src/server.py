###############################################################################
# DISTRIBUTED SYSTEMS SUMMATIVE: SERVER PROGRAM                               #
# The system implements passive replication                                   #
###############################################################################
# TODO: Refactor headers
import socket, _thread
from select import select
# from random import randint
# import struct
# import sys


class RegisteredUsers:
    userList = []

    def __init__(self):
        self.userList = []

    def addUser(self, user):
        self.userList.append(user)


class User:
    username = ""
    password = ""
    orderHistory = []

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.orderHistory = []

    def placeOrder(self, threeTuple):
        self.orderHistory.append(threeTuple)

    def cancelOrder(self, index):
        del self.orderHistory[index]


################################################################
#                  GAME-SPECIFIC FUNCTIONS                     #
################################################################

def startGreeting():
    return ("""
                         ."-,.__
                         `.     `.  ,
                      .--'  .._,'"-' `.
                     .    .'         `'
                     `.   /          ,'
                       `  '--.   ,-"'
                        `"`   |  \\
                           -. \, |
                            `--Y.'      ___.
                                 \     L._, \\
                       _.,        `.   <  <\                _
                     ,' '           `, `.   | \            ( `
                  ../, `.            `  |    .\`.           \ \_
                 ,' ,..  .           _.,'    ||\l            )  '".
                , ,'   \           ,'.-.`-._,'  |           .  _._`.
              ,' /      \ \        `' ' `--/   | \          / /   ..\\
            .'  /        \ .         |\__ - _ ,'` `        / /     `.`.
            |  '          ..         `-...-"  |  `-'      / /        . `.
            | /           |L__           |    |          / /          `. `.
           , /            .   .          |    |         / /             ` `
          / /          ,. ,`._ `-_       |    |  _   ,-' /               ` \\
         / .           \\"`_/. `-_ \_,.  ,'    +-' `-'  _,        ..,-.    \`.
          '         .-f    ,'   `    '.       \__.---'     _   .'   '      \ \\
        ' /          `.'    l     .' /          \..      ,_|/   `.  ,'`     L`
        |'      _.-""` `.    \ _,'  `            \ `.___`.'"`-.  , |   |    | \\
        ||    ,'      `. `.   '       _,...._        `  |    `/ '  |   '     .|
        ||  ,'          `. ;.,.---' ,'       `.   `.. `-'  .-' /_ .'    ;_   ||
        || '              V      / /           `   | `   ,'   ,' '.    !  `. ||
        ||/            _,-------7 '              . |  `-'    l         /    `||
         |          ,' .-   ,'  ||               | .-.        `.      .'     ||
         `'        ,'    `".'    |               |    `.        '. -.'       `'
                  /      ,'      |               |,'    \-.._,.'/'
                  .     /        .               .       \    .''
                .`.    |         `.             /         :_,'.'
                  \ `...\   _     ,'-.        .'         /_.-'
                   `-.__ `,  `'   .  _.>----''.  _  __  /
                        .'        /"'          |  "'   '_
                       /_|.-'\ ,".             '.'`__'-( \\
                         / ,"'"\,'               `/  `-.|"

                                Login successful!

                        WELCOME TO THE WORLD OF POKEMON""").format()


def authenticate(clientsock, addr, user):
    authenticated = False
    while not authenticated:
        givenPass = clientsock.recv(1024)
        if givenPass == user.password:
            authenticated = True
            clientsock.sendto(bytes("True", "utf-8"), addr)


def createUser(username, clientsock, addr, registeredUsers):
    clientsock.sendto(bytes("We did not recognize your username, so we created one for you!", "utf-8"), addr)
    passwordGiven = bytes.decode(clientsock.recv(1024))
    newUser = User(username, passwordGiven)
    registeredUsers.addUser(newUser)
    print(registeredUsers)


def getUsernameIndex(username, registeredUsers):
    registeredUsers.userList.index(User.username)


#####################################################################
#                    SOCKET-SPECIFIC FUNCTIONS                      #
#####################################################################

# Reads UDP data packets; you can ignore this!
def read_udp(serverSocket):
    data, addr = serverSocket.recvfrom(2048)
    serverSocket.sendto(startGreeting(), addr)


def read_tcp(serverSocket, registeredUsers):
    connectionSocket, addr = serverSocket.accept()
    _thread.start_new_thread(handler, (connectionSocket, addr, registeredUsers))


def handler(clientsock, addr, registeredUsers):
    data = clientsock.recv(1024)
    if data:
        username = data.decode("utf-8")
        userExists = False
        for user in registeredUsers.userList:
            if user.username == username:
                userExists = True
                authenticate(clientsock, addr, user)
        if not userExists:
            createUser(username, clientsock, addr, registeredUsers)
            clientsock.sendto(bytes("True", "utf-8"), addr)
        clientsock.sendto(bytes(startGreeting(), "utf-8"), addr)
    while True:
        data = clientsock.recv(1024)
        if not (data):
            break
    clientsock.close()


def createSocket(registeredUsers):
    serverPort = 12500
    serverAddress = ('', 10000)
    # Create socket for TCP
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', serverPort))
    tcp.listen(1)

    # Create socket for UDP; you can ignore this!
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(('', serverPort))

    input = [tcp, udp]

    while True:
        inputready, outputready, exceptready = select(input,[],[])

        for s in inputready:
            if s == tcp:
                read_tcp(s, registeredUsers)
            elif s == udp:
                read_udp(s)
            else:
                print("Error: Unknown socket type ", s)

if __name__ == '__main__':
    registeredUsers = RegisteredUsers()
    createSocket(registeredUsers)
    print(getUsernameIndex("jrvh15", registeredUsers))