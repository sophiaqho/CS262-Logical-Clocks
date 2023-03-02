"""
Run  `python3 test_server.py`

Instructions: 
Once this file has printed 'Server is active'. 

In two separate terminals, run `python3 run_client.py` and create an account in each terminal.
We will use that to test the server-client interactions.

Instruction: when prompted for a password, enter 'hi'.
Needed to test the login function.

READ CAREFULLY, take your time. 
You can ignore the unclosed socket.socket warning :) 

"""

import os
import socket
import math
import time
import uuid
import unittest
from server import Server
from client import ClientSocket

# https://docs.python.org/2/library/unittest.html from section 25.3.1 
# Adapted from section 25.3.4

set_port = 8889
set_host = ''

class SimpleServerTestCase(unittest.TestCase):
    # create only one instance to avoid multiple instantiations
    @classmethod
    def setUpClass(self):
        self.server_instance = Server()

        #set up host, port, create connection
        self.server_instance.server.bind((set_host, set_port))
        print('Server is active.')

        # accept incoming connections
        self.server_instance.server.listen()

        self.client_socket = ClientSocket()
        self.client_socket.client.connect((set_host, set_port))

        self.conn, self.addr = self.server_instance.server.accept()

    def tearDown(self):
        #conn.close()
        print('shut downwnn')
    
    # testing the create username function
    def test_create_account(self):
       # test create- see if the username is properly created
        print("Testing the CREATE function")

        # call on the server's create username function
        created_username = self.server_instance.create_username(set_host, set_port, self.conn)

        # the expected username value for the created username
        expected_username = "1"

        # check that the created username matches the expected username value
        self.assertEqual(expected_username, created_username)

    # testing the is_username_valid function on a valid username
    def test_is_username_valid(self):
        print("Testing the IS_USERNAME_VALID function on a valid input")
        # create a variable to store a valid/existing username
        valid_username = "1"
        print("HEHLLO0000", self.server_instance.account_list)

        # call on the server's is_username_valid function
        is_username_valid_output = self.server_instance.is_username_valid(valid_username)

        # check that the is_username_valid outputs True because the username is valid
        self.assertEqual(is_username_valid_output, True)


    # testing the is_username_valid function on an invalid username
    def test_is_username_invalid(self):
        print("Testing the IS_USERNAME_VALID function on an invalid input")
        # create a variable to store a valid/existing username
        invalid_username = "8"

        # call on the server's is_username_valid function
        is_username_valid_output = self.server_instance.is_username_valid(invalid_username) 

        # check that the is_username_valid outputs False because the username is invalid
        self.assertEqual(is_username_valid_output, False)

    # NOTE: We do not test the add_message_to_queue function because this function
    # is calling upong the is_username_valid function and the addMessages function, 
    # both of which are already covered in our unit tests. 

    # NOTE: We do not test the deliver_message function because this function
    # is calling upong the add_message_to_queue function which has already been covered 
    # in our other unit test cases. 
        
    # NOTE: We do not test the send_client_messages function because this function
    # requires client integration and it just calls on the getFirstMessage function
    # on the Client code. This function has already been covered in our Client 
    # unit test cases. 

    # # testing the add_message_to_queue function for a valid recipient
    # def test_add_message_to_queue_valid(self):
    #     print("Testing the ADD_MESSAGE_TO_QUEUE function on a valid recipient")
    #     # create a variable to store a valid/existing username
    #     machine_username = "1"
    #     message = "[we, <3, cs262]"
    #     print("HEHLLO", self.server_instance.account_list)

    #     # call on the server's add_message_to_queue function
    #     add_message_output = self.server_instance.add_message_to_queue(machine_username, machine_username, message)

    #     # check that the add_message_to_queue outputs True because the recipient is valid
    #     self.assertEqual(add_message_output, True)


    # testing the add_message_to_queue function for a valid recipient
    def test_add_message_to_queue_invalid(self):
        print("Testing the ADD_MESSAGE_TO_QUEUE function on an invalid recipient")
        # create a variable to store a valid/existing username
        sender_username = "1"
        recipient_username = "8"
        message = "[we, <3<3, cs262]"

        # call on the server's is_username_valid function
        add_message_output = self.server_instance.add_message_to_queue(sender_username, recipient_username, message)

        # check that the add_message_to_queue outputs False because the recipient is invalid
        self.assertEqual(add_message_output, False)



       
if __name__ == '__main__':
    unittest.main()
