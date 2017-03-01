#####################################################################################
#  Distributed Systems Summative: The client Python program which does the          #
#  following: allow the user to place an order (1), retrieve his/her order history  #
#  (2), cancel an order (3)                                                         #
#####################################################################################
#  TO REDUCE THE LOAD ON THE SERVER AS WELL AS BANDWIDTH CONSUMPTION, ALL           #
#  PROCESSING IS CARRIED OUT ON THE CLIENT-SIDE, I.E. ASCII ART IS CONTAINED WITHIN #
#  THE CLIENT PROGRAM (with the exception of the first graphic, which was entirely  #
#  to observe how large packets are transmitted).
#####################################################################################

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
        mainMenu()
        while True:
            packet = bytes.decode(serverSocket.recv(1024), "utf-8")
            if packet:
                print("\n\n                            " + packet)
                if packet == "SHOP":
                    openShop()
                elif packet == "ORDERS":
                    viewOrders()
                elif packet == "CANCEL":
                    cancelOrder()
                elif packet == "TOO MANY":
                    print("Unable to make purchases; you made more purchases than allowed!")
                    mainMenu()
                else:
                    mainMenu()
            if not packet:
                print("Exiting...")
                break


##########################################################
#                        ACTIONS                         #
##########################################################

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
    menuChoice = input("""
    What would you like to do?
    1) Browse the item shop
    2) View order history

    Choose by entering the Option number
    E.g. If I want to view my order history, I would type: 2
    """)
    serverSocket.send(bytes(menuChoice, "utf-8"))


def openShop():
    choice = input(("""
    ────────▄███████████▄────────
    ─────▄███▓▓▓▓▓▓▓▓▓▓▓███▄─────
    ────███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███────  WELCOME TO THE SHOP
    ───██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██───  What would you like to purchase?
    ──██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██──  1) Pokeball
    ─██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██─  2) Ultraball
    ██▓▓▓▓▓▓▓▓▓███████▓▓▓▓▓▓▓▓▓██  3) Masterball
    ██▓▓▓▓▓▓▓▓██░░░░░██▓▓▓▓▓▓▓▓██  4) Potion
    ██▓▓▓▓▓▓▓██░░███░░██▓▓▓▓▓▓▓██  5) Super Potion
    ███████████░░███░░███████████  6) Incense
    ██░░░░░░░██░░███░░██░░░░░░░██  7) Egg Incubator
    ██░░░░░░░░██░░░░░██░░░░░░░░██  8) Razz Berry
    ██░░░░░░░░░███████░░░░░░░░░██  9) Revive
    ─██░░░░░░░░░░░░░░░░░░░░░░░██─  10) Max Revive
    ──██░░░░░░░░░░░░░░░░░░░░░██──
    ───██░░░░░░░░░░░░░░░░░░░██───
    ────███░░░░░░░░░░░░░░░███────
    ─────▀███░░░░░░░░░░░███▀─────
    ────────▀███████████▀────────


If I want to purchase a Pokeball, a Potion, and a Razz Berry, I place the order as follows:
      1, 4, 8
Your turn! Choose up to a max of 3 items to purchase: """).format())
    serverSocket.send(bytes(choice, "utf-8"))


def viewOrders():
    ordersMade = bytes.decode(serverSocket.recv(1024), "utf-8")
    ordersMade = json.loads(ordersMade)
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
    if ordersMade:
        for i in range(0, len(ordersMade)):
            print(str(i+1) + ") " + str([item for item in ordersMade[i] if item]))
        orderAction = input(("""
        1) Cancel order
        2) Main Menu
        """).format())
        if orderAction == "1":
            serverSocket.send(bytes("3", "utf-8"))
        else:
            mainMenu()
    else:
        print("""
             No orders made yet
         """)
        mainMenu()


def cancelOrder():
    print("Please ensure you pick the right option. Here are your orders listed again: ")
    ordersMade = bytes.decode(serverSocket.recv(1024), "utf-8")
    ordersMade = json.loads(ordersMade)
    for i in range(0, len(ordersMade)):
        print(str(i+1) + ") " + str([item for item in ordersMade[i] if item]))
    orderToCancel = input("Which order would you like to cancel? ".format())
    serverSocket.send(bytes(str(int(orderToCancel) - 1), "utf-8"))


######################################################
#                    MAIN METHOD                     #
######################################################

if __name__ == '__main__':
    connectToServer()
    serverSocket.close()