import os
import socket
import math
import time
from datetime import datetime
import random
import logging

set_port = 8887
set_host = ''


class ClientSocket:

    def __init__(self, client=None):
        # We store if the client is currently logged in (to see if they have permission to
        # send/receive messages), their username, and 
        # queue of messages that they have received.

        self.logged_in = False
        self.username = ''
        self.messages = []
        self.logical_clock_time = 0
        self.other_machines = ['1', '2', '3']
        self.logname = "Process"
        self.log = None

        self.time_breakdown = random.randint(1, 6)


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

    # returns the first message in the message queue and removes it from the queue
    def getFirstMessage(self):
        if self.messages:
            return self.messages.pop(0)
        return "No messages available."
    
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
        self.username = str(data)
        self.logged_in = True
        self.other_machines.remove(self.username)

        # create a logger file name and use that name to create the log file for this user
        self.logname = "Process" + self.username + "_" + str(datetime.now()) + ".csv"
        logging.basicConfig(
            filename=self.logname,
            format='%(asctime)s,%(msecs)03d, %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.INFO)

        self.log = logging.getLogger(__name__)
        
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
        # sends to one of the other machine or two machines a message that is the local logical clock time
    def send_clock_message(self, host, port, msg_content, recipient_username):
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
    
    # function to update the local logical clock 
    def update_local_logical_clock(self):
        # TODO
        return
    
    # function to log the internal event, the system time, and the logical clock value.
    def log_event(self, action, recipient=None):
        # add to the log file the action to the recipient 
        formatted_message = action + '_' + recipient + ' , ' + self.logical_clock
        # call on the logger to log the action into the log file
        self.log.info(formatted_message)
        return formatted_message


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

            action = random.randint(1, 10)

            if action == 1 or action == 2:
                recipient_username = self.other_machines[action - 1]
                self.send_clock_message(host, port, self.clock_time, recipient_username)
                self.log_event('SEND', recipient_username)

            elif action == 3:
                recipient_one_username = self.other_machines[0]
                recipient_two_username = self.other_machines[1]
                
                self.send_clock_message(host, port, self.clock_time, recipient_one_username)
                self.log_event('SEND', recipient_one_username)

                self.send_clock_message(host, port, self.clock_time, recipient_two_username)
                self.log_event('SEND', recipient_two_username)
                
            else: 
                self.update_local_logical_clock()
                self.log_event('INTERNAL')

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