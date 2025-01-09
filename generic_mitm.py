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


    def meet_in_middle(self, prefix_size, suffix_size, n_collisions=10):
        precomp = {}
        
        target = self.__rand_generator(prefix_size + suffix_size)
        target_hash = self.hash(target)

        # We upperbound the memory usage to 2^24
        upper_bound = min(24, suffix_size*8)

        print("Target value : ", target)
        print("Target hash : ", target_hash)
        print("Starting precomputations.")

        for i in range(2**upper_bound):
            s = self.__suffix_generator(i, suffix_size)
            h = self.__partial_backward_hash(s, target_hash)
            # print("{%s: %s}" % (binascii.hexlify(h.to_bytes(4, byteorder='big')), binascii.hexlify(s)))
            precomp[h] = s
        
        print("Done precomputing.")

        input("Press Enter to start finding collisions...")

        # for k in precomp:
        #   print k, precomp[k]
        n = 0
        collisions = []
        while n != n_collisions:
            s = self.__rand_generator(prefix_size)
            h = self.__partial_forward_hash(s)
            if h in precomp:
                # print(binascii.hexlify(s + precomp[h]))
                print(s + precomp[h])
                collisions.append(s + precomp[h])
                n += 1
        return collisions

def print_c_array(hex_string):
    return "{" + ", ".join('0x%02x' % i for i in bytearray.fromhex(hex_string)) + "}"

def consistency_tests():
    size = 10
    prefix_size = 8
    suffix_size = size - prefix_size
    mHash = MultiplicativeHash(5387, 31)
    collisions = mHash.meet_in_middle(prefix_size, suffix_size, 10)
    hash1 = mHash.hash(collisions[0])

    for c in collisions[1:]:
        assert(mHash.hash(c) == hash1)
        # print(mHash.hash(c))

def main(args):
    consistency_tests()


if __name__ == "__main__":
    main(sys.argv)