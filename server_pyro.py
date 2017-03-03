#########################################################################
#  Distributed Systems Summative: Server side script, works with Pyro
#
#########################################################################
#
#########################################################################

class RegisteredUsers(object):
    userList = []

    def __init__(self):
        self.userList = []

    def addUser(self, user):
        self.userList.append(user)


class User(object):
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


class Server(object):
    registeredUsers = []

    def __init__(self):
        self.registeredUsers = RegisteredUsers()

    def login(self, username):
        currentUser = None
        userExists = False
        for user in self.registeredUsers.userList:
            if user.username == username:
                currentUser = self.authenticate(user)
                userExists = True
        if not userExists:
            currentUser = self.createUser(username)
        return currentUser

    def authenticate(self, user):
        authenticated = False
        while not authenticated:
            passwordGiven = input("Please enter your password here: ")
            if passwordGiven == user.password:
                authenticated = True
                return user

    def createUser(self, username):
        print("We did not recognize your username, so we created one for you!")
        passwordGiven = input("Please enter your password here: ")
        ''.join(e for e in passwordGiven if e.isalnum())
        currentUser = User(username, passwordGiven)
        self.registeredUsers.addUser(currentUser)
        return currentUser

    def getUsernameIndex(self, username):
        for i in range(0, len(self.registeredUsers.userList)):
            if self.registeredUsers.userList[i].username == username:
                return i

    def placeOrder(self, orderReceived, usernameIndex):
        orderReceived = [x.strip() for x in orderReceived.split(',')]
        # Ensures not more than 3 items are purchased at a time
        if len(orderReceived) > 3:
            print("\n\nUnable to make purchases; you made more purchases than allowed!")
            return False
        listOfOrders = ["Pokeball", "Ultraball", "Masterball", "Potion", "Super Potion", "Incense", "Egg Incubator",
                        "Razz Berry", "Revive", "Max Revive"]
        orderArray = ["", "", ""]
        for i in range(0, len(orderReceived)):
            # Gets the String value of the items listed above
            orderArray[i] = listOfOrders[int(orderReceived[i]) - 1]
        self.registeredUsers.userList[usernameIndex].placeOrder(orderArray)
        print("""
                    Purchases logged\n""")
        # print(registeredUsers.userList[usernameIndex])

    def viewOrders(self, usernameIndex):
        return self.registeredUsers.userList[usernameIndex].orderHistory

    def cancelOrder(self, usernameIndex, orderToCancel):
        # Delete stored order
        self.registeredUsers.userList[usernameIndex].cancelOrder(int(orderToCancel))
        print("Deleted item " + str(int(orderToCancel) + 1))
        # Send feedback to client
        print("\n\n                            Item deleted!")

