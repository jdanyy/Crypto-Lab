class BlumBlumShub:

    def __init__(self) -> None:
        BIT_NUM = 32

    def is_prime(self, num: int) -> bool:

        if num < 2 or num % 2 == 0:
            return False
        
        if num == 3 or num == 5: 
            return True
        
        if num % 3 == 0:
            return False 

        root = int(num**0.5)
        step = 2
        divider = 5

        while divider <= root:
            if num % divider == 0:
                return False
            
            divider += step 
            step = 6 - step
            
        return True

    def generate_prime_number(self, bits: int, prev: int) -> int:
        prime_num = 2**bits - 1

        while not (self.is_prime(prime_num) and prime_num % 4 == 3 and prime_num != prev):
            prime_num += 2

        return prime_num

    def generate_bit_array(self, seed: int, len_of_array: int) -> [int]:

        p = self.generate_prime_number(self.BIT_NUM, 0)
        q = self.generate_prime_number(self.BIT_NUM, p)

        n = p * q 

        x = seed % n

        result = []

        for _ in range(len_of_array):
            x = (x**2) % n
            bit = x % 2
            result.append(bit)

        return result
    
    def generate_byte_stream(self, seed: int, len_of_key: int) -> bytes:
        
        bits = self.generate_bit_array(seed, 8 * len_of_key)
        
        chunks = [bits[i:i+8] for i in range(0, len(bits), 8)]
        
        byte_array = bytes([int(''.join(map(str,chunk)), 2) for chunk in chunks])
        
        return byte_array
    