import socket
import threading
import json
import argparse
from StreamCipher import StreamCipher


def read_config_file(filepath):
    with open(filepath, 'r') as f:
        config = json.load(f)

    return config

def receive_data(client_socket, streamCipher: StreamCipher):
    while True:
        message = client_socket.recv(1024)

        if not message:
            break

        decrypted_message = streamCipher.decode_byte_array(message)

        print(f'I got the following message: {decrypted_message.decode()}\n> Enter message: ')

        if message == 'BYE':
            break


def client(host, port, filepath):
    config = read_config_file(filepath)

    streamCipher = StreamCipher(algorithm=config['alg'], seed=config['seed'])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print(f'Client connected to another client')

    receive_thread = threading.Thread(target=receive_data, args=(client_socket, streamCipher))
    receive_thread.start()

    while True:
        message = input("Enter a message: ")
        encrypted_message = streamCipher.encode_byte_array(message.encode())
  
        client_socket.sendall(encrypted_message)
        
        if message == 'BYE':
            break


def main(filepath):
    host='localhost'
    port=5510

    client(host, port, filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stream Cipher')
    parser.add_argument('filepath', help='Config file path')

    args = parser.parse_args()
    main(filepath=args.filepath)
    