#####################################################################################
#  DISTRIBUTED SYSTEMS SUMMATIVE: The client Python program which should do the     #
#  following: allow the user to place an order (1), retrieve his/her order history  #
#  (2), cancel an order                                                             #
#####################################################################################
# TODO: Refactor headers
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

    # TODO: Fix this
    else:
        while True:
            serverSocket.recv(2048)


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


if __name__ == '__main__':
    connectToServer()
    serverSocket.close()