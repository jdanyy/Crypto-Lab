import socket
import threading
import json
import argparse

class KeyServer:
    def __init__(self, host: str='localhost', port: int=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.public_keys = {}

    def add_key(self, key: str, value: str) -> None:
        self.public_keys[key] = value

    def get_key(self, key: str) -> str:
        return self.public_keys[key]
    
    def compose_client_response(self, status: str, message: str) -> str:

        return f'{status}#{message}'
    
    def process_client_message(self, message: str, client_id: str) -> str:
                
        request_parts = message.split('#')
        print(f'>[{client_id}] - Client make an {request_parts[0]} request')
        if request_parts[0] == "ADD":
            key = request_parts[1]
            value = request_parts[2]

            self.add_key(key, value)
            
            return self.compose_client_response('CREATED', 'Public key stored')
        elif request_parts[0] == "GET":
            key = request_parts[1]
            if key not in self.public_keys.keys():
                return self.compose_client_response('NOT_FOUND', 'Client not found')

            print(f'> Response to client: {self.public_keys[key]}')
            return self.compose_client_response('OK', self.public_keys[key])
        

        return self.compose_client_response('ERROR', 'Invalid client request')

    def handle_client(self, client_socket: socket.socket, client_id: str) -> str:
        request = client_socket.recv(1024).decode()

        server_response = self.process_client_message(request, client_id)

        client_socket.sendall(server_response.encode())
        print(f'> KeyServer response to [{client_id}] Client - Sent!')
        
        client_socket.close()
        print(f'> Client with id - [{client_id}] deconected')

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f'> Server is listening on: {self.host}:{self.port}')

            while True: 
                client_socket, client_addr = self.server_socket.accept()
                print(f'> Client connected from: {client_addr}')
                client_id = client_addr[1]

                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_id))
                client_handler.start()

        except socket.error as e:
            print(f'Server start error: {e}')
            
def main(filepath):
    with open(filepath, 'r') as f:
        config = json.load(f)

    keyServer = KeyServer(config['host'], config['port'])

    keyServer.start()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='KeyServer')
    parser.add_argument('config_path', help='The server config file path')

    args = parser.parse_args()
    main(filepath=args.config_path)