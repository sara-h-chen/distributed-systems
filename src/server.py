###############################################################################
# DISTRIBUTED SYSTEMS SUMMATIVE: SERVER PROGRAM                               #
# The system implements passive replication                                   #
###############################################################################
# TODO: Refactor headers
import json
import socket, _thread
from select import select

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

    def placeOrder(self, orderArray):
        self.orderHistory.append(orderArray)

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
    passwordGiven = bytes.decode(clientsock.recv(1024), "utf-8")
    newUser = User(username, passwordGiven)
    registeredUsers.addUser(newUser)
    # print(registeredUsers)


def getUsernameIndex(username, registeredUsers):
    for i in range(0, len(registeredUsers.userList)):
        if registeredUsers.userList[i].username == username:
            return i

def placeOrder(usernameIndex, clientsock, addr, registeredUsers):
    orderReceived = bytes.decode(clientsock.recv(1024), "utf-8")
    orderReceived = [x.strip() for x in orderReceived.split(',')]
    if len(orderReceived) > 3:
        clientsock.sendto(bytes("Unable to make purchases; you made more purchases than allowed!"))
    listOfOrders = ["Pokeball", "Ultraball", "Masterball", "Potion", "Super Potion", "Incense", "Egg Incubator", "Razz Berry", "Revive", "Max Revive"]
    orderArray = ["","",""]
    for i in range(0, len(orderReceived)):
        # Gets the String value of the items listed above
        orderArray[i] = listOfOrders[int(orderReceived[i]) - 1]
    registeredUsers.userList[usernameIndex].placeOrder(orderArray)
    print(registeredUsers.userList[usernameIndex])


def openShop(usernameIndex, clientsock, addr, registeredUsers):
    clientsock.sendto(bytes("SHOP", "utf-8"), addr)
    print("Opening SHOP on " + str(addr))
    placeOrder(usernameIndex, clientsock, addr, registeredUsers)
    clientsock.sendto(bytes("Purchases logged", "utf-8"), addr)


def viewOrders(usernameIndex, clientsock, addr, registeredUsers):
    clientsock.sendto(bytes("ORDERS", "utf-8"), addr)
    print("Opening ORDERS on " + str(addr))
    serialized = json.dumps(registeredUsers.userList[usernameIndex].orderHistory)
    clientsock.sendto(bytes(serialized, "utf-8"), addr)


def cancelOrder(usernameIndex, clientsock, addr, registeredUsers):
    clientsock.sendto(bytes("CANCEL", "utf-8"), addr)
    print("Begin CANCEL sequence on " + str(addr))
    serialized = json.dumps(registeredUsers.userList[usernameIndex].orderHistory)
    clientsock.sendto(bytes(serialized, "utf-8"), addr)
    orderToCancel = bytes.decode(clientsock.recv(1024), "utf-8")
    registeredUsers.userList[usernameIndex].cancelOrder(int(orderToCancel))
    print("Deleted item " + str(int(orderToCancel) + 1))
    clientsock.sendto(bytes("Item deleted", "utf-8"), addr)


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
    data = clientsock.recv(4096)
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
            data = clientsock.recv(4096)
            if data:
                usernameIndex = getUsernameIndex(username, registeredUsers)
                command = bytes.decode(data, "utf-8")
                if command == "1":
                    openShop(usernameIndex, clientsock, addr, registeredUsers)
                elif command == "2":
                    viewOrders(usernameIndex, clientsock, addr, registeredUsers)
                elif command == "3":
                    cancelOrder(usernameIndex, clientsock, addr, registeredUsers)
            if not (data):
                break
    clientsock.close()


# Creates new sockets for every thread that connects to the server
def createSocket(registeredUsers):
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
                read_tcp(s, registeredUsers)
            elif s == udp:
                read_udp(s)
            else:
                print("Error: Unknown socket type ", s)


############################################################
#                      MAIN METHOD                         #
############################################################

if __name__ == '__main__':
    registeredUsers = RegisteredUsers()
    createSocket(registeredUsers)