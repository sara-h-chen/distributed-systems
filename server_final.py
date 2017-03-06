###########################################################################
#  Distributed Systems Summative: Server side script, works with Pyro4    #
#  Stores user information, including usernames, passwords and orders     #
#  The @property notation before a function allows it to behave like      #
#  the dot-notation attributes since they have been disabled due to       #
#  security concerns.                                                     #
###########################################################################
#  WARNING: THE FRONT-END PROGRAM NEEDS TO BE STARTED FIRST, FOLLOWED BY  #
#  THE SERVER, THEN THE CLIENT PROGRAM. RUNS ON PYTHON3.                  #
###########################################################################

import sys
import Pyro4.util
import time
import json

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

    def setNewState(self, listOfUsers):
        self.userList = listOfUsers


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

    def setNewState(self, listOfOrders):
        self.orderHistory = listOfOrders


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
        newState = json.loads(newState)
        # Create a temporary list to hold new state
        registeredUserList = []
        for i in range(0, len(newState)):
            try:
                # Take each User object out of encoded list
                userObject = newState[i]
                # Instantiate a new user
                user = User(userObject[0], userObject[1])
                user.setNewState(userObject[2])
                registeredUserList.append(user)
            except IndexError:
                print("No data yet")
        self.registeredUsers.setNewState(registeredUserList)
        # UNCOMMENT TO DEBUG REPLICATION
        try:
            for i in range(0, len(self.registeredUsers.userList)):
                print(self.registeredUsers.userList[i].username + ": " + str(self.registeredUsers.userList[i].getOrderHistory))
        except IndexError:
            print("No data yet")

    def getNewState(self):
        return ComplexEncoder().encode(self.getAllRegisteredUsers)

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

    # Function to test return of attribute
    def returnAllRegisteredUsers(self):
        return self.getAllRegisteredUsers


############################################################
#                   CUSTOM SERIALIZERS                     #
############################################################
#  Required because Pyro4 does not allow classes to be     #
#  sent over the network, due to security concerns         #
############################################################

class ComplexEncoder(json.JSONEncoder):
    def default(self, user):
        if isinstance(user, User):
            return [user.username, user.password, user.orderHistory]
        return json.JSONEncoder.default(self, user)


#################################################################################
#                                  MAIN METHOD                                  #
#################################################################################
#  If you would like to see the code pre-modification, please refer to:         #
#  https://github.com/sara-h-chen/distributed-systems/commit/                   #
#  01d54acfd766e168eb34fbe530bc0ba9943e6a75                                     #
#################################################################################
#  Modifications made to allow crash recovery: instead of just creating the     #
#  primary servers separately from the passive replicas, the server should now  #
#  detect if it is the first server to be established, or if there have been    #
#  changes to the connection to the primary server. If it is not the first then #
#  the server will simply join the system as a passive replica. If the server   #
#  is primary then it will be bound to the nameserver, which allows the passive #
#  replicas to pull data from it. Refer to comments in code below for full      #
#  walkthrough of modifications.                                                #
#################################################################################


if __name__ == '__main__':
    # Finds the nameserver
    nameserv = Pyro4.locateNS()
    try:
        # Checks if a primary has already been
        # registered with the nameserver
        uri = nameserv.lookup("pyro.server")
        print(uri)
        # If True, create a passive replica
        server = Server(False)
    # If a primary cannot be found, then create one
    except Exception:
        server = Server(True)

    # Depending on type of server, change behavior
    if server.isPrimary:
        with Pyro4.Daemon() as daemon:
            # Binds the Server instance to the nameserver
            uri = daemon.register(server)
            nameserv.register("pyro.server", uri)
            print("Server is now ready")
            daemon.requestLoop()
    else:
        with Pyro4.Proxy("PYRONAME:pyro.server") as primary:
            # Try to pull data from the primary continuously
            while True:
                try:
                    newState = primary.getNewState()
                    server.setNewState(newState)
                    # This is set to less time than it usually takes for a server to restart.
                    # It will not pull continuously to reduce network traffic
                    time.sleep(3)
                except Exception:
                    checkConnection = nameserv.lookup("pyro.server")
                    # If the connection from the initial primary has failed
                    # and the URI remains the same in the nameserver, take over
                    # and remove; otherwise, you know that another replica has taken over
                    # as primary
                    if checkConnection == uri:
                        # Ensure that a newly established/rebooted server cannot become primary
                        # by checking the data that the session carries
                        if server.registeredUsers.userList:
                            nameserv.remove("pyro.server")
                            print("Connection lost! Taking over as primary... ")
                            server.primary = True
                            daemon = Pyro4.Daemon()
                            uri = daemon.register(server)
                            nameserv.register("pyro.server", uri)
                            print("Backup has taken over")
                            daemon.requestLoop()
                    # Refresh URI if another replica has taken over as primary
                    primary = Pyro4.Proxy("PYRONAME:pyro.server")
                    continue
