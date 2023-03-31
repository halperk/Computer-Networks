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
client.setblocking(1) 
client.settimeout(0.5)

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

def sendCommand(command):
    # send a command to the server
    command_length = len(command)
    num_bytes_to_send = command_length

    # send the command until completely sent
    while num_bytes_to_send > 0:
        num_bytes_to_send -= client.send(command[command_length-num_bytes_to_send:])

def sendCommands():
    print("[STARTED] Enter your inputs below...")
    while True:
        print("[INPUT] Please enter your input: ", end="")
        user_input = input()
        if user_input == "!quit":
            # close the client, finish
            print(f"[EXIT] Bye bye {username}, see you again!")
            client.close()
            break
        elif user_input == "!who":
            # list all online users
            command = ("LIST\n").encode(FORMAT)
            sendCommand(command)
        elif len(user_input) > 0 and user_input[0] == "@":
            # send a message to an active user
            target_username = user_input.split()[0][1:]
            message = user_input[(len(target_username)+2):]
            send_request = ("SEND " + target_username + " " + message + "\n").encode(FORMAT)
            sendCommand(send_request)
        else:
            print("[INVALID] Invalid command, please try again!")
            continue

def receiveCommands():
    buffer = b''
    received = []

    while True:
        try:
            data = client.recv(1)
            if data == b'\n':
                # current result is finished
                processed_buffer = buffer.decode(FORMAT)
                received.append(processed_buffer)
                result = processed_buffer.split(" ")
                print(result[0])

                if result[0] == "LIST-OK":
                    user_list = []
                    for user in result[1].split(","):
                        user_list.append(user)
                    print("[USERS]", user_list)
                elif result[0] == "SEND-OK":
                    print(f"[{result[0]}] Message sent successfully. Ready for more.")
                elif result == "BAD-DEST-USER":
                    print(f"[{result[0]}] User is not online. Try again.")
                elif result[0] == "DELIVERY":
                    delivered_message = processed_buffer[len(result[0])+len(result[1])+2:]
                    print(result[1], "sent", delivered_message)
                elif result[0] == "BAD-RQST-HDR":
                    print(f"[{result[0]}] Header error detected. Please retry request.")
                elif result[0] == "BAD-RQST-BODY":
                    print(f"[{result[0]}] Body error detected. Please retry request.")
                else:
                    print("UNKNOWN")

                buffer = b''
            else:
                # add data to buffer
                buffer += data
        except:
            # client is closed, finish
            break

send_thread = threading.Thread(target=sendCommands)
send_thread.start()

receive_thread = threading.Thread(target=receiveCommands)
receive_thread.start()

send_thread.join()
receive_thread.join()

client.close()