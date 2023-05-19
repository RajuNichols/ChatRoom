# Created By Raju Nichols
# Date: 3/16/2023
# Description: This is the server program V2 needed for the chatroom.
#              This is where the server communicates with the client.
#              This server accepts command such as login, newuser, send(kinda), send all, send USERID, who, and logout.
#              The server will get the command from the client and will perform what is needed of the command 
#              The difference between this version and V1 is this also uses threading to handle multiple clients.

import socket
import threading
import os

# Required num of clients, Port, and IP from the requirments
MAXCLIENTS = 3
PORT = 15904
SERVER_IP = "127.0.0.1"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, PORT))
server.listen(MAXCLIENTS)

#list of clients and addresses
clients = {}
addresses = {}

# This is the same as V1 just loads in users based on the users.txt file
# if file not found will create one
def load_users():
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.write("(Tom, Tom11)\n(David, David22)\n(Beth, Beth33)")
    with open("users.txt", "r") as f:
        users = {line.strip()[1:-1].split(", ")[0]: line.strip()[1:-1].split(", ")[1] for line in f.readlines()}
    return users

users = load_users()

# Same as V1 this will just add to the users.txt file
def save_users():
    with open("users.txt", "w") as f:
        for user, password in users.items():
            f.write(f"({user}, {password})\n")

# This function acts as a broadcast this is used for when something needs to sent to users that are logged in.
# I will note that based on the outputs it shows that the broadcasted message shouldnt be sent back to the client, that sent the broadcast
# so there is a check to make sure it doesnt.
def broadcast(msg, sender, exclude_sender=False):
    for client, user in clients.items():
        if exclude_sender and client == sender:
            continue
        if user:  # Check if the user is logged in
            client.send(msg.encode())

# This is used for the send USERID it simply goes thru the clients and sends to the user that the sender client wanted.        
def unicast(msg, recipient):
    for client, user in clients.items():
        if user == recipient:
            client.send(msg.encode())
            break

# This is the main section. This is where the server gets the messages from the clients and sends messages back to the clients.
# This is similar to V1 but with extra such as needed to broadcast certain messages to everyone.
# This also includes the new commands such as send all, send USERID, and who
# The hardest logic was the send all and send USERID because I needed a way to send to everyone sometimes and send only to a specific user.
# because of that I created the helper functions above to do just that. 
def handle_client(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg:
                cmd = msg.split(" ", 1)[0]
                if cmd == "login":
                    _, user, password = msg.split(" ")
                    if user in users and users[user] == password:
                        clients[client] = user
                        client.send("login confirmed".encode())
                        broadcast(f"{user} joined.", client, exclude_sender=True)
                        print(f"{user} login.")
                    else:
                        client.send("login failed".encode())
                        
                elif clients[client] is None:
                    if cmd in ["newuser", "send", "who", "logout"]:
                        client.send("Denied. Please login first.".encode())
                    else:
                        client.send("Invalid command.".encode())
                        
                elif cmd == "newuser":
                    _, user, password = msg.split(" ")
                    if user not in users:
                        users[user] = password
                        save_users()
                        client.send("New user created.".encode())
                    else:
                        client.send("User already exists.".encode())
                        
                elif cmd == "send":
                    if len(msg.split(" ")) >= 3:
                        recipient, message = msg.split(" ")[1], " ".join(msg.split(" ")[2:])
                        sender = clients[client]
                        if recipient == "all":
                            broadcast(f"{sender}: {message}", client, exclude_sender=True)
                            print(f"{sender}: {message}")
                        else:
                            unicast(f"{sender}: {message}", recipient)
                            print(f"{sender} (to {recipient}): {message}")
                            
                elif cmd == "who":
                    online_users = ", ".join([user for user in clients.values() if user])
                    client.send(f"{online_users}".encode())
                    
                elif cmd == "logout":
                    user = clients[client]
                    clients[client] = ""
                    broadcast(f"{user} left.", client, exclude_sender=True)
                    print(f"{user} logout.")
                    client.close()
                    break
                
                else:
                    client.send("Invalid command.".encode())
        except Exception as e:
            print(f"Error: {e}")
            break

# Like stated eariler the main difference here is using threads for multiple clients.
# This allows for multiple clients to connect to the server
def accept_connections():
    while True:
        client, client_address = server.accept()
        addresses[client] = client_address
        clients[client] = ""
        threading.Thread(target=handle_client, args=(client,)).start()

# Prints the header and runs the program.
print("My chat room server. Version Two.")
accept_connections()