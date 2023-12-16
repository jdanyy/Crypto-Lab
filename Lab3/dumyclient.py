import socket
import sys
import threading
import argparse

from textual import work, events
from textual.app import App, ComposeResult
from textual.widgets import Input, Header, Markdown
from textual.containers import VerticalScroll
from typing import Any, Coroutine, Union
from merkle_hellman_knapsack import MerkleHellmanKnapsack

SERVER_HOST='localhost'
SERVER_PORT=8080
LISTEN_TIMEOUT=0.2

class Client(App):
    
    log_owner: str = 'LOG'

    def __init__(self, port:int, host: str='localhost'):
        super().__init__()
        self.host: str = host
        self.port: int = port
        self.own_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.key_server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.other_client_socket: Union[None, socket.socket] = None
        self.merkleHermanKnapsack: MerkleHellmanKnapsack = MerkleHellmanKnapsack()
        self.private_key: bytes = ''
        self.public_key: tuple[tuple, int, int] = ''
        self.other_client_public: bytes = ''
        self.is_listening: bool = True

        # For messages storing
        self.messages: list[tuple(str, str)] = []
        self.my_name: str = 'You'


    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Markdown()
        if not self.is_listening:
            yield Input(placeholder='Type your input...')


    def on_mount(self) -> None:
        self.query_one(Markdown).focus()
        self.title = f'Client - {self.port}'
        self.start()


    def on_unmount(self) -> None:
        self._clean_up_active_sockets()


    def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.value:
            self.messages.append((self.my_name, message.value))
            self.query_one(Markdown).update(self.conver_to_markdown())
            message.input.value = ''


    def conver_to_markdown(self) -> str:
        message = ''

        for sender, msg in self.messages:
            sender = sender if sender != self.log_owner else f'[{self.log_owner}]'
            message += f'> {sender} - {msg}\n'
        
        return message
    

    def _handle_socket_error(self, message: str) -> None:
        message = f'Server socket error: {message}'
        self.messages.append((self.log_owner, message))
        self.query_one(Markdown).update(self.conver_to_markdown())


    def _clean_up_active_sockets(self):
        if self.own_socket:
            self.own_socket.close()
        
        if self.key_server_socket:
            self.key_server_socket.close()

        if self.other_client_socket:
            self.other_client_socket.close()


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
        status, response_message = self.decompose_key_server_message(decoded_response)

        if status == 'ERROR' or status == 'NOT_FOUND':
            message = f'Error from KeyServer: {response_message}'
            self.messages.append((self.log_owner, message))
            self.query_one(Markdown).update(self.conver_to_markdown())
            self.key_server_socket.close()

            message = 'Stoping...'
            self.messages.append((self.log_owner, message))
            self.query_one(Markdown).update(self.conver_to_markdown())
            sys.exit()
    
        if status == 'CREATED':
            message = f'Public key stored: {response_message}'
            self.messages.append((self.log_owner, message))
            self.query_one(Markdown).update(self.conver_to_markdown())
            
        if status == 'OK':
            self.other_client_public = response_message

    
    def send_my_public_key(self):
        try:
            self.key_server_socket.connect((SERVER_HOST, SERVER_PORT))            

            message = self.compose_key_server_request_messsage('ADD')

            self.key_server_socket.sendall(message.encode())
            
            response = self.key_server_socket.recv(1024)
            self.process_server_response(response)
            self.key_server_socket.shutdown(socket.SHUT_RDWR)

        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()


    def send_public_key_request(self, port: int):
        try:
            message = self.compose_key_server_request_messsage('GET')
            self.key_server_socket.sendall(message.encode())
        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()

    def get_other_client_public_key(self, port: int):
        try:
            self.key_server_socket.connect((SERVER_HOST, SERVER_PORT))
            server_handler = threading.Thread(target=self.process_server_response)
            server_handler.start()

            self.send_public_key_request(port)
            self.key_server_socket.shutdown()
            server_handler.join()

        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()
    
    @work(exclusive=True, thread=True)
    def start_listening(self) -> None:
        self.own_socket.bind((self.host, self.port))
        self.own_socket.listen(1)

        message = f'Client is listening on port: {self.port}'
        self.messages.append((self.my_name, message))
        self.call_from_thread(self.query_one(Markdown).update, self.conver_to_markdown())
        # self.query_one(Markdown).update(self.conver_to_markdown())
        
        try:
            try:
                client_socket, addrs = self.own_socket.accept()
            except socket.error as e:
                self._handle_socket_error(e)
                sys.exit()

            message = f'Other client connected from address: {addrs}'
            self.messages.append((self.log_owner, message))
            self.call_from_thread(self.query_one(Markdown).update, self.conver_to_markdown())
            # self.query_one(Markdown).update(self.conver_to_markdown())

            if self.other_client_socket is not None:
                self.other_client_socket.close()

            self.other_client_socket = client_socket
            self.is_listening = False
        
        except KeyboardInterrupt:
            self.is_listening = False

    def on_key(self, event: events.Key) -> None:
        if event.key == "c" and event.ctrl:
            self.is_listening = False


    def start(self):
        try:
            # First generate my public and private key
            self.generate_keys()
            # After that i can send to KeyServer my public key
            self.send_my_public_key()
            # Start Listening on my client socket
            # threading.Thread(target=self.start_listening).start()
            self.start_listening()

            # Implement conversation logic


        except socket.error as e:
            self._handle_socket_error(e)
            sys.exit()
         


def main(port: int):
    client = Client(port)
    client.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('port', help='Port of client process', type=int)

    args = parser.parse_args()
    main(port=args.port)