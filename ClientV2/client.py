# Created By Raju Nichols
# Date: 3/16/2023
# Description: This is the client program for the chatroom program.
#              The client is inchage of sending messages to and receiving messages from the server.
#              Some main aspects of the client is making sure that it uses valid commands and have correct logic from client to server.
#              This client was built with the socket api, and allows us to connect to the server.
#              The commands the client allows are login, newuser, send(not a real command just the output showed it), send all, send USERID, who, and logout.
#              The main difference between this version is the use of threading and the new commands


import socket
import threading
import sys

# Required IP and Port based on the requirements
SERVER_IP = "127.0.0.1"
PORT = 15904
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Keep track of the state of the client
is_connected = True;
is_logged_in = False;

# This allows the client to recieve messages from the server
# it also handles if the client is connected or not and is the client is logged in or not
def receive_messages():
    global is_logged_in
    global is_connected
    while True:
        try:
            message = client.recv(1024).decode()
            if message == "logout confirmed":
                is_logged_in = False
            print(message)
            if not message:
                print("connection closed by server")
                is_connected = False
                break
        except Exception as e:
            print(f"Error: {e}")
            is_connected = False
            break

# This function is similar to the V1 function the main difference is the extra commands
# It includes updated validation for the send all and send USERID as well includes the who command        
def validate_command(cmd):
    cmd_parts = cmd.split(" ")
    if cmd_parts[0] in ["login", "newuser"]:
        if len(cmd_parts) == 3:
            if cmd_parts[0] == "newuser":
                client_name = cmd_parts[1]
                client_password = cmd_parts[2]
                if 3 <= len(client_name) <= 32 and 4 <= len(client_password) <= 8:
                    return True
            else:
                return True
    elif cmd_parts[0] == "send":
        if len(cmd_parts) == 1:
            return True
        elif len(cmd_parts) >= 3:
            if cmd_parts[1] == "all":
                message = " ".join(cmd_parts[2:])
                if 1 <= len(message) <= 256:
                    return True
            else:
                message = " ".join(cmd_parts[2:])
                if 1 <= len(message) <= 256:
                    return True
    elif cmd_parts[0] in ["who", "logout"]:
        return len(cmd_parts) == 1
    return False

# The main difference between the V1 client and the this version is the use of threading.
# When I was testing the client I found it hard to try and get messages back from the server, I would get timed out a lot,
# So I used threading to allow the client to get create its own thread to receive messages from the server, it worked out better for me this way
# Majoirty of this is simiar to the V1 version it makes sure certain commands arent being used in the wrong place
# Things like using commands when the user isnt logged in, and if there are any invalid commands the client uses. 
def main():
    global is_connected
    client.connect((SERVER_IP, PORT))
    print("My chat room client. Version Two.")

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    is_logged_in = False

    while is_connected:
        command = input("")
        if validate_command(command):
            if command.startswith("login ") and not is_logged_in:
                is_logged_in = True
            elif command == "logout" and is_logged_in:
                client.send(command.encode())  
                is_logged_in = False
                continue

            if not is_logged_in and not command.startswith("login ") and not command.startswith("newuser "):
                print("Denied. Please login first.")
            else:
                client.send(command.encode())
        else:
            print("Invalid command.")
    sys.exit(0) # I added this to try and allow me to manually exit the server but I didnt have any luck. it wasnt part of the requirements only just to make sure nothing crashed.

# Starting the program
main()