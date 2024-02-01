import unittest

from SolitairCipher import Solitair

class TestSolitairCipher(unittest.TestCase):
    
    def setUp(self):
        self.solitair = Solitair()

    def test_deck_initialization(self):
        self.assertEqual(self.solitair.deck, list(range(1, 55)))

    def test_move_joker_A(self):
        self.solitair.move_joker_A()
        self.assertEqual(self.solitair.deck, list(range(1, 53)) + [54, 53])

    def test_move_joker_B(self):
        self.solitair.move_joker_B()
        self.assertEqual(self.solitair.deck, [1, 2, 54] + list(range(3, 54)))

    def test_triple_cut(self):
        solitair = Solitair()
        solitair.deck = [1, 2, 3, 54, 4, 5, 6, 53, 7, 8, 9]
        solitair.triple_cut()
        self.assertEqual(solitair.deck, [7, 8, 9, 54, 4, 5, 6, 53, 1, 2, 3])

    def test_card_value_switch(self):
        solitair = Solitair()
        solitair.deck = [1, 2, 3, 54, 4, 5, 6, 53, 7, 8, 9]
        solitair.card_value_switch()
        self.assertEqual(solitair.deck, [8, 1, 2, 3, 54, 4, 5, 6, 53, 7, 9])

    def test_get_value(self):
        solitair = Solitair()
        solitair.move_joker_A()
        solitair.move_joker_B()
        solitair.triple_cut()
        solitair.card_value_switch()
        self.assertEqual(solitair.get_value(solitair.deck[0]), 4)

        solitair.deck = [54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        self.assertEqual(solitair.get_value(solitair.deck[0]), 1)
        solitair.deck = [54, 1, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 53]
        self.assertIsNone(solitair.get_value(solitair.deck[0]))


    def test_key_stream_generator(self):
        solitair = Solitair()
        keystream = solitair.key_stream_generator(5)
        self.assertEqual(keystream, [4, 49, 10, 24, 8])


    def test_byte_stream_generator(self):
        solitair = Solitair()
        bytestream = solitair.byte_stream_generator(solitair.deck, 2)

        expected_keystream = [4, 49, 10, 24, 8, 51, 44, 6]
        chunks = [expected_keystream[i:i+4] for i in range(0, len(expected_keystream), 4)]
        expected_num_stream = [solitair.create_byte_from_numbers(ch) for ch in chunks]
        self.assertEqual(bytestream, bytes(expected_num_stream))