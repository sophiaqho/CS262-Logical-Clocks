import os
import socket
import math
import time
from datetime import datetime
import random
import logging

set_port = 8888
set_host = ''


class ClientSocket:

    def __init__(self, client=None):
        # We store if the client is currently logged in (to see if they have permission to
        # send/receive messages), their username, and 
        # queue of messages that they have received.

        self.username = ''
        self.messages = []
        self.logical_clock_time = [0] * 3
        self.other_machines = ['1', '2', '3']
        self.logname = "Process"
        self.log = None

        self.time_breakdown = random.randint(1, 6)
        
        if client is None:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.client = client


    # basic get/set functions to allow for the server to update these values

    def getUsername(self):
        return self.username

    def getMessages(self):
        return self.messages

    # returns the first message in the message queue and removes it from the queue
    def getFirstMessage(self):
        if self.messages:
            return self.messages.pop(0), len(self.messages)
        return "No messages available", 0
    
    def addMessage(self, message_string):
        self.messages.append(message_string)


    # Function to create a new account
    # returns the client username
    def create_client_username(self, host, port):
        # message contains 'create'- send this to the server
        # so the server runs the create function

        self.client.sendto('create'.encode(), (host, port))

        # server will send back a username (UUID)
        data = self.client.recv(1024).decode()

        # Update ClientSocket object username and log in fields
        self.username = str(data)
        self.other_machines.remove(self.username)

        # create a logger file name and use that name to create the log file for this user
        self.logname = "Process" + self.username + "_" + str(datetime.now()) + ".txt"
        logging.basicConfig(
            filename=self.logname,
            format='%(asctime)s,%(msecs)03d, %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.INFO)

        self.log = logging.getLogger(__name__)
        
        print('Your unique username is '  + data)

        return self.getUsername()


    # helper function to parse messages as everything is sent as strings
    # return is of the format (sender username, logical clock time, 
    # length of remaining messages in queue)
    def parse_live_message(self, message):
        # message format is `SenderUsername/time1/time2/time3_length`
        # username is 1 characters total (fixed length)
        parsed_message = message.split("_")
        
        # get the string of the new logical clock received from the server
        # the format of this variable will be `time1/time2/time3`
        received_logical_clock = parsed_message[0][2:]

        # parse the string of the received logical clock to be split by "/"
        logical_clock_vector = received_logical_clock.split("/")

        # convert each string in the array to an int of the logical clock time
        logical_clock_vector = [int(x) for x in logical_clock_vector]

        # return the sender username, logical clock timestamp, number of remaining messages
        return (parsed_message[0][0], logical_clock_vector, parsed_message[1])


    # function to print all available messages
    # returns the # of messages delivered
    def deliver_first_msg(self, received_msg):
        # We want to parse the recieved message to get the logical time clock
        # and the length of the remaining message queue
        sender_username, logical_clock_vector, length = self.parse_live_message(received_msg)

        # print the logical clock timestamp message from the sender machine
        print("Logical clock timestamp from machine #" + sender_username + ":", logical_clock_vector)
        # print the number of messages left in the queue
        print("Number of unread messages: " + str(length))
        
        return logical_clock_vector, length

    
    # function used to send a message to another user!/yourself!
    # returns True if message was delivered
    # False otherwise
    # sends to one of the other machine or two machines a message that is the local logical clock time
    def send_clock_message(self, host, port, recipient_username):
        # format the logical clock vector into a string where each machines logical clock is separated by a `/`.
        logical_clock_string = '/' + str(self.logical_clock_time[0]) + '/' + str(self.logical_clock_time[1]) + '/' + str(self.logical_clock_time[2])
        
        # send the formatted vector clock as a string to the server along with the sender machine and the recipient machine
        self.client.sendto(('sendmsg' + self.getUsername() + recipient_username + logical_clock_string).encode(), (host, port))
        
        # receive confirmation from the server that it was delivered or error message elsewhere
        data = self.client.recv(1024).decode()

        # print to see whether it was sent successfully
        print(data)

        # return True if sent was successful, False if it was unsuccessful
        return data != "Message could not be delivered. Please try again."

    
    # function used to receive messages from the server
    # returns available messages
    def receive_messages(self, host, port):
        # inform server that you want to get new messages
        self.client.sendto('msgspls!'.encode(), (host, port))

        # server will send back messages of proper length
        data = self.client.recv(128).decode()

        return data


    def client_exit(self):
        print(f'Connection closed.')
        self.client.close()
        self.logged_in = False
        return True
    

    # function to update the local logical clock 
    def update_local_logical_clock(self, received_logical_clock=None):
        # get the index of the current machine so we can increment the logical clock of the local machine
        curr_machine = int(self.getUsername()) - 1

        # if we have received a logical clock time then we know that it is not an internal event
        # this update the logical clock vector for the non internal event cases
        if received_logical_clock:
            for i, _ in enumerate(self.logical_clock_time):
                self.logical_clock_time[i] = max(self.logical_clock_time[i], received_logical_clock[i])
            # increment the logical clock value for the local component
            self.logical_clock_time[curr_machine] += 1

        # this update the logical clock vector for the internal event cases
        else:
            # increment the logical clock value for the local component
            self.logical_clock_time[curr_machine] += 1
        
        # return the new updated local logical clock vector
        return self.logical_clock_time
    

    # function to log the internal event, the system time, and the logical clock value.
    def log_event(self, action, recipient=None, num_remaining_messages=None):
        # create string variables for common strings that are used multiple times in our logs
        action_string = 'ACTION: '
        logical_clock_string = ' , Logical Clock Time: '
        # convert the logical clock vector to a string containing each vector value in the format `[clock1, clock2, clock3]`
        logical_clock_vector = "[" + str(self.logical_clock_time[0]) + ", " + str(self.logical_clock_time[1]) + ", " + str(self.logical_clock_time[2]) + "]"

        # add to the log file the appropriate log depending on the input to the log_event function
        if num_remaining_messages:
            formatted_message = action_string + action + logical_clock_string + logical_clock_vector + ' , # of remaining messages: ' + str(num_remaining_messages)
        elif recipient:
            formatted_message = action_string + action + ', Recipient Machine: ' + recipient + logical_clock_string + logical_clock_vector
        else:
            formatted_message = action_string + action + logical_clock_string + logical_clock_vector

        # call on the logger to log the action into the log file
        # the log is in the format: `Global time action_recipientMachine, logical_clock, number of remaining messages`
        self.log.info(formatted_message)
        return formatted_message


    # this is the main client program that we run- it calls on all subfunctions
    def client_program(self):
        host = set_host
        port = set_port

        self.client.connect((host, port))

        # handle initial information flow- either will login or create a new account
        # You need to either log in or create an account first

        self.create_client_username(host, port)
        
        # can only enter loop if you are logged in
        while True:
            # once initialized, carry out an action every 1/time_initialized seconds
            time.sleep(1/self.time_breakdown)
            # get the first available message that has been sent to this machine
            received_msg = self.receive_messages(host, port)

            print("HI IM HERE", received_msg)
            if received_msg[:21] != 'No messages available':
                # deliver the first available message if there is one
                received_logical_clock, num_remaining_messages = self.deliver_first_msg(received_msg)
                print("HI IM HERE 2", received_logical_clock, num_remaining_messages)

                # update the local logical clock for this machine
                self.update_local_logical_clock(received_logical_clock)

                # log the deliver message event in the log file
                self.log_event('RECEIVE', num_remaining_messages=num_remaining_messages)

            else:
                # randomly generate a number between 1 and 10 to be our machine's action
                action = random.randint(1, 10)

                # if the action is 1 or 2, send the logical clock message to one of the other machines
                if action == 1 or action == 2:
                    recipient_username = self.other_machines[action - 1]
                    self.send_clock_message(host, port, recipient_username)

                    # update the local logical clock for this machine
                    self.update_local_logical_clock()

                    # log the event in the log file
                    self.log_event('SEND', recipient=recipient_username)

                # if the action is 3, send the logical clock message to both of the other machines
                elif action == 3:
                    recipient_one_username = self.other_machines[0]
                    recipient_two_username = self.other_machines[1]
                    
                    self.send_clock_message(host, port, recipient_one_username)

                    # update the local logical clock for this machine
                    self.update_local_logical_clock()

                    # log the event in the log file
                    self.log_event('SEND', recipient=recipient_one_username)

                    self.send_clock_message(host, port, recipient_two_username)

                    # update the local logical clock for this machine
                    self.update_local_logical_clock()

                    # log the event in the log file
                    self.log_event('SEND', recipient=recipient_two_username)
                    
                else: 
                    # update the local logical clock for this machine
                    self.update_local_logical_clock()

                    # log the event in the log file
                    self.log_event('INTERNAL')

            # # will only exit while loops on 'exit' or 'delete'
            # # read undelivered messages for exit
            # if message.strip() == 'exit':
                # self.client_exit()

# program creates a ClientSocket object and runs client_program which
# handles input and directs it to the appropriate function
if __name__ == '__main__':
    socket = ClientSocket()
    socket.client_program()