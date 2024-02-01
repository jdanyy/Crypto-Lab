from collections import deque

class Solitair:
    def __init__(self) -> None:
        self.deck = list(range(1,53))
        self.deck.append(53)
        self.deck.append(54)
        self.white_joker = 53
        self.black_joker = 54

    def initialize_deck(self, deck):
        self.deck = deck

    def shift_an_array_portion(self, destination_index, elem):
        l = self.deck.copy()

        previous_index = l.index(elem)

        l[destination_index+1:previous_index+1] = self.deck[destination_index:previous_index].copy()
        l[destination_index] = elem

        self.deck = l 

    def move_joker_A(self) -> None:

        index_of_joker = self.deck.index(self.white_joker)

        if index_of_joker == (len(self.deck) - 1):
            self.shift_an_array_portion(1, self.white_joker)
        else:
            self.deck[index_of_joker], self.deck[index_of_joker + 1] = self.deck[index_of_joker + 1], self.deck[index_of_joker]


    def move_joker_B(self) -> None:

        index_of_joker = self.deck.index(self.black_joker)

        if index_of_joker == (len(self.deck) - 1):
            self.shift_an_array_portion(2, self.black_joker)
        elif index_of_joker == (len(self.deck) - 2): 
            self.shift_an_array_portion(1, self.black_joker)
        else:
            # self.deck[index_of_joker], self.deck[index_of_joker+2] = self.deck[index_of_joker+2], self.deck[index_of_joker]
            new_index_of_joker = index_of_joker + 2
            self.deck[index_of_joker:new_index_of_joker] = self.deck[index_of_joker+1:new_index_of_joker+1]
                
            self.deck[new_index_of_joker] = self.black_joker
        
    def triple_cut(self) -> None:

        first_joker_index = min(self.deck.index(self.black_joker), self.deck.index(self.white_joker))
        second_joker_index = max(self.deck.index(self.black_joker), self.deck.index(self.white_joker))

        top_deck = self.deck[:first_joker_index].copy()
        middle_deck = self.deck[first_joker_index:second_joker_index+1].copy()
        bottom_deck = self.deck[second_joker_index+1:].copy()

        self.deck.clear()
        self.deck.extend(bottom_deck + middle_deck + top_deck)

    def card_value_switch(self) -> None:

        bottom_card = self.deck[-1]
        
        if bottom_card in [self.black_joker,self.white_joker]:
            return
            
        top_deck = self.deck[:bottom_card].copy()
        bottom_deck = self.deck[bottom_card:-1]

        self.deck.clear()
        self.deck.extend(bottom_deck + top_deck + [bottom_card])


    def get_value(self, top_value):
        if top_value == self.black_joker:
            top_value = self.white_joker

        key_value = self.deck[top_value]

        if key_value == self.white_joker or key_value == self.black_joker:
            return None

        return key_value
    
    def key_stream_generator(self, length: int) -> [int]:
        keystream = []

        i = 0
        while i < length:
            
            self.move_joker_A()
            self.move_joker_B()
            self.triple_cut()
            self.card_value_switch()
            top_value = self.deck[0]    
            key_value = self.get_value(top_value)

            if key_value:
                keystream.append(key_value)
                i += 1


        return keystream

    
    def create_byte_from_numbers(self, numbers: [int]) -> int:
        
        num_to_byte = [(num % 4) for num in numbers]

        return num_to_byte[0] + (num_to_byte[1] << 2) + (num_to_byte[2] << 4) + (num_to_byte[3] << 6)
        
        
    def byte_stream_generator(self, deck, length: int) -> bytes:
        self.initialize_deck(deck)
        keystream = self.key_stream_generator(4 * length)
        
        chunks = [keystream[i:i+4] for i in range(0, len(keystream), 4)]
        
        large_num_stream = [self.create_byte_from_numbers(chunk) for chunk in chunks]
        
        return bytes(large_num_stream)

