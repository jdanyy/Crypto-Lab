#!/usr/bin/env python3 -tt
"""
File: crypto.py
---------------
Assignment 1: Cryptography
Course: CS 41
Name: Jako Daniel
SUNet: jdim2141

Replace this with a description of the program.
"""
import utils
import math


def check_text_length(text: str) -> None:
    """Error handling function for cipers 
    """

    if len(text) > 0:
        return

    raise ValueError('The given text not contains any charachter')


def check_upper_case(text: str) -> None:
    """Uppercase check function
    """

    if text.isupper():
        return

    raise ValueError('The given text contains lowercase charachters')


def is_alphabetic(text: str) -> None:
    """Check if the text is contains only alphabetic characters

    """

    if text.isalpha():
        return

    raise ValueError('The given text contains non-alphabetic charachters')


def validate(text: str) -> bool:
    """Make all validation constraints

    """

    if not text.isalpha():
        raise ValueError('The given text contains non-alphabetic charachters')

    if not text.isupper():
        raise ValueError('The given text contains lowercase charachters')

    if len(text) == 0:
        raise ValueError('The given text is empty')

    return True


def shift_letter(letter: str, shifting: int) -> str:

    return chr((ord(letter) + shifting - ord('A')) % 26 + ord('A'))


# Caesar Cipher
def encrypt_caesar(plaintext: str) -> str:
    """Encrypt plaintext using a Caesar cipher.
    The encyption is implemented with 3 shifting
    """
    shifting = 3
    try:
        check_text_length(plaintext)
        check_upper_case(plaintext)

        res = [letter if not letter.isalpha() else shift_letter(letter, shifting) for letter in plaintext]

        return ''.join(res)

    except ValueError as e:
        print(e)


def decrypt_caesar(ciphertext: str) -> str:
    """Decrypt a ciphertext using a Caesar cipher.
    Caesar decryption is using 3 shifting
    """
    shifting = 3
    try:
        check_text_length(ciphertext)
        check_upper_case(ciphertext)

        res = [letter if not letter.isalpha() else shift_letter(letter, -shifting) for letter in ciphertext]

        return ''.join(res)

    except ValueError as e:
        print(e)


# Vigenere Cipher

def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """Encrypt plaintext using a Vigenere cipher with a keyword.
    """
    try:
        validate(plaintext)
        validate(keyword)

        result = ''
        keyword_len = len(keyword)

        for i, letter in enumerate(plaintext): 
            shift_character = keyword[i % keyword_len]
            shift_number = ord(shift_character) - ord('A')

            result_charachter = shift_letter(letter, shift_number)

            result += result_charachter

        return result

    except ValueError as e:
        print(e)


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """Decrypt ciphertext using a Vigenere cipher with a keyword.
    """

    try:
        validate(ciphertext)
        validate(keyword)

        result = ''
        keyword_len = len(keyword)

        for i, letter in enumerate(ciphertext):
            shift_character = keyword[i % keyword_len]
            shift_number = ord(shift_character) - ord('A')

            result_charachter = shift_letter(letter, -shift_number)

            result += result_charachter

        return result

    except ValueError as e:
        print(e)


def encrypt_scytale(plaintext: str | bytes, circumference: int) -> str | bytes:
    """Encrypt plaintext using Scytale Cipher
    """

    try:
        is_incomplet = len(plaintext) % circumference
        complet_line_nr = len(plaintext) // circumference

        if is_incomplet == 0:
            step_complet = step_incomplet = len(plaintext) // circumference
        else:
            step_complet = circumference
            step_incomplet = is_incomplet

        rows = [plaintext[i:(i+step_complet)] for i in range(0, step_complet * complet_line_nr, step_complet)]

        if is_incomplet:
            plaintext = plaintext[(step_complet * complet_line_nr):]

            incomplet_rows = [plaintext[i:(i+step_incomplet)] for i in range(0, len(plaintext), step_incomplet)]
            [rows.append(row) for row in incomplet_rows]

        if isinstance(plaintext, bytes):
            ciper_text = [bytes([column[i]]) for i in range(0, step_incomplet) for column in rows]
            if is_incomplet:
                [ciper_text.append(bytes([row[i]]))
                 for i in range(step_incomplet, step_complet) for row in rows[:complet_line_nr]]
            return b''.join(ciper_text)

        ciper_text = [column[i] for i in range(0, step_incomplet) for column in rows]
        if is_incomplet:
            [ciper_text.append(column[i])
             for i in range(step_incomplet, step_complet) for column in rows[:complet_line_nr]]

        return ''.join(ciper_text)

    except ValueError as e:
        print(e)


def decrypt_scytale(cipertext: str | bytes, circumference: int) -> str | bytes:
    """Decrypt cipertext using Scytale Cipher
    """
    plaintext = ['' for _ in range(len(cipertext))]

    binary = False
    if isinstance(cipertext, bytes):
        binary = True
        plaintext = [b'' for _ in range(len(cipertext))]

    if len(cipertext) % circumference == 0:
        step_complet = step_incomplet = len(cipertext) / circumference
    else:
        step_complet = math.ceil(len(cipertext) / circumference)
        step_incomplet = math.floor(len(cipertext) / circumference)

    complet_rows_nr = len(cipertext) % circumference

    rows = [cipertext[i:(i+step_complet)] for i in range(0, step_complet * complet_rows_nr, step_complet)]

    if len(cipertext) % circumference != 0:
        cipertext = cipertext[(step_complet * complet_rows_nr):]

        in_complet_rows = [cipertext[i:(i+step_incomplet)] for i in range(0, len(cipertext), step_incomplet)]

        [rows.append(row) for row in in_complet_rows]

    for index, row in enumerate(rows):

        index_in_plain = index
        for letter in row:
            if binary:
                plaintext[index_in_plain] = bytes([letter])
            else:
                plaintext[index_in_plain] = letter
            index_in_plain += circumference

    if isinstance(cipertext, bytes):
        return b''.join(plaintext)

    return ''.join(plaintext)


def encrypt_railfence(plaintext: str, circumference: int) -> str:
    """Encrypt plain text using Railfence Cipher
    """
    ciphertext = ['' for _ in range(circumference)]

    row = 0
    direction = 1
    for letter in plaintext:
        ciphertext[row] += letter

        if row == 0:
            direction = 1
        elif row == circumference - 1:
            direction = -1

        row += direction

    return ''.join(ciphertext)


def decrypt_railfence(ciphertext: str, circumference: int) -> str:
    """Decrypt plain text using Railfence Cipher
    """

    plaintext = ['' for _ in range(len(ciphertext))]

    plaintext_len = len(ciphertext)

    index_in_plain = 0

    row = 0
    i = 0
    while i < len(ciphertext):
        if index_in_plain >= (plaintext_len - row):
            row += 1
            index_in_plain = row
        plaintext[index_in_plain] = ciphertext[i]
        i = i + 1

        if row == 0 or row == circumference - 1:
            step = 2 * circumference - 2
        else:
            step = 2*(circumference - row) - 2

        index_in_plain += step

        if row != 0 and row != circumference - 1:
            print(index_in_plain, ciphertext[i])
            plaintext[index_in_plain] = ciphertext[i]
            next_index = index_in_plain + 2 * row
            i += 1

            index_in_plain = next_index
        
    return ''.join(plaintext)


# Merkle-Hellman Knapsack Cryptosystem
def generate_private_key(n=8):
    """Generate a private key for use in the Merkle-Hellman Knapsack Cryptosystem.

    Following the instructions in the handout, construct the private key components
    of the MH Cryptosystem. This consistutes 3 tasks:

    1. Build a superincreasing sequence `w` of length n
        (Note: you can check if a sequence is superincreasing with `utils.is_superincreasing(seq)`)
    2. Choose some integer `q` greater than the sum of all elements in `w`
    3. Discover an integer `r` between 2 and q that is coprime to `q` (you can use utils.coprime)

    You'll need to use the random module for this function, which has been imported already
    
    Somehow, you'll have to return all of these values out of this function! 
    Can we do that in Python?!

    @param n bitsize of message to send (default 8)
    @type n int

    @return 3-tuple `(w, q, r)`, with `w` a n-tuple, and q and r ints.
    """
    raise NotImplementedError  # Your implementation here


def create_public_key(private_key):
    """Create a public key corresponding to the given private key.

    To accomplish this, you only need to build and return `beta` as described in the handout.

        beta = (b_1, b_2, ..., b_n) where b_i = r × w_i mod q

    Hint: this can be written in one line using a list comprehension

    @param private_key The private key
    @type private_key 3-tuple `(w, q, r)`, with `w` a n-tuple, and q and r ints.

    @return n-tuple public key
    """
    raise NotImplementedError  # Your implementation here


def encrypt_mh(message, public_key):
    """Encrypt an outgoing message using a public key.

    1. Separate the message into chunks the size of the public key (in our case, fixed at 8)
    2. For each byte, determine the 8 bits (the `a_i`s) using `utils.byte_to_bits`
    3. Encrypt the 8 message bits by computing
         c = sum of a_i * b_i for i = 1 to n
    4. Return a list of the encrypted ciphertexts for each chunk in the message

    Hint: think about using `zip` at some point

    @param message The message to be encrypted
    @type message bytes
    @param public_key The public key of the desired recipient
    @type public_key n-tuple of ints

    @return list of ints representing encrypted bytes
    """
    raise NotImplementedError  # Your implementation here


def decrypt_mh(message, private_key):
    """Decrypt an incoming message using a private key

    1. Extract w, q, and r from the private key
    2. Compute s, the modular inverse of r mod q, using the
        Extended Euclidean algorithm (implemented at `utils.modinv(r, q)`)
    3. For each byte-sized chunk, compute
         c' = cs (mod q)
    4. Solve the superincreasing subset sum using c' and w to recover the original byte
    5. Reconsitite the encrypted bytes to get the original message back

    @param message Encrypted message chunks
    @type message list of ints
    @param private_key The private key of the recipient
    @type private_key 3-tuple of w, q, and r

    @return bytearray or str of decrypted characters
    """
    raise NotImplementedError  # Your implementation here
