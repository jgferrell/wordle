#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Jan. 2023
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""A script to help you decide on your next Wordle guess."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
import argparse
import itertools
from typing import Generator
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def _cli_parse(args: argparse.Namespace):
    """Feed command line data to guess generator and print guesses."""
    dictionary = None
    if args.dictionary is not None:
        dictionary = set(_ for _ in args.dictionary.split())
    present = ''
    if args.present is not None:
        present = args.present
    for guess in guess_generator(args.word, args.available, present, dictionary):
        print(guess)

def _permgen(p: str) -> Generator[str, None, None]:
    """Generate permutation strings instead of tuples."""
    for perm in itertools.permutations(p):
        yield ''.join(perm)

def _combogen(p: str, r: int) -> Generator[str, None, None]:
    """Generate combination strings instead of tuples."""
    for combo in itertools.combinations(p, r):
        yield ''.join(combo)
        
def guess_generator(previous_guess: str, available_letters: str, required_letters: str = '', dictionary=None) -> Generator[str, None, None]:
    """Generates wordle guesses. `previous_guess` should a 5-character
    string with '?' as placeholders for unknown
    letters. `required_letters` is a string containing all letters
    known to be in the word but in an unknown
    location. `available_letters` is a string containing all other
    letters available for the next guess; these are available in
    addition to those in `required_letters`. If the letter 'x' is
    available and possibly in the word twice, it should be included in
    `available_letters` twice as well.

    `dictionary`, if provided, contains all possible words. Words must
    be accessible with the 'in' operator. If a dictionary is provided,
    only guesses found in the dictionary will be yielded.
    """
    n_unknown = previous_guess.count('?')
    n_required = len(required_letters)

    # build a permutation generator to use for guesses
    if n_unknown == n_required:
        perms = _permgen(required_letters)
    else:
        perm_generators = []
        combos_seen = set()
        for combo in _combogen(available_letters, n_unknown - n_required):
            if combo in combos_seen:
                continue
            combos_seen.add(combo)
            perm_generators.append(_permgen(combo + required_letters))
        perms = itertools.chain(*perm_generators)

    # use string permutations to generate guesses
    perms_seen = set()
    for perm in perms:
        if perm in perms_seen:
            continue
        perms_seen.add(perm)
        guess = previous_guess
        for letter in perm:
            guess = guess.replace('?', letter, 1)
        if dictionary is None or guess in dictionary:
            yield guess

if __name__ == '__main__':
    # provide command line interface
    parser = argparse.ArgumentParser()
    parser.add_argument('word', help="A 5-character string\
    representing your previous guess. Use \"?\" character as a\
    placeholder for unknown letters.")
    parser.add_argument('available', help="A string of all possible\
    letters that can still be added to the word (minus those letters\
    known to be `present`). If it's possible for a letter to be\
    included twice, that letter should be in the `available` string\
    twice, etc. If you know a letter is in the word somewhere, it\
    should be provided as `present` instead of `available`. If you\
    *know* a letter is in the word somewhere ONCE, and it *might* be\
    in the word TWICE, it should be in `available` once and `present`\
    once.")
    parser.add_argument('--present', help="An optional string\
    of letters that we know are in the word somewhere, but we don't\
    know their position in the word yet.")
    parser.add_argument('--dictionary', help="An optional list of all\
    possible words. Surround by quotes and separate with spaces.")
    args = parser.parse_args()
    _cli_parse(args)
