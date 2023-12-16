import unittest

from src.merkle_hellman_knapsack import MerkleHellmanKnapsack
from src.utils import coprime

class TestMerkleHelmanKnapsack(unittest.TestCase):

    def setUp(self):
        self.merkle = MerkleHellmanKnapsack()

    def test_super_increasing_list(self):

        super_increasing_list = self.merkle.generate_super_increasing_list()
        print(f'> Super increasing: {super_increasing_list}')
        self.assertEqual(len(super_increasing_list), self.merkle.n)
        self.assertTrue(all(super_increasing_list[i] > sum(super_increasing_list[:i]) for i in range(1, self.merkle.n)))

    def test_generate_coprime(self):
        num = 100

        comprime_value = self.merkle.generate_coprime(num)
        self.assertTrue(coprime(num, comprime_value))

    def test_generate_private_key(self):
        private_key = self.merkle.generate_private_key()
        print(f'> Generated Private key: {private_key}')

        self.assertEqual(len(private_key), 3)
        self.assertEqual(len(private_key[0]), self.merkle.n)

    def test_generate_public_key(self):
        private_key = self.merkle.generate_private_key()
        public_key = self.merkle.generate_public_key(private_key)

        print(f'> Test Public key: {public_key}')

        self.assertEqual(len(public_key), self.merkle.n)

    def test_encrypt_and_decrypt(self):
        private_key = self.merkle.generate_private_key()
        public_key = self.merkle.generate_public_key(private_key)

        message = b'Test message'

        encrypted_message = self.merkle.encrypt_message(message, public_key)
        decrypted_message = self.merkle.decrypt_message(encrypted_message, private_key)

        self.assertEqual(message, decrypted_message)

if __name__ == '__main__':
    unittest.main()