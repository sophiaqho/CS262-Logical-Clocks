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

set_port = 8888
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

    # # testing the function that updates a machines local logical clock on an INTERNAL event
    # def test_send_clock_messages_invalid_recipient(self):
    #     # create an invalid recipient username
    #     invalid_machine_username = "8"

    #     # pass in the invalid username to the send_clock_message function
    #     send_clock_message_output = self.client_socket.send_clock_message(set_host, set_port, invalid_machine_username)
    #     # the send_clock_message should return False on an invalid user
    #     # checks that the function correctly returns False
    #     self.assertEqual(send_clock_message_output, False)

    # testing the receive message function 

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


    # # testing our create account function
    # def test_create_account(self):
    #     # test create- see if the username + password are properly updated
    #     print("Testing the CREATE function")
    #     # creating the test user client account
    #     created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     self.assertEqual(created_username, self.client_socket.getUsername())
    #     self.assertEqual(expected_password, self.client_socket.getPassword())

       
    # # testing our login account function
    # def test_login_account(self):
    #     print("Testing the LOGIN function")
    #     # test will only pass if you enter the correct password- try it out!
    #     # want to exit out of the account to see whether that works
    #     # creating the test user client account
    #     created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     print("Username is:", created_username)
    #     # log out of the account
    #     self.client_socket.client.send('exit'.encode())

    #     # log into the account
    #     username_logged_into = self.client_socket.login_client_account("login", set_host, set_port, usrname_input=created_username, pwd_input=expected_password)
    #     self.assertEqual(created_username, username_logged_into)

    # # testing logging into an account with an incorrect password
    # def test_incorrect_login_password(self):
    #     print('Testing the LOGIN function - incorrect password')
    #     # test will only pass if you enter an incorrect password- try it out!
    #     # want to exit out of the account to see whether that works
    #     # creating the test user client account
    #     created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     print("Username is:", created_username)
    #     # log out of the account
    #     self.client_socket.client.send('exit'.encode())

    #     # fail the log attempt into the account
    #     login_status, _ = self.client_socket.send_login_information("login", set_host, set_port, usrname_input=created_username, pwd_input="h")
    #     self.assertEqual(login_status, False)

    # # testing logging into an account with an incorrect username
    # def test_incorrect_login_username(self):
    #     print('Testing the LOGIN function - incorrect username')
    #     # test will only pass if you enter an incorrect password- try it out!
    #     # want to exit out of the account to see whether that works
    #     # creating the test user client account
    #     created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     print("Username is:", created_username)
    #     # log out of the account
    #     self.client_socket.client.send('exit'.encode())

    #     # fail the log attempt into the account
    #     login_status, _ = self.client_socket.send_login_information("login", set_host, set_port, usrname_input="bogus_username", pwd_input=expected_password)
    #     self.assertEqual(login_status, False)

    # # testing exiting/logging out from your account
    # def test_exit_account(self):
    #     print('Testing the EXIT function')
    #     # assert that after we have created an account, we can successfully log out/exit.
    #     self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     self.assertEqual(self.client_socket.client_exit(), True)

    # # testing deleting your account
    # def test_delete_account(self):
    #     print("Testing the DELETE function")
    #     # assert that after we have created an account, it is deleted (returns True)
    #     # creating the test user client account
    #     self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     self.assertEqual(self.client_socket.delete_client_account(set_host, set_port), True)
    
    # # testing sending messages yourself
    # def test_send_messages_to_self(self):
    #     print("Testing the SEND MESSAGE function to yourself. ")
    #     # create a new user
    #     sender_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     # send message to yourself
    #     confirmation_from_server = self.client_socket.send_message(sender_username, set_host, set_port, msg_content=msg_content)
    #     # see if the message was delivered as expected
    #     expected_confirmation = "Delivered message '" + msg_content + " ...' to " + sender_username + " from " + sender_username
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    # # testing recieving messages from yourself
    # def test_receive_messages_to_self(self):
    #     print("Testing the RECEIVE MESSAGE function to yourself.")
        
    #     # create a new test user
    #     curr_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        
    #     # send message to yourself
    #     self.client_socket.send_message(curr_username, set_host, set_port, msg_content=msg_content)
        
    #     # see if the message is received from the server
    #     confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
    #     expected_confirmation = "we_love_cs262" + curr_username + "abc"
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    # # testing sending messages to another account
    # def test_send_messages_to_others(self):
    #     print("Testing the SEND MESSAGE function to another client.")
    #     # creating the test user client account
    #     sender_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     time.sleep(1)

    #     # make other client
    #     other_client = ClientSocket()
    #     other_client.client.connect((set_host, set_port))
    #     other_username = other_client.create_client_username(set_host, set_port, pwd_client=expected_password)
       
    #     # comparing the confirmation from the server with expected confirmation
    #     confirmation_from_server = self.client_socket.send_message(other_username, set_host, set_port, msg_content=msg_content)
    #     expected_confirmation = "Delivered message '" + msg_content + " ...' to " + other_username + " from " + sender_username
    #     self.assertEqual(confirmation_from_server, expected_confirmation)
    #     # exit other socket
    #     other_client.client_exit()

    # # testing receiving messages from another account
    # def test_receive_messages_from_others(self):
    #     print("Testing the RECEIVE MESSAGE function to another client.")
    #     # creating the test user client recipient
    #     recipient_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     time.sleep(1)

    #     # make other client
    #     other_client = ClientSocket()
    #     other_client.client.connect((set_host, set_port))
    #     other_username = other_client.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     # send message to recipient
    #     other_client.send_message(recipient_username, set_host, set_port, msg_content=msg_content)
    #     time.sleep(1)

    #     # confirmation you expect to receive from the server
    #     confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
    #     expected_confirmation = "we_love_cs262" + other_username + "abc"
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    #     # exit other socket
    #     other_client.client_exit()

    # # testing sending messages to an account that does not exist
    # def test_send_messages_to_nonexistent_user(self):
    #     print("Testing the SEND MESSAGE function to a nonexistent client username.")
    #     # creating the test user client account to send messages from
    #     self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     time.sleep(1)

    #     # create nonexistent client username
    #     nonexistent_username = "nonexistent_client_username"

    #     # expected confirmation from the server
    #     confirmation_from_server = self.client_socket.send_message(nonexistent_username, set_host, set_port, msg_content=msg_content)
    #     expected_confirmation = "User not found."
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    # # testing receiving messages with no available messages
    # def test_receive_empty_messages(self):
    #     print("Testing the RECEIVE MESSAGE function with no available messages.")
    #     # creating the test user client account to get messages for
    #     self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
    #     time.sleep(1)

    #     # confirmation you expect to receive 
    #     confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
    #     expected_confirmation = "No messages available"
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    # # testing the view all accounts function
    # def test_view_account_list(self):
    #     print("Testing the VIEW ACCOUNTS function")
    #     # creating the test user
    #     self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        
    #     # getting the list of all accounts 
    #     list_of_accounts = self.client_socket.list_accounts("listaccts", set_host, set_port)
        
    #     # checking if the test user exists in the account list
    #     is_in_account_list = self.client_socket.getUsername() in list_of_accounts
    #     self.assertEqual(is_in_account_list, True)


if __name__ == '__main__':
    # set up the server once. This did not work, so you must run the run_server.py file separately.
    # server_instance = Server()
    # server_instance.server.bind((set_host, set_port))
    # server_instance.server.listen()
    # #conn, addr = server_instance.server.accept()
    unittest.main()