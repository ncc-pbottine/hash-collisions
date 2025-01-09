# Hash Collisions

This repository contains resources for generating large numbers of collisions for *non-cryptographic* hash functions. Generating colliding inputs for such functions can be achieved in several different ways (mathematically, combinatorially, using SMT solvers, etc). Currently, this repository implements a meet-in-the-middle approach to generate collisions, and only support simple multiplicative hash functions producing a 32-bit digest.

Generating collisions can be performed as follows:

~~~python
# Define an instance of a MultiplicativeHash with initial value 5387 and multiplier 31
# The hash function with these parameters is sometimes referred to as Daniel J. Bernstein’s algorithm
mHash = MultiplicativeHash(5381, 33)

# The size of the colliding inputs corresponds to prefix_size + suffix_size
prefix_size = 8

# The suffix size dictates the time-memory tradeoff. A table of size 2^(suffix_size*8) will be created.
# The larger this value, the more time precomputations will take, but the quicker collisions will be 
# generated after that. Currently, we upper bound this value to 3, which would result in a table of
# size 2^24, which corresponds to over 200 MB for inputs of size 10.
suffix_size = 2

# The number of collisions to generate
n_collisions = 1000

collisions = mHash.meet_in_middle(prefix_size, suffix_size, n_collisions)
~~~
