######################################################################
#
######################################################################

from server_pyro import *


class Client(object):
    currentUser = None
    server = None

    def __init__(self, usernameIndex, server):
        self.currentUser = usernameIndex
        self.server = server

    def viewOrders(self):
        ordersMade = self.server.viewOrders(self.currentUser)
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
                self.cancelOrder()
            else:
                self.action(mainMenu())
        else:
            print("""
                 No orders made yet
             """)
            self.action(mainMenu())

    def cancelOrder(self):
        print("\n\nPlease ensure you pick the right option. Here are your orders listed again: ")
        ordersMade = self.server.viewOrders(self.currentUser)
        for i in range(0, len(ordersMade)):
            print(str(i + 1) + ") " + str([item for item in ordersMade[i] if item]))
        orderToCancel = input("Which order would you like to cancel? ".format())
        self.server.cancelOrder(self.currentUser, (int(orderToCancel) - 1))

    def action(self, command):
        command = int(command)
        if command == 1:
            # Gets the LIST from Input
            shopChoice = openShop()
            self.server.placeOrder(shopChoice, self.currentUser)
        elif command == 2:
            self.viewOrders()
        elif command == 3:
            self.cancelOrder()
        else:
            return False

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


if __name__ == '__main__':
    # Set up server
    server = Server()
    username = input(mainGreeting())
    ''.join(e for e in username if e.isalnum())
    # Authenticate
    user = server.login(username)
    currentUsernameIndex = server.getUsernameIndex(user.username)
    # Create current session
    client = Client(currentUsernameIndex, server)
    print(welcomeGreeting())
    while True:
        client.action(mainMenu())
