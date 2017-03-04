#########################################################################
#  Distributed Systems Summative: Client side script, works with Pyro4  #
#  Allows the user to place an order (1), retrieve their order history  #
#  (2), and cancel their orders (3)                                     #
#########################################################################
#  WARNING: THE FRONT-END PROGRAM NEEDS TO BE STARTED FIRST, FOLLOWED   #
#  BY THE SERVER, THEN THE CLIENT PROGRAM                               #
#########################################################################
import json
import socket


################################################################
#            CLASS TO MAINTAIN STATE OF CURRENT SESSION        #
################################################################

class Client(object):
    currentUser = None
    serverSocket = None

    def __init__(self, usernameIndex, serverSocket):
        self.currentUser = usernameIndex
        self.serverSocket = serverSocket

    def viewOrders(self):
        ordersMade = bytes.decode(self.serverSocket.recv(2048), "utf-8")
        ordersMade = json.loads(ordersMade)
        print("""
                            ORDERS

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
                self.cancelOrder()
            else:
                self.action(mainMenu())
        else:
            print("""
                 No orders made yet
             """)
            self.action(mainMenu())

    def cancelOrder(self):
        self.serverSocket.send(bytes("3", "utf-8"))
        print("""
                                  CANCEL

Please ensure you pick the right option. Here are your orders listed again: """)
        ordersMade = bytes.decode(self.serverSocket.recv(1024), "utf-8")
        ordersMade = json.loads(ordersMade)
        for i in range(0, len(ordersMade)):
            print(str(i + 1) + ") " + str([item for item in ordersMade[i] if item]))
        orderToCancel = input("Which order would you like to cancel? ".format())
        self.serverSocket.send(bytes(str(int(orderToCancel) - 1), "utf-8"))
        if bytes.decode(self.serverSocket.recv(1024), "utf-8") == "True":
            print("\n                           Order cancelled!")
            return True

    def action(self, command):
        # Sends command to frontend
        self.serverSocket.send(bytes(command, "utf-8"))
        command = int(command)
        if command == 1:
            shopChoice = openShop()
            self.serverSocket.send(bytes(shopChoice, "utf-8"))
            conf = bytes.decode(self.serverSocket.recv(1024), "utf-8")
            if conf == "True":
                print("""
                                             Purchases logged\n""")
            else:
                print("\n\nUnable to make purchases; you made more purchases than allowed!")
        elif command == 2:
            self.viewOrders()
        else:
            return False


################################################################
#                 SOCKET-RELATED FUNCTIONS                     #
################################################################

def connectToFrontEnd():
    serverName = ''
    serverPort = 12500
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Create TCP connection to frontend
    serverSocket.connect((serverName, serverPort))
    username = input(mainGreeting())
    ''.join(e for e in username if e.isalnum())
    # Sends username to frontend
    serverSocket.send(bytes(username, "utf-8"))
    while True:
        loginPacket = bytes.decode(serverSocket.recv(1024), "utf-8")
        if loginPacket == "nonauth":
            passwordGiven = input("Please enter your password: ")
            serverSocket.send(bytes(passwordGiven, "utf-8"))
        if loginPacket == "auth":
            print("Welcome back!")
            break
        if loginPacket == "create":
            print("We did not recognize your username, so we created one for you!")
            passwordGiven = input("Please enter your password here: ")
            ''.join(e for e in passwordGiven if e.isalnum())
            serverSocket.send(bytes(passwordGiven, "utf-8"))
            break
    usernameIndex = bytes.decode(serverSocket.recv(1024), "utf-8")
    currentSession = Client(usernameIndex, serverSocket)
    print(welcomeGreeting())
    while True:
        currentSession.action(mainMenu())


################################################################
#                    ASCII-ART FUNCTIONS                       #
################################################################
#  All ASCII art is held on the client-side to reduce size of  #
#  packets being sent over the network.                        #
################################################################

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


def welcomeGreeting():
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


def mainMenu():
    menuChoice = input("""
    What would you like to do?
    1) Browse the item shop
    2) View order history

    Choose by entering the Option number
    E.g. If I want to view my order history, I would type: 2
    """)
    return menuChoice


def openShop():
    choice = input(("""
                                SHOP

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
    return choice


#########################################################
#                     MAIN METHOD                       #
#########################################################

if __name__ == '__main__':
    connectToFrontEnd()
