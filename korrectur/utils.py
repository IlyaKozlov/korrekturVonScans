import random

from xkcdpass import xkcd_password as xp


def random_string(n):
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(wordfile=wordfile, min_length=5, max_length=8)
    words = xp.generate_xkcdpassword(mywords, numwords=n).split()
    return "".join(map(str.capitalize, words)) + "{:03d}".format(random.randint(0, 999))
