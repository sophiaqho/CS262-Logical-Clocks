import os
import socket
import math
import time
import uuid
from _thread import *
import threading
from run_client import ClientSocket

set_port = 8887
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
        result =  recipient_username in self.account_list
        # unlock mutex
        self.account_list_lock.release()
        return result


    # Function to add the message to the recipient's queue
    def add_message_to_queue(self, sender_username, recipient_username, message):
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
        # If username is invalid, throw error message
        # We do NOT need to know who the sender is- only recipient because
        # recipient will increment their VC
        # if not self.is_username_valid(recipient_username): 
        #     recipient_not_found = "User not found."
        #     print(recipient_not_found)
        #     conn.sendto(recipient_not_found.encode(), (host, port))
        #     return False

        # # query the client for what the message is
        # confirmed_found_recipient = "User found. Please enter your message: "
        # print(confirmed_found_recipient)
        # conn.sendto(confirmed_found_recipient.encode(), (host, port))

        # server will receive what the message the client wants to send is 
        # message = conn.recv(1024).decode()

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
            conn.sendto(confirmation_message_sent.encode(), (host, port))
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
    def send_client_messages(self, client_username, host, port, conn, prefix=''):
        # prefix is appended to the FRONT of messages to be delivered 
        # prefix is an optional argument as everything is sent as strings
        # prefix is ONLY used in the login function to send conffirmation

        final_msg = ""
        # note that we hold the mutex in this entire area- if we let go of mutex + reacquire to
        # empty messages we may obtain new messages in that time and then empty messages
        # that have not yet been read

        # lock mutex
        self.account_list_lock.acquire()
    
        # get available messages
        msgs = self.account_list.get(client_username).getMessages()

        # if there are messages, append them to the final messages
        if msgs:
            str_msgs = ''
            for message in msgs:
                # this string divider was chosen because it would never be sent :)
                str_msgs += 'we_hate_cs262' + message
            final_msg += str_msgs

            # clear all delivered messages as soon as possible to address concurent access
            self.account_list.get(client_username).emptyMessages()
        else:
            final_msg += "No messages available" 
        # unlock mutex
        self.account_list_lock.release()

        # first send over the length of the message
        # SEND prefix + length of final msg- there is only a prefix for login 
        len_msg = prefix + str(len(final_msg))        
        conn.sendto(len_msg.encode(), (host, port))

        # TODO- see the timing of this with just senidng over one message
        # if at all 

        # receive back confirmation from the Client (this is to control info flow)
        confirmed = conn.recv(1024).decode()

        # then, send over the final message
        conn.sendto(final_msg.encode(), (host, port))

        return final_msg


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
    a.server_program()
