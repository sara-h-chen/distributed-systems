#####################################################################################
#  DISTRIBUTED SYSTEMS SUMMATIVE: The client Python program which should do the     #
#  following: allow the user to place an order (1), retrieve his/her order history  #
#  (2), cancel an order                                                             #
#####################################################################################
# TODO: Refactor headers
import json
import socket

serverName = ''
serverPort = 12500
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connectToServer():
    serverSocket.connect((serverName, serverPort))
    username = input(mainGreeting())
    ''.join(e for e in username if e.isalnum())
    # Sends username to server
    serverSocket.send(bytes(username, "utf-8"))
    authenticated = False
    while not authenticated:
        # Receives authentication response from server
        print(bytes.decode(serverSocket.recv(1024), "utf-8"))
        password = input("Please enter your password here: ")
        ''.join(e for e in password if e.isalnum())
        serverSocket.send(bytes(password, "utf-8"))
        # Receive confirmation for authentication
        authenticated = bytes.decode(serverSocket.recv(1024), "utf-8")
    if authenticated == "True":
        # After authentication
        welcome = serverSocket.recv(4096)
        print(bytes.decode(welcome, "utf-8"))
        menuChoice = input(mainMenu())
        serverSocket.send(bytes(menuChoice, "utf-8"))
        while True:
            packet = bytes.decode(serverSocket.recv(1024), "utf-8")
            if packet:
                print("                            " + packet)
                if packet == "SHOP":
                    openShop()
                elif packet == "ORDERS":
                    # TODO: Function to check order history
                    viewOrders()
                else:
                    menuChoice = input(mainMenu())
                    serverSocket.send(bytes(menuChoice, "utf-8"))
            if not packet:
                print("Exiting...")
                break


    # TODO: What happens when you're not authenticated?
    # else:


def openShop():
    shopGreeting = bytes.decode(serverSocket.recv(4096), "utf-8")
    print(shopGreeting)
    choice = input("""
If I want to purchase a Pokeball, a Potion, and a Razz Berry, I place the order as follows:
      1, 4, 8
Your turn! Choose up to a max of 3 items to purchase: """)
    serverSocket.send(bytes(choice, "utf-8"))


def mainGreeting():
    return ("""
                                        ,'\\
          _.----.        ____         ,'  _\   ___    ___     ____
      _,-'       `.     |    |  /`.   \,-'    |   \  /   |   |    \  |`.
      \      __    \    '-.  | /   `.  ___    |    \/    |   '-.   \ |  |
       \.    \ \   |  __  |  |/    ,','_  `.  |          | __  |    \|  |
         \    \/   /,' _`.|      ,' / / / /   |          ,' _`.|     |  |
          \     ,-'/  /   \    ,'   | \/ / ,`.|         /  /   \  |     |
           \    \ |   \_/  |   `-.  \    `'  /|  |    ||   \_/  | |\    |
            \    \ \      /       `-.`.___,-' |  |\  /| \      /  | |   |
             \    \ `.__,'|  |`-._    `|      |__| \/ |  `.__,'|  | |   |
              \_.-'       |__|    `-._ |              '-.|     '-.| |   |
                                      `'                            '-._|

                         Please enter your username:
     """).format()


def mainMenu():
    return (("""
    What would you like to do?
    1) Browse the item shop
    2) View order history
    3) Exit

    Choose by entering the Option number
    E.g. If I want to quit, I would type: 3
    """)).format()


def viewOrders():
    ordersMade = bytes.decode(serverSocket.recv(4096), "utf-8")
    print("""
               .-. \_/ .-.
               \.-\/=\/.-/
            '-./___|=|___\.-'
           .--| \|/`"`\|/ |--.
          (((_)\  .---.  /(_)))
           `\ \_`-.   .-'_/ /`_     YOUR ORDERS:
             '.__       __.'(_))
                 /     \     //
                |       |__.'/
                \       /--'`
            .--,-' .--. '----.
           '----`--'  '--`----'

        """)
    ordersMade = json.loads(ordersMade)
    for i in range(0, len(ordersMade)):
        print(str(i+1) + ") " + str(ordersMade[i]))


if __name__ == '__main__':
    connectToServer()
    serverSocket.close()