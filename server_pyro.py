###########################################################################
#  Distributed Systems Summative: Server side script, works with Pyro4    #
#  Stores user information, including usernames, passwords and orders     #
###########################################################################
#  WARNING: THE FRONT-END PROGRAM NEEDS TO BE STARTED FIRST, FOLLOWED BY  #
#  THE SERVER, THEN THE CLIENT PROGRAM                                    #
###########################################################################

import sys
import Pyro4.util

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

    def __init__(self):
        self.registeredUsers = RegisteredUsers()

    @property
    def getRegisteredUsers(self):
        return self.registeredUsers

    @property
    def getAllRegisteredUsers(self):
        return self.getRegisteredUsers.getUserList

    def userExists(self, username):
        for user in self.registeredUsers.getUserList:
            if user.getUsername == username:
                return True
        return False

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

############################################################
#                      MAIN METHOD                         #
############################################################

if __name__ == '__main__':
    # Creates a Server instance
    server = Server()
    nameserv = Pyro4.locateNS()
    daemon = Pyro4.Daemon()
    # Binds the Server instance to the NameServer
    uri = daemon.register(server)
    nameserv.register("pyro.server", uri)
    print("Server is now ready")
    daemon.requestLoop()