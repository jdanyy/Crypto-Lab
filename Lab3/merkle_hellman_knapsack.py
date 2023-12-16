import random
from utils import byte_to_bits, bits_to_byte, modinv, coprime, compose_bits_from_super_increase

class MerkleHellmanKnapsack:

    def __init__(self): 
        self.n = 8


    def get_a_random_higher_then(self, num: int) -> int:
        return random.randint(num + 1, 2 * num)

    def generate_super_increasing_list(self) -> [int]:
        v = []
        v0 = random.randint(2, 10)
        v.append(v0)

        for _ in range(1, self.n):
            sum_before = sum(v)

            v.append(self.get_a_random_higher_then(sum_before))

        return v
    
    def generate_coprime(self, num: int) -> int:
        
        while True:
            coprime_num = random.randint(2, num - 1)

            if coprime(coprime_num, num):
                return coprime_num

    def generate_private_key(self, n=None)->bytes:
        if n:
            self.n = n
        
        print('> The current length of the keypair is: {}'
                  .format(self.n))
        
        v = self.generate_super_increasing_list()

        q = self.get_a_random_higher_then(sum(v))
        r = self. generate_coprime(q)

        tuple_v = tuple(v)

        return (tuple_v, q, r)

    def generate_public_key(self, private_key: tuple) -> bytes:
        v, q, r = private_key
        return tuple([(vi * r) % q for vi in v])
    
    def encrypt_message(self, message: bytes, public_key: tuple) -> bytes:
        
        def encryp_byte(byte: bytes, public_key: tuple):
            bits = byte_to_bits(byte)
            return sum(a*b for a, b in zip(bits, public_key))
        

        chunk_size = len(public_key)
        encrypted_message = []

        for i in range(0, len(message), chunk_size):
            chunk = message[i:i+chunk_size]

            encrypted_chunk = [encryp_byte(byte, public_key) for byte in chunk]
            encrypted_message.extend(encrypted_chunk)

        return encrypted_message
    


    def decrypt_message(self, message: bytes, private_key: tuple) -> bytes:
        v, q, r = private_key

        s = modinv(r, q)
        decrypted_message = b''

        for message_component in message:
            value = (s * message_component) % q 
            bits = compose_bits_from_super_increase(v, value)
            byte_representation = bits_to_byte(bits)
            decrypted_message += byte_representation.to_bytes(1, 'big')

        return decrypted_message