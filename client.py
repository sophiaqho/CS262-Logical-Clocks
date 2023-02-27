import os
import socket
import math
import time
import uuid

set_port = 8887
set_host = ''


class ClientSocket:

    def __init__(self, client=None):
        # We store if the client is currently logged in (to see if they have permission to
        # send/receive messages), their username, password, and 
        # queue of messages that they have received.

        # All of these objects are stored in a dictionary on the server of [username : ClientSocket object]

        self.logged_in = False
        self.username = ''
        self.messages = []
        self.logical_clock_time = 0
        if client is None:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.client = client


    # basic get/set functions to allow for the server to update these values
    def getStatus(self):
        return self.logged_in

    def setStatus(self, update_status):
        self.logged_in = update_status

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def setPassword(self, password):
        self.password = password

    def getMessages(self):
        return self.messages

    def emptyMessages(self):
        self.messages = []

    def addMessage(self, message_string):
        self.messages.append(message_string)


    # Function to create a new account
    # returns the client username
    # TODO- add the time stamp
    def create_client_username(self, host, port, pwd_client = None):
        # message contains 'create'- send this to the server
        # so the server runs the create function

        self.client.sendto('create'.encode(), (host, port))

        # server will send back a username (UUID)
        data = self.client.recv(1024).decode()

        # Update ClientSocket object username and log in fields
        self.username = data
        self.logged_in = True
        print('Your unique username is '  + data)

        return self.getUsername()

    # helper function to parse messages as everything is sent as strings
    # return is of the format (sender username, message)
    def parse_live_message(self, message):
        # message format is sender username +message
        # username is 1 characters total (fixed length)
        return (message[:1], message[1:])


    # function to print all available messages
    # returns the # of messages delivered
    def deliver_available_msgs(self, available_msgs):
        # want to receive all undelivered messages
        for received_msg in available_msgs:
        # get Messages() has 
            sender_username, msg = self.parse_live_message(received_msg)
            print("Message from " + sender_username + ": " + msg)
        
        return len(available_msgs)

    
    # function used to send a message to another user!/yourself!
    # returns True if message was delivered
    # False otherwise
    def send_message(self, recipient_username, host, port, msg_content = None):
        # modified on server side to have
        self.client.sendto(('sendmsg' + self.getUsername() + recipient_username + str(self.logical_clock_time)).encode(), (host, port))
        # receive confirmation from the server that it was delivered or error message elsewhere
        data = self.client.recv(1024).decode()
        # print to see whether the 
        # TODO delete this later on
        print(data)
        return not data == "Message could not be delivered. Please try again."

    
    # function used to receive messages from the server
    # returns available messages
    def receive_messages(self, host, port):
        # inform server that you want to get new messages
        self.client.sendto('msgspls!'.encode(), (host, port))

        # server will send back the length of messages
        len_msgs = self.client.recv(1024).decode()

        # TODO- see if we still want to do the length of stuff- currentyl matches 
        # server side
        # or do we want to recieve one message at a time?! to reduce this flow
        # send message to control info flow (ensure you are ready to decode msg)
        message = 'ok'
        self.client.sendto(message.encode(), (host, port))

        # server will send back messages of proper length
        data = self.client.recv(int(len_msgs)).decode()

        return data

    def client_exit(self):
        print(f'Connection closed.')
        self.client.close()
        self.logged_in = False
        return True

    # this is the main client program that we run- it calls on all subfunctions
    def client_program(self):
        host = set_host
        port = set_port

        self.client.connect((host, port))

        # handle initial information flow- either will login or create a new account
        # You need to either log in or create an account first

        while not self.logged_in:
            # create a username
            self.create_client_username(host, port)
            
        # can only enter loop if you are logged in
        if self.logged_in:

            message = input("""
            To send a message, enter the recipient username, 
            'listaccts' to list all active usernames, 
            'exit' to leave program, or 
            'delete' to delete your account: 
            """)
            # TODO- this!
            # generate a number to decide an action and then call upon that function for the acton

                # send message otherwise
                else:
                    server_message = self.send_message(message, host, port)
                    
                    # print output of the server- either that it was successfully sent or that the user was not found.
                    print('Message from server: ' + server_message)

                # # get all messages that have been delivered to this client
                received_msgs = self.receive_messages(host, port)

                if received_msgs != 'No messages available':
                    # deliver available messages if there are any
                    available_msgs = received_msgs.split('we_hate_cs262')[1:]
                    self.deliver_available_msgs(available_msgs)

                # re query for new client actions
                message = input("""
                To send a message, enter the recipient username, 
                'listaccts' to list all active usernames, 
                'exit' to leave program, or 
                'delete' to delete your account: 
                """)

            # # will only exit while loops on 'exit' or 'delete'
            # # read undelivered messages for exit
            # if message.strip() == 'exit':
                # self.client_exit()

# program creates a ClientSocket object and runs client_program which
# handles input and directs it to the appropriate function
if __name__ == '__main__':
    socket = ClientSocket()
    socket.client_program()