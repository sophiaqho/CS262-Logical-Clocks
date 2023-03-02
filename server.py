import os
import socket
import math
import time
from _thread import *
import threading
from client import ClientSocket
import sys

set_port = 8888
set_host = ''

class Server:
    curr_user = ''
    
    # Server object
    def __init__(self, sock=None):
        # Create a list of accounts for this server to keep track of clients
        # Format of account_list is [UUID: ClientObject]
        self.account_list = dict()
        # Mutex lock so only one thread can access account_list at a given time
        # Need this to be a Recursive mutex as some subfunctions call on lock on 
        # top of a locked function
        self.account_list_lock = threading.RLock()

        if sock is None:
            self.server = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock

    # Returns true if the username exists in the account_list database,
    # false otherwise.
    def is_username_valid(self, recipient_username):
        # lock mutex as we access account_list
        self.account_list_lock.acquire()
        result = recipient_username in self.account_list
        # unlock mutex
        self.account_list_lock.release()
        return result


    # Function to add the message to the recipient's queue
    def add_message_to_queue(self, sender_username, recipient_username, message):
        # checks if the recipient machine username is valid, returns False if not so we can throw an error later
        if not self.is_username_valid(recipient_username):
            return False
        # queue format is strings of sender_username + "" + message
        message_string = sender_username + message
        # lock mutex
        self.account_list_lock.acquire()
        self.account_list.get(recipient_username).addMessage(message_string)
        # unlock mutex
        self.account_list_lock.release()
        return True

    # NOTE: modified from initial function bc we feed in message now too
    # so there is less back & forth.
    # returns True upon successful message delivery. returns False if it fails.
    def deliver_message(self, sender_username, recipient_username, message, host, port, conn):
        # regardless of client status (logged in or not), add the message to the recipient queue
        if self.add_message_to_queue(sender_username, recipient_username, message):
            # print + deliver confirmation
            confirmation_message_sent = "Delivered message '" + message[:50] + " ...' to " + recipient_username + " from " + sender_username
            print(confirmation_message_sent)
            conn.sendto(confirmation_message_sent.encode(), (host, port))
            return True
        
        # if the message did not deliver, deliver an error message
        else:
            message_did_not_work = "Message could not be delivered. Please try again."
            print(message_did_not_work)
            conn.sendto(message_did_not_work.encode(), (host, port))
            return False


    # function to create an account/username for a new user
    # returns the username created
    def create_username(self, host, port, conn):

        # server will generate username, 
        # add account information to the dictionary,
        # print username + then send info to client

        # lock mutex
        self.account_list_lock.acquire()

        # username is length of account_list + 1
        username = str(len(self.account_list) + 1)

        # add (username: clientSocket object where clientSocket includes log-in status,
        # username, and queue of undelivered messages
        self.account_list[username] = ClientSocket()

        # unlock mutex
        self.account_list_lock.release()
        
        print("Unique username generated for client is "+ username + ".")
        conn.sendto(username.encode(), (host, port))

        return username

    # send messages to the client that are in the client's message queue
    # returns what messages are sent over
    def send_client_messages(self, client_username, host, port, conn):
        # note that we hold the mutex in this entire area- if we let go of mutex + reacquire to
        # empty messages we may obtain new messages in that time and then empty messages
        # that have not yet been read

        # lock mutex
        self.account_list_lock.acquire()
    
        # get the first available message and the length of the remaining queue
        logical_clock_time, length = self.account_list.get(client_username).getFirstMessage()

        # unlock mutex
        self.account_list_lock.release()

        # parse the first message containing the logical clock time with the length of the queue
        # so we can send it to the client and the client can log it
        msg = logical_clock_time + '_' + str(length)

        # send over the message with the logical clock time and the messages queue length
        conn.sendto(msg.encode(), (host, port))

        return msg


# function that does the heavy lifting of server, client communication
    # this function returns nothing, exits only when the Client closes
    def server_to_client(self, host, conn, port):
        
        # keep track of the current client on this thread
        curr_user = ''

        # while statement only breaks when client deletes their account
        # or if client exits on their side (closes connection)
        while True:
            # receive from client
            data = conn.recv(1024).decode()
            
            # check if connection closed- if so, close thread
            if not data:
                # close thread
                return

            print('Message from client ' + curr_user + ': ' + data)

            # check if data equals 'create'
            if data.lower().strip()[:6] == 'create':
                curr_user = self.create_username(host, port, conn)

                # make the server sleep until at least three machiens are connected 
                # to the server
                # prevents the issue of one machine trying to send messages 
                # to a machine that doesn't exist yet
                if not_testing: 
                    while len(self.account_list) < 3:
                        # make the server sleep for a time that is the LCM of 1 through 6 
                        # because we can carry out 1 through 6 opertions per second
                        time.sleep(1/10)

            # check if client request to send a message
            elif data.lower().strip()[:7] == 'sendmsg':
                # data parsing works correctly
                # print(data, data.strip()[7], data.strip()[8], data.strip()[9:])
                # client username, recipient username, message, host, port, conn
                self.deliver_message(data.strip()[7], data.strip()[8], data.strip()[9:], host, port, conn)

            # check if client request is to get available messages
            elif data[:8] == "msgspls!":
                self.send_client_messages(curr_user, host, port, conn)


    # this program sets up the server + creates new threads for clients      
    def server_program(self):
        host = set_host
        port = set_port
        self.server.bind((host, port))
        self.server.listen()
        print('Server is active')

        # while SOMETHING, listen!
        while True:
            conn, addr = self.server.accept()

            print(f'{addr} connected to server.')

            # Start a new thread with this client
            curr_thread = threading.Thread(target=self.server_to_client, args=(host, conn, port,))
            curr_thread.start()

# create a server object and run the server program!
if __name__ == '__main__':
    a = Server()
    not_testing = (len(sys.argv) == 1)
    a.server_program()
