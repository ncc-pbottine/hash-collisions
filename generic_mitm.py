#! /usr/bin/env python3

import string
import random
import sys
import os
import binascii
import logging
import argparse

U32_MASK = 0xFFFFFFFF
U32_SIZE = 32

class MultiplicativeHash():
    """
        Multiplicative hash with given initial value and multiplier.
        Only computes on 32-bit hashes for now.
    """
    def __init__(self, initial_value, multiplier):
        self.INITIAL_VALUE = initial_value
        self.MULTIPLIER = multiplier
        self.hash_size = (1 << U32_SIZE)
        self.INV_MULTIPLIER = pow(self.MULTIPLIER, -1, self.hash_size)


    def hash(self, val):
        digest = self.INITIAL_VALUE
        for i in range(0, len(val)):
            digest = ((digest * self.MULTIPLIER) + val[i]) & U32_MASK
        return digest


    def __partial_forward_hash(self, val):
        return self.hash(val)

    def __partial_backward_hash(self, val, target):
        hash_target = target
        for char in val[::-1]:
            hash_target = (((hash_target - char) * self.INV_MULTIPLIER)) & U32_MASK
        return hash_target


    def __rand_generator(self, size):
        return bytearray(os.urandom(size))

    def __suffix_generator(self, int_val, len):
        return int_val.to_bytes(len, byteorder='big')

    def __show_progress(self, current, total, bar_length=40):
        progress = current / total
        bar = '#' * int(progress * bar_length) + '-' * (bar_length - int(progress * bar_length))
        percent = progress * 100
        sys.stdout.write(f'\rProgress: [{bar}] {percent:.2f}%')
        sys.stdout.flush()

    def meet_in_middle(self, prefix_size, suffix_size, n_collisions=10, target_hash=None, output=None, print_fct=print, interactive=False):
        precomp = {}
        
        if target_hash is None:
            target_hash = random.randint(0, 2**U32_SIZE - 1)


        # We upperbound the memory usage to 2^24
        upper_bound = min(24, suffix_size*8)

        print("Target hash: ", target_hash)
        print("Entries in table: 2^", upper_bound, " = ", 2**upper_bound)
        print("Starting precomputations.")

        total = 2**upper_bound
        increment_display = total // 1000
        for i in range(total):
            # Displaying progress
            if interactive and (i % increment_display == 0 or i == total - 1):
                self.__show_progress(i, total)

            s = self.__suffix_generator(i, suffix_size)
            h = self.__partial_backward_hash(s, target_hash)
            precomp[h] = s
        
        print("\nDone precomputing.")

        n = 0
        collisions = []
        while n != n_collisions:
            s = self.__rand_generator(prefix_size)
            h = self.__partial_forward_hash(s)
            if h in precomp:
                # print(binascii.hexlify(s + precomp[h]))
                print_fct(s + precomp[h])
                collisions.append(s + precomp[h])
                n += 1
        return collisions

def print_c_array(hex_string):
    print("{" + ", ".join('0x%02x' % i for i in hex_string) + "}")

def print_hex_string(array):
    print(binascii.hexlify(array))

def consistency_tests():
    size = 10
    prefix_size = 7
    suffix_size = size - prefix_size
    mHash = MultiplicativeHash(5387, 31)
    collisions = mHash.meet_in_middle(prefix_size, suffix_size, 10, 0)
    hash1 = mHash.hash(collisions[0])

    for c in collisions[1:]:
        assert(mHash.hash(c) == hash1)
        # print(mHash.hash(c))

def run_attack(prefix_size, suffix_size, initial_value, multiplier, n_collisions, print_fct, interactive):
    mHash = MultiplicativeHash(initial_value, multiplier)
    collisions = mHash.meet_in_middle(prefix_size, suffix_size, n_collisions=n_collisions, print_fct=print_fct, interactive=interactive)
    print(collisions)

def main(args):
    # consistency_tests()
    print_fct = print
    if args.format == 'c':
        print_fct = print_c_array
    elif args.format == 'hex':
        print_fct = print_hex_string

    run_attack(args.prefix, args.suffix, args.initial, args.multiplier, args.n_collisions, print_fct, args.interactive)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to generate colliding inputs for multiplicative hash functions.")
    parser.add_argument('-f', '--format', type=str, choices=['c', 'hex', 'bytes'], default='bytes',
                        help="Output format: 'c' for C-style byte array, 'hex' for hexadecimal, 'bytes' for byte representation (default: 'bytes').")
    # Todo:
    # There should be 3 output options
    # If the script is called as a standalone script, print to std out or file
    # If it is called from somewhere else, return collisions or print to file
    parser.add_argument('-o', '--output', type=str, help='Output file to write the result to. If not provided, prints to console.')
    parser.add_argument('-p', '--prefix', type=int, default=7, help='Prefix size')
    parser.add_argument('-s', '--suffix', type=int, default=3, help='Suffix size. Dictates the size of the precomputation table.')
    parser.add_argument('-i', '--initial', type=int, default=5387, help='Initial value for the multiplicative hash computation.')
    parser.add_argument('-m', '--multiplier', type=int, default=31, help='Multiplier for the multiplicative hash computation.')
    parser.add_argument('-n', '--n-collisions', type=int, default=10, help='The number of collisions to compute.')
    parser.add_argument('--interactive', action='store_true', help='Make it interactive, printing a progress bar.')
    # parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode.')
    args = parser.parse_args()
    main(args)