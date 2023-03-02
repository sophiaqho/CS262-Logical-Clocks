"""
Configuration (BEFORE RUNNING `python3 test_client.py`)
In a separate terminal run `python3 run_server.py` and wait for 'Server is active'.

Now, run `python3 test_client.py` in another terminal. 

"""

import os
import socket
import math
import time
import uuid
import uuid
import unittest
from client import ClientSocket
from server import Server

set_port = 8889
set_host = ''

# https://docs.python.org/2/library/unittest.html from section 25.3.1 

class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client_socket = ClientSocket()
        host = set_host
        port = set_port

        self.client_socket.client.connect((host, port))

    # def tearDown(self):
        # self.client_socket.client.close()

    # testing the create machine client username function
    def test_create_machine_username(self):
        # test create- see if the username + password are properly updated
        print("Testing the CREATE USERNAME function")
        # creating the test user client account
        created_username = self.client_socket.create_client_username(set_host, set_port)
        # checking that the created username is equal to teh expected username
        self.assertEqual(created_username, self.client_socket.getUsername())

    # testing the message parsing function
    def test_parse_live_message(self):
        print("Testing the PARSE LIVE MESSAGE function")
        # create a message to be parsed
        # message will be formatted as `SenderUsername/time1/time2/time3_length`
        message = "1/2/3/2_2"

        # call the parse message function on our test message
        sender_username, logical_clock_vector, remaining_messages = self.client_socket.parse_live_message(message)
       
        # define variables for what we expect `parse_live_message` to return 
        expected_sender_username = "1"
        expected_logical_clock_vector = [2, 3, 2]
        expected_remaining_messages = "2"

        # see if the message was parsed as expected
        self.assertEqual(expected_sender_username, sender_username)
        self.assertEqual(expected_logical_clock_vector, logical_clock_vector)
        self.assertEqual(expected_remaining_messages, remaining_messages)

    # testing the message parsing function on invalid message input
    def test_parse_live_message_invalid_input(self):
        print("Testing the PARSE LIVE MESSAGE function")
        # create an message to be parsed
        # message will be formatted as `SenderUsername/time1/time2/time3_length_length`
        message = "1/2/3/2_2_2"
       
        # see if the function raises an error
        self.assertRaises(NameError, self.client_socket.parse_live_message, message)

    # testing the message parsing function on invalid logical clock input
    def test_parse_live_message_invalid_clock(self):
        print("Testing the PARSE LIVE MESSAGE function")
        # create an invalid message to be parsed
        # message will be formatted as `SenderUsername/time1/time2/time3/time4_length`
        message = "1/2/3/3/2_2"

        # see if the function raises an error on the invalid logical clock
        self.assertRaises(NameError, self.client_socket.parse_live_message, message)

    # testing the add message function
    def test_add_message(self):
        print("Testing the ADD MESSAGE function")
        # create a dummy message to add to the queue
        message = "[clock1, clock2, clock3]"

        # creating the test user
        # self.client_socket.create_client_username(set_host, set_port)
        self.client_socket.addMessage(message)
        
        # getting the queue of all messages
        list_of_messages = self.client_socket.messages
        
        # checking if the test message exists in the message queue
        is_in_message_list = message in list_of_messages
        self.assertEqual(is_in_message_list, True)


    # testing the get messages function
    def test_get_messages(self):
        print("Testing the GET MESSAGES function")
        # create a dummy message to add to the queue
        message = "[1, 2, 3]"

        # creating the test user
        # self.client_socket.create_client_username(set_host, set_port)
        self.client_socket.addMessage(message)
        
        # getting the queue of all messages
        list_of_messages = self.client_socket.getMessages()
        
        # checking if the test message exists in the message queue
        is_in_message_list = message in list_of_messages
        self.assertEqual(is_in_message_list, True)


    # testing the function that updates a machines local logical clock on an EXTERNAL event
    def test_update_logical_clock_external(self):
        # set the local logical clock vector so we can test updating it
        self.client_socket.logical_clock = [0, 0, 0]

        # pass in a dummy logical clock to the function that is received from another machine
        updated_logical_clock = self.client_socket.update_local_logical_clock([2, 3, 4])

        # this is the expected values of the logical clock vector
        expected_logical_clock = [3, 3, 4]

        # check that the function returns the correctly updated local logical clock
        self.assertEqual(expected_logical_clock, updated_logical_clock)

    # testing the function that updates a machines local logical clock on an INTERNAL event
    def test_update_logical_clock_internal(self):
        # get the value of the current local logical clock vector so we can test updating it
        cur_clock = self.client_socket.logical_clock_time 
        
        # this is the expected values of the logical clock vector after it gets updated
        expected_logical_clock = [cur_clock[0] + 1, cur_clock[1], cur_clock[2]]

        # call the update logical clock function for an internal event
        updated_logical_clock = self.client_socket.update_local_logical_clock()

        # check that the function returns the correctly updated local logical clock
        self.assertEqual(expected_logical_clock, updated_logical_clock)

    # testing the get first message function on empty message queue
    def test_get_first_message(self):
        # set the message queue to be empty for this test
        self.client_socket.messages = ["[we, love, cs262]", "[we, rly_love, cs262]"]

        # call on the receive messages function when the message queue is empty
        received_message_output, received_length = self.client_socket.getFirstMessage()

        # expected output of the function on an empty queue
        expected_output, expected_queue_length = "[we, love, cs262]", 1

        # check that the function output matches the expected output
        self.assertEqual(expected_output, received_message_output)
        self.assertEqual(expected_queue_length, received_length)

    # testing the get first message function on empty message queue
    def test_get_first_message_empty(self):
        # set the message queue to be empty for this test
        self.client_socket.messages = []
        # call on the receive messages function when the message queue is empty
        received_message_output, received_length = self.client_socket.getFirstMessage()

        # expected output of the function on an empty queue
        expected_output, expected_queue_length = "No messages available", 0

        # check that the function output matches the expected output
        self.assertEqual(expected_output, received_message_output)
        self.assertEqual(expected_queue_length, received_length)

    # testing the function that updates a machines local logical clock on an INTERNAL event
    def test_send_clock_messages_invalid_recipient(self):
        # create an invalid recipient username
        invalid_machine_username = "8"
        # clear messages to ensure you are able to send a message
        # there may be some issue here with optionality ?
        self.client_socket.messages = []

        # pass in the invalid username to the send_clock_message function
        send_clock_message_output = self.client_socket.send_clock_message(set_host, set_port, invalid_machine_username)
        # the send_clock_message should return False on an invalid user
        # checks that the function correctly returns False
        self.assertEqual(send_clock_message_output, False)

    # TODO add send message to valid username function (send message to itself)

    # testing the receive message function on empty queue
    def test_receive_empty_message(self):
        # set the message queue to be empty for this test
        self.client_socket.messages = []
        # call on the receive messages function when the message queue is empty
        receive_message_output = self.client_socket.receive_messages(set_host, set_port)

        expected_output = "No messages available" + "_" + "0"

        # check that the function output matches the expected output
        self.assertEqual(expected_output, receive_message_output)

    # TODO add receive valid message function


    # testing the log events function
    def test_log_internal_event(self):
        # create expected output string for the log function
        expected_output_string = 'ACTION: ' + "INTERNAL" + ", Logical Clock Time: " + "[" + str(self.client_socket.logical_clock_time[0]) + ", " + str(self.client_socket.logical_clock_time[1]) + ", " + str(self.client_socket.logical_clock_time[2]) + "]"

        # call on the log event function on an INTERNAL event
        log_event_output = self.client_socket.log_event("INTERNAL")

        # check that the function returns the correctly updated local logical clock
        self.assertEqual(expected_output_string, log_event_output)


    # testing the log events function
    def test_log_external_event_receive_message(self):
        # create expected output string for the log function
        expected_output_string = 'ACTION: ' + "RECEIVE" + ", Logical Clock Time: " + "[" + str(self.client_socket.logical_clock_time[0]) + ", " + str(self.client_socket.logical_clock_time[1]) + ", " + str(self.client_socket.logical_clock_time[2]) + "]" + ', # of remaining messages: ' + "2"

        # call on the log event function on an INTERNAL event
        log_event_output = self.client_socket.log_event("RECEIVE", num_remaining_messages="2")

        # check that the function returns the correctly updated local logical clock
        self.assertEqual(expected_output_string, log_event_output)


    # testing the log events function
    def test_log_event_send_message(self):
        # create expected output string for the log function
        expected_output_string = 'ACTION: ' + "SEND" + ', Recipient Machine: ' + "2" + ", Logical Clock Time: " + "[" + str(self.client_socket.logical_clock_time[0]) + ", " + str(self.client_socket.logical_clock_time[1]) + ", " + str(self.client_socket.logical_clock_time[2]) + "]"

        # call on the log event function on an INTERNAL event
        log_event_output = self.client_socket.log_event("SEND", recipient="2")

        # check that the function returns the correctly updated local logical clock
        self.assertEqual(expected_output_string, log_event_output)


if __name__ == '__main__':
    # run unit tests
    unittest.main()