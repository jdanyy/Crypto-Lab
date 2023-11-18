import secrets

from SolitairCipher import Solitair
from BlumBlumShub import BlumBlumShub


class StreamCipher:
    def __init__(self, algorithm, seed):
        self.data = []
        self.algorithm = algorithm if algorithm else None
        self.seed = seed if seed != 0 else list(range(1,55))

    def __str__(self):
        return f'Hi, I am a stream cipher.'
        
    def get_key_by_algorithm(self, len_of_key: int) -> bytes:
        
        if self.algorithm == 'solitair':
            soli = Solitair()
            soli.initialize_deck(self.seed)
            return soli.byte_stream_generator(len_of_key)
        
        if self.algorithm == 'blumblum':
            blum = BlumBlumShub()
            
            return blum.generate_byte_stream(self.seed, len_of_key)
        
        return secrets.token_bytes(len_of_key)
        
    def encode_byte_array(self, text: bytes) -> bytes:

        key = self.get_key_by_algorithm(len(text))
            

        encrypted_text = [input_byte ^ key_byte for input_byte, key_byte in zip(text, key)]
 
        return bytes(encrypted_text)
       
    def decode_byte_array(self, cipher_text: bytes) -> bytes:
        
        key = self.get_key_by_algorithm(len(cipher_text))
        
        decrypted_text = [input_byte ^ key_byte for input_byte, key_byte in zip(cipher_text, key)]
        
        return bytes(decrypted_text)