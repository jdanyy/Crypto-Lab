#!/usr/bin/env python3 -tt
"""
Mathematical utilities for CS41's Assignment 1: Cryptography.
"""
import fractions as _fractions
from math import gcd
import socket
from itertools import chain

class Error(Exception):
    """Base class for exceptions in this module."""

class BinaryConversionError(Error):
    """Custom exception for invalid binary conversions."""
    pass

def is_superincreasing(seq):
    """Return whether a given sequence is superincreasing."""
    ct = 0  # Total so far
    for n in seq:
        if n <= ct:
            return False
        ct += n
    return True


def modinv(a, b):
    """Returns the modular inverse of a mod b.

    Pre: a < b and gcd(a, b) = 1

    Adapted from https://en.wikibooks.org/wiki/Algorithm_Implementation/
    Mathematics/Extended_Euclidean_algorithm#Python
    """
    saved = b
    x, y, u, v = 0, 1, 1, 0
    while a:
        q, r = b // a, b % a
        m, n = x - u*q, y - v*q
        b, a, x, y, u, v = a, r, u, v, m, n
    return x % saved


def coprime(a, b):
    """Returns True iff `gcd(a, b) == 1`, i.e. iff `a` and `b` are coprime"""
    return gcd(a, b) == 1


def byte_to_bits(byte):
    if not 0 <= byte <= 255:
        raise BinaryConversionError(byte)

    out = []
    for i in range(8):
        out.append(byte & 1)
        byte >>= 1
    return out[::-1]


def bits_to_byte(bits):
    if not all(bit == 0 or bit == 1 for bit in bits):
        raise BinaryConversionError("Invalid bitstring passed")

    byte = 0
    for bit in bits:
        byte *= 2
        if bit:
            byte += 1
    return byte

def compose_bits_from_super_increase(v: [int], num: int) -> [int]:
    bits = []
    for i in range(len(v) - 1, 0, -1):
        if num >= v[i]:
            num -= v[i]
            bits.append(1)
        else:
            bits.append(0)
    bits.reverse()
    return bits

def convert_list_of_int_to_string(integer_list: [int]) -> str:
    return '#'.join(str(i) for i in integer_list)

def convert_string_to_list_of_int(string: str) -> [int]:
    return [int(x) for x in string.split('#')]

def generate_common_secret(list1: [int], list2: [int]) -> [int]:
    return list(chain(*zip(list1, list2)))


def create_and_listen(host: str, port: int) -> tuple:

    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        connection_socket.connect((host, port))
        print(f'> Client connected to {host}:{port}')
    except socket.error as e:
        print(f'> Connection to {host}:{port} failed. Creating server socket.')

        try:
            connection_socket.bind((host, port))

            connection_socket.listen(1)
            print(f'> Client listening on {host}:{port}')

            client_socket, client_addr = connection_socket.accept()

            print(f'> Client connection from address: {client_addr}')

            return (connection_socket, client_socket)

        except socket.error as e: 
            print('> Server error!')
            sys.exit()

    return (connection_socket, None)