import socket
import threading

# server configurations
SERVER = "143.47.184.219"
PORT = 5378
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

def receive():
    # receive text from server
    received_text = b''
    while True:
        # receive next byte
        data = client.recv(1)
        if data == b'\n':
            break
        received_text += data

    # decode the data
    received_text = received_text.decode(FORMAT)

    return received_text

def send(message):
    # send a message to the server
    # get the length of the message
    message_length = len(message)
    num_bytes_to_send = message_length

    # send the message until completely sent
    while num_bytes_to_send > 0:
        num_bytes_to_send -= client.send(message[message_length-num_bytes_to_send:])
    
    received_result = receive()

    return received_result

def getUsers():
    # get all logged-in users
    request = ("LIST\n").encode(FORMAT)
    users = send(request).split(" ")

    user_list = []

    # get all the users into a list
    if users[0] == "LIST-OK":
        for user in users[1].split(","):
            user_list.append(user)

    return user_list

# connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

while True:
    # connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    
    # get username from the user
    username = input("[LOGIN] Enter your username: ")

    # send login request to the server by username
    message = ("HELLO-FROM " + username + "\n").encode(FORMAT)
    result = send(message)

    # check the status of the request
    if result == "IN-USE":
        print(f"[{result}] Username already taken. Choose another.")
    elif result == "BUSY":
        print(f"[{result}] Maximum clients reached. Try again later.")
    elif result == "BAD-RQST-HDR":
        print(f"[{result}] Header error detected. Please retry request.")
    elif result == "BAD-RQST-BODY":
        print(f"[{result}] Body error detected. Please retry request.")
    else:
        print(f"[SUCCESS] Hello {username}, you are ready to chat!")
        break

# get the inputs after successful login
print("[STARTED] Enter your inputs below...")
while True:
    print("[INPUT] Please enter your input: ", end="")
    user_input = input()

    if user_input == "!quit":
        # quit the system
        print(f"[EXIT] Bye bye {username}, see you soon!")
        client.close()
        break
    elif user_input == "!who":
        # list all the logged-in users
        user_list = getUsers()
        print("[USERS] Online users:", sorted(user_list))
    elif len(user_input) > 0 and user_input[0] == "@":
        # send a message to an active user
        target_username = user_input.split()[0][1:]
        message = user_input[(len(target_username)+2):]
        send_request = ("SEND " + target_username + " " + message + "\n").encode(FORMAT)
        result = send(send_request)
        if result == "SEND-OK":
            print(f"[{result}] Message sent successfully. Ready for more.")
        elif result == "BAD-DEST-USER":
            print(f"[{result}] User {target_username} is not online. Try again.")
    else:
        print("[INVALID] Invalid command, please try again!")
