###########################################################################
#  Distributed Systems Summative: Server side script, works with Pyro4    #
#  Stores user information, including usernames, passwords and orders     #
#  The @property notation before a function allows it to behave like      #
#  the dot-notation attributes since they have been disabled due to       #
#  security concerns.
###########################################################################
#  WARNING: THE FRONT-END PROGRAM NEEDS TO BE STARTED FIRST, FOLLOWED BY  #
#  THE SERVER, THEN THE CLIENT PROGRAM                                    #
###########################################################################
import pickle
import sys
import Pyro4.util
import socket
import time

import struct
import _thread

sys.excepthook = Pyro4.util.excepthook


###############################################################
#           CLASSES USED TO STORE DATA WITHIN SERVER          #
###############################################################

@Pyro4.expose
class RegisteredUsers(object):
    userList = []

    def __init__(self):
        self.userList = []

    @property
    def getUserList(self):
        return self.userList

    def addUser(self, user):
        self.userList.append(user)


@Pyro4.expose
class User(object):
    username = ""
    password = ""
    orderHistory = []

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.orderHistory = []

    @property
    def getOrderHistory(self):
        return self.orderHistory

    @property
    def getPassword(self):
        return self.password

    @property
    def getUsername(self):
        return self.username

    def placeOrder(self, orderArray):
        self.orderHistory.append(orderArray)

    def cancelOrder(self, index):
        del self.orderHistory[index]


##############################################################
#                      MAIN SERVER CLASS                     #
##############################################################

@Pyro4.expose
class Server(object):
    registeredUsers = []
    primary = False

    def __init__(self, isPrimary):
        self.registeredUsers = RegisteredUsers()
        self.primary = isPrimary

    @property
    def getRegisteredUsers(self):
        return self.registeredUsers

    @property
    def getAllRegisteredUsers(self):
        return self.getRegisteredUsers.getUserList

    @property
    def isPrimary(self):
        return self.primary

    def userExists(self, username):
        for user in self.registeredUsers.getUserList:
            if user.getUsername == username:
                return True
        return False

    def setNewState(self, newState):
        self.registeredUsers = newState

    def getNewState(self):
        return self.getRegisteredUsers

    def authenticate(self, usernameIndex, passwordGiven):
        if passwordGiven == self.getRegisteredUsers.getUserList[usernameIndex].getPassword:
            return True
        else:
            return False

    def createUser(self, username, passwordGiven):
        currentUser = User(username, passwordGiven)
        self.getRegisteredUsers.addUser(currentUser)

    def getUsernameIndex(self, username):
        for i in range(0, len(self.getRegisteredUsers.userList)):
            if self.getRegisteredUsers.getUserList[i].username == username:
                return i

    def placeOrder(self, orderReceived, usernameIndex):
        orderReceived = [x.strip() for x in orderReceived.split(',')]
        # Ensures not more than 3 items are purchased at a time
        if len(orderReceived) > 3:
            return False
        listOfOrders = ["Pokeball", "Ultraball", "Masterball", "Potion", "Super Potion", "Incense", "Egg Incubator",
                        "Razz Berry", "Revive", "Max Revive"]
        orderArray = ["", "", ""]
        for i in range(0, len(orderReceived)):
            # Gets the String value of the items listed above
            orderArray[i] = listOfOrders[int(orderReceived[i]) - 1]
        self.getRegisteredUsers.getUserList[usernameIndex].placeOrder(orderArray)
        return True

    def viewOrders(self, usernameIndex):
        return self.getRegisteredUsers.getUserList[usernameIndex].getOrderHistory

    def cancelOrder(self, usernameIndex, orderToCancel):
        # Delete stored order
        self.getRegisteredUsers.getUserList[usernameIndex].cancelOrder(int(orderToCancel))
        print("Deleted item " + str(int(orderToCancel) + 1))
        return True

    def returnAllRegisteredUsers(self):
        return self.getAllRegisteredUsers


##############################################################
#                  CREATE MULTICAST GROUP                    #
##############################################################
# Reference: https://pymotw.com/2/socket/multicast.html      #
##############################################################

# Multicast the current state of the primary to passive replicas
def beginMulticasting(server):
    multicastGroup = ('225.0.0.1', 10000)

    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely
    # when trying to receive data
    sock.settimeout(0.8)

    # Set time-to-live to 1 so they do not go past local
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Save the reference; it will be removed from the tuple passed in arg
    savedServerReference = server
    try:
        while True:

            serverState = pickle.dumps(savedServerReference.getRegisteredUsers)
            sock.sendto(serverState, multicastGroup)

            while True:
                try:
                    data, server = sock.recvfrom(16)
                # Retransmit if no ack received from either passive replica
                # because that would mean that nothing was sent to the mcast group
                except socket.timeout:
                    break
                else:
                    print("Received %s from %s" % (bytes.decode(data), server))

            time.sleep(30)

    finally:
        sock.close()


def beginListening(server):
    multicastGroup = '225.0.0.1'
    multicastPort = 10000

    # Look up multicast group address in name server and find out IP version
    addrinfo = socket.getaddrinfo(multicastGroup, None)[0]

    # Create a socket
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind it to the port
    s.bind(('', multicastPort))

    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    # Join group
    if addrinfo[0] == socket.AF_INET: # IPv4
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    else:
        mreq = group_bin + struct.pack('@I', 0)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    # Loop, printing any data we receive
    while True:
        data, sender = s.recvfrom(1500)
        while data[-1:] == '\0': data = data[:-1]  # Strip trailing \0's
        data = pickle.loads(data)
        server.setNewState(data)
        # TO DEBUG
        # try:
        #     print(*server.registeredUsers.userList, sep=',')
        #     print(*server.registeredUsers.userList[1].orderHistory, sep=',')
        # except:
        #     print("None")

        s.sendto(bytes("ack", "utf-8"), sender)


############################################################
#                      MAIN METHOD                         #
############################################################

if __name__ == '__main__':
    # Creates a Server instance
    server = Server(False)
    if server.isPrimary:
        _thread.start_new_thread(beginMulticasting, (server,))

        nameserv = Pyro4.locateNS()
        daemon = Pyro4.Daemon()
        # Binds the Server instance to the nameserver
        uri = daemon.register(server)
        nameserv.register("pyro.server", uri)
        print("Server is now ready")
        daemon.requestLoop()
    else:
        beginListening(server)

        ## LOOKUP
        # TODO: If the server finds that this already exists then it won't try to establish itself
        # ns = Pyro4.locateNS()
        # uri = ns.lookup("objectname")
        # # uri now is the resolved 'objectname'
        # obj = Pyro4.Proxy(uri)
        # obj.method()

