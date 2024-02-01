import unittest

from unittest.mock import patch
from KeyServer import KeyServer

class TestKeyServer(unittest.TestCase):
    
    def setUp(self):
        self.keyServer = KeyServer()


    def tearDown(self):
        self.keyServer.server_socket.close()


    def test_client_add_request(self):
        request_message = '{"type": "ADD", "port": "8001", "public_key": [1, 2, 3]}'
        expected_response = '{"status": "CREATED", "message": "Public key stored"}'

        with patch('KeyServer.socket.socket', autospec=True) as mock_socket:
            mock_socket.recv.return_value = request_message.encode()

            response = self.keyServer.process_client_message(request_message, '123')

        self.assertEqual(response, expected_response)

    
    def test_client_get_request(self):
        request_message = '{"type": "GET", "port": "8001"}'
        self.keyServer.public_keys = {'8001': [1, 2, 3]}

        expected_message = '{"status": "OK", "message": [1, 2, 3]}'

        with patch('KeyServer.socket.socket', autospec=True) as mock_socket:
            mock_socket.recv.return_value = request_message.encode()

            response = self.keyServer.process_client_message(request_message, '123')

        self.assertEqual(response, expected_message)


    def test_client_key_not_found(self):
        request_message = '{"type": "GET", "port": "8002"}'

        expected_message = '{"status": "NOT_FOUND", "message": "Client not found"}'

        with patch('KeyServer.socket.socket', autospec=True) as mock_socket:
            mock_socket.recv.return_value = request_message.encode()

            response = self.keyServer.process_client_message(request_message, '123')

        self.assertEqual(response, expected_message)