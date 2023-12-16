import socket
import sys
import threading
import argparse
import random

from typing import Union
from merkle_hellman_knapsack import MerkleHellmanKnapsack
from StreamCipher import StreamCipher
from utils import convert_list_of_int_to_string, generate_common_secret, convert_string_to_list_of_int

SERVER_HOST='localhost'
SERVER_PORT=8080
LISTEN_TIMEOUT=0.2
FIRST_START_RANGE=1
FIRST_END_RANGE=27
SECOND_END_RANGE=54
DECK_LENGTH=27

class Client:

    def __init__(self, port:int, host: str='localhost'):
        self.host: str = host
        self.port: int = port
        self.own_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.key_server_socket: socket.socket
        self.communication_socket: Union[None, socket.socket] = None
        self.merkleHermanKnapsack: MerkleHellmanKnapsack = MerkleHellmanKnapsack()
        self.streamCipher: StreamCipher
        
        self.private_key: tuple[tuple, int, int]
        self.public_key: bytes
        self.other_client_public: bytes
        self.other_client_port: int
        self.is_listening: bool = True

    def _handle_socket_error(self, message: str) -> None:
        message = f'> [ERROR] - Server socket error: {message}'
        print(message)


    def _clean_up_active_sockets(self):
        if self.own_socket:
            self.own_socket.close()
        
        if self.key_server_socket:
            self.key_server_socket.close()

        if self.communication_socket:
            self.communication_socket.close()


    def generate_keys(self) -> None:
        private_key = self.merkleHermanKnapsack.generate_private_key()
        public_key = self.merkleHermanKnapsack.generate_public_key(private_key)

        self.private_key = private_key
        self.public_key = public_key


    def decompose_key_server_message(self, message: str) -> str:
        status, response = message.split('#')

        return (status, response)
    

    def compose_key_server_request_messsage(self, type: str) -> str:
        message = f'{type}#{self.port}#{self.public_key}'

        return message
    

    def process_server_response(self, response: bytes) -> None: 
        decoded_response = response.decode()
        print(decoded_response)
        status, response_message = self.decompose_key_server_message(decoded_response)

        if status == 'ERROR' or status == 'NOT_FOUND':
            message = f'> [ERROR] - Error from KeyServer: {response_message}'
            print(message)
            self.key_server_socket.close()

            message = 'Stoping...'
            print(message)
            sys.exit()
    
        if status == 'CREATED':
            message = f'> [Client] - Public key stored: {response_message}'
            print(message)
            
        if status == 'OK':
            self.other_client_public = response_message

    
    def send_my_public_key(self):
        try:
            self.key_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.key_server_socket.connect((SERVER_HOST, SERVER_PORT))            

            message = self.compose_key_server_request_messsage('ADD')

            self.key_server_socket.sendall(message.encode())
            
            response = self.key_server_socket.recv(1024)
            self.process_server_response(response)
            self.key_server_socket.close()

        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()


    def send_public_key_request(self, port: int):
        try:
            message = f'GET#{port}'
            self.key_server_socket.sendall(message.encode())
        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()

    def get_other_client_public_key(self, port: int):
        try:
            self.key_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.key_server_socket.connect((SERVER_HOST, SERVER_PORT)) 
            self.send_public_key_request(port)

            response = self.key_server_socket.recv(1024)
            self.process_server_response(response)
            self.other_client_port = port

            self.key_server_socket.close()
        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()
    

    def get_peer_user_port_and_key(self) -> None:
        peer_port = int(input('\n> Please enter peer port: '))
        self.get_other_client_public_key(peer_port)


    def connect_to_other_client(self) -> None:
        try:
            self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.communication_socket.connect((SERVER_HOST, self.other_client_port))
        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()

    def start_listening(self) -> None:
        self.own_socket.bind((self.host, self.port))
        self.own_socket.listen(1)

        message = f'> [Client] - Listening on port: {self.port}'
        print(message)
        
        try:
            try:
                client_socket, addrs = self.own_socket.accept()
            except socket.error as e:
                self._handle_socket_error(e)
                sys.exit()

            message = f'> [Client] - Other client connected from address: {addrs}'
            print(message)

            if self.communication_socket is not None:
                self.communication_socket.close()

            self.communication_socket = client_socket
        
        except KeyboardInterrupt:
            self.own_socket.close()
            self.is_listening = False

    def connector_keypair_exchange(self) -> None:
        # First send handshake with my port
        message = f'HELLO#{self.port}'.encode()
        encrypted_msg = self.merkleHermanKnapsack.encrypt_message(message, self.other_client_public)
        self.communication_socket.send(encrypted_msg)
        print('> [Client] - HandShake message sent')

        # Wait for ACK
        ack_response = self.communication_socket.recv(1024)
        decrypted_msg = self.merkleHermanKnapsack.decrypt_message(ack_response, self.private_key)
        print(f'> [Client] - Other client reponse: {decrypted_msg.decode()}')

        # Generate half of the deck
        fist_half_random_deck = random.sample(range(FIRST_START_RANGE, FIRST_END_RANGE + 1), DECK_LENGTH)
        # Send the half of the deck
        encoded_half_deck = convert_list_of_int_to_string(fist_half_random_deck).encode()
        encrypted_msg = self.merkleHermanKnapsack.encrypt_message(encoded_half_deck, self.other_client_public)
        self.communication_socket.send(encrypted_msg)
        print(f'> [Client] - Half of the deck send!')

        # Receive other half of the deck
        second_half_response = self.communication_socket.recv(1024)
        decrypted_second_half_deck = self.merkleHermanKnapsack.decrypt_message(second_half_response, self.private_key).decode()
        print(f'> [Client] - Other half of the deck received!')

        # Compose common secret
        common_deck = generate_common_secret(fist_half_random_deck, decrypted_second_half_deck)
        self.streamCipher = StreamCipher(common_deck)
        print(f'> [Client] - Stream Cipher initialized with common key')
        print(f'> Deck - {common_deck}')

    
    def receiver_keypair_exchange(self) -> None:
        # First receive the hello message from the client
        message = self.communication_socket.recv(1024).decode()
        decrypted_message = self.merkleHermanKnapsack.decrypt_message(message, self.private_key)
        _, port = decrypted_message.split('#')
        print(f'> [Client] - Hello message from client: {port}')

        # Get the client public key from key server
        self.get_other_client_public_key(int(port))

        # Send ok Ack to hello message
        message = 'OK-Port And public key received'.encode()
        encrypted_message = self.merkleHermanKnapsack.encrypt_message(message, self.other_client_public)
        self.communication_socket.sendall(encrypted_message)

        # Generate half deck
        second_half_random_deck = random.sample(range(FIRST_END_RANGE, SECOND_END_RANGE + 1), FIRST_END_RANGE)
        # Receive the other half deck
        decoded_first_half = self.communication_socket.recv(1024)
        decrypted_first_half = self.merkleHermanKnapsack.decrypt_message(decoded_first_half, self.private_key).decode()
        print('> [Client] - First half of deck received')

        first_half_deck_numbers = convert_string_to_list_of_int(decrypted_first_half)
        # Send the other hald 
        encoded_second_half = convert_list_of_int_to_string(second_half_random_deck).encode()
        encrypted_second_half = self.merkleHermanKnapsack.encrypt_message(encoded_second_half, self.other_client_public)
        self.communication_socket.sendall(encrypted_second_half)
        print('> [Client] - Second half of the deck sent')

        # Compose common secret
        common_deck = generate_common_secret(first_half_deck_numbers, second_half_random_deck)
        self.streamCipher = StreamCipher(common_deck)
        print(f'> [Client] - Stream Cipher initialized with common key')
        print(f'> Deck - {common_deck}')

    def send_message(self) -> None:
        message = input('\n> Enter message: ')
        encoded_message = message.encode()
        encrypted_message = self.streamCipher.encode_byte_array(encoded_message)
        self.communication_socket.sendall(encrypted_message)

    def communication(self) -> None:
        while True:
            if not self.is_listening:
                self.send_message()
            
            response = self.communication_socket.recv(1024)
            decrypted_messsage = self.streamCipher.decode_byte_array(response)
            raw_message = decrypted_messsage.decode()
            print(f'> [Other client] - {raw_message}')

            if self.is_listening:
                self.send_message()

    def start(self):
        try:
            # First generate my public and private key
            self.generate_keys()
            # After that i can send to KeyServer my public key
            self.send_my_public_key()
            # Start Listening on my client socket
            self.start_listening()
            # If i am not listening to any connection I 
            #   try to connect to other client using his port
            if not self.is_listening:
                # If I got a port from user input
                #   I get his public key
                self.get_peer_user_port_and_key()
                # After that I connect to his socket
                self.connect_to_other_client()
                # And I start the common key exchange
                self.connector_keypair_exchange()
            else: 
                # If I am the listener, I make the common key exchange too
                self.receiver_keypair_exchange()

            self.communication()

        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()
         


def main(port: int):
    client = Client(port)
    client.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('port', help='Port of client process', type=int)

    args = parser.parse_args()
    main(port=args.port)