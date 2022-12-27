"""
Syllabification de mots en français.
"""

__author__ = "Heuron Patapon"
__email__ = "heuron-patapon@laposte.net"
__version__ = "1.1.1"

import re
import unittest
import doctest
import functools


import hpat.ezre as ezre
from hpat.xsampa import XSAMPA


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(__name__))
    return tests


class Syllable:
    LIQUIDS = ["ʁ", "l"]
    GLIDES = ["j", "w", "ɥ"]
    VOWELS = [
        "a", "ɛ", "e", "i",
        "ə", "œ", "ø", "y",
        "ɑ", "ɔ", "o", "u",
        "ɑ̃", "ɛ̃", "œ̃", "ɔ̃",
        # diphthongs:
        XSAMPA.to_ipa("u_^a"),
        XSAMPA.to_ipa("y_^i"),
        XSAMPA.to_ipa("i_^e"),
        XSAMPA.to_ipa("i_^E"),
    ]
    LIQUID_FRIENDLY = [
        "p", "b", "f", "v",
        "t", "d",
        "k", "g",
    ]
    CONSONANTS = [
        "p", "b", "f", "v", "m",
        "t", "d", "s", "z", "n",
        "k", "g", "ʃ", "ʒ", "ɲ",
        # dataset specific:
        "ŋ", "ʼ", "tʃ", "dʒ",
    ]

    V = ezre.Ezre.from_sequence(VOWELS, label="A")
    S = ezre.Ezre.from_sequence(["s"], label="S")
    L = ezre.Ezre.from_sequence(LIQUIDS, label="L")
    Y = ezre.Ezre.from_sequence(GLIDES, label="Y")
    C = (L | Y | ezre.Ezre.from_sequence(CONSONANTS)).as_("C")
    # beware: we work on reversed syllables:
    LC = (L + ezre.Ezre.from_sequence(LIQUID_FRIENDLY)).as_("LC")

    structure = (
        # it seems easier to reverse the word for the syllabification:
        C[:].group("coda")  # any coda without particular rule
        + V.group("nucleus")
        + (
            # semivowel:
            Y[:1]
            # onset:
            + (ezre.Ezre.from_str("ng") | LC | C)[:1]
            # extrasyllabic element:
            + (S[:1] + None | S[:1:min])
        ).group("onset")
    )

    pattern = structure.compiled
    is_complex = lambda x: len(x) != 1
    complex_sound = r"|".join(set(
        filter(is_complex, LIQUIDS + GLIDES + VOWELS + CONSONANTS)))

    __slots__ = ("onset", "nucleus", "coda")

    def __init__(self, onset, nucleus, coda):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda

    @property
    def ipa(self):
        return str(self)

    def __str__(self):
        return "".join((self.onset, self.nucleus, self.coda))

    def __repr__(self):
        return repr((self.onset, self.nucleus, self.coda))


class Syllabification:
    __slots__ = ("syllables", )

    def __init__(self, *syllables):
        self.syllables = syllables

    @property
    def ipa(self):
        return str(self)

    def __str__(self):
        return ".".join(map(str, self.syllables))

    def __repr__(self):
        return repr(self.syllables)

    def __iter__(self):
        return iter(self.syllables)

    def __len__(self):
        return len(self.syllables)

    def __getitem__(self, key):
        return self.syllables[key]


@functools.cache
def mirrored(word: str) -> str:
    """
    Reverse the word, safe for complex sounds. 

    Examples
    --------
    ~~~python
    >>> mirrored("kalkyləʁjɔ̃")
    'ɔ̃jʁəlyklak'

    ~~~
    """
    return re.sub(Syllable.complex_sound, lambda m: m.group()[::-1], word)[::-1]


def syllabify(word: str) -> Syllabification:
    """
    Break a word pronunciation written in IPA into syllables. 

    Examples
    --------
    ~~~python
    >>> syllabify("aʁbʁ")
    (('', 'a', 'ʁbʁ'),)
    >>> syllabify("kadavʁ")
    (('k', 'a', ''), ('d', 'a', 'vʁ'))
    >>> syllabify("kalkyləʁjɔ̃")
    (('k', 'a', 'l'), ('k', 'y', ''), ('l', 'ə', ''), ('ʁj', 'ɔ̃', ''))
    >>> syllabify("kɑ̃bʁje")
    (('k', 'ɑ̃', ''), ('bʁj', 'e', ''))
    >>> syllabify("distʁibɥe")
    (('d', 'i', 's'), ('tʁ', 'i', ''), ('bɥ', 'e', ''))
    >>> syllabify("ɛ̃stʁyksjɔ̃")
    (('', 'ɛ̃', 's'), ('tʁ', 'y', 'k'), ('sj', 'ɔ̃', ''))
    >>> syllabify("stʁiktəmɑ̃")
    (('stʁ', 'i', 'k'), ('t', 'ə', ''), ('m', 'ɑ̃', ''))
    >>> syllabify("ʼaʃvjɑ̃d")
    (('ʼ', 'a', 'ʃ'), ('vj', 'ɑ̃', 'd'))
    >>> syllabify("ɛlʁɔ̃")
    (('', 'ɛ', 'l'), ('ʁ', 'ɔ̃', ''))
    >>> syllabify("aʁləkɛ̃")
    (('', 'a', 'ʁ'), ('l', 'ə', ''), ('k', 'ɛ̃', ''))
    >>> syllabify("kʁɛmʁi")
    (('kʁ', 'ɛ', 'm'), ('ʁ', 'i', ''))
    >>> syllabify("fɛʁɔnʁi")
    (('f', 'ɛ', ''), ('ʁ', 'ɔ', 'n'), ('ʁ', 'i', ''))
    >>> syllabify("bwazʁi")
    (('bw', 'a', 'z'), ('ʁ', 'i', ''))
    >>> syllabify("bʁasʁi")
    (('bʁ', 'a', 's'), ('ʁ', 'i', ''))
    >>> syllabify("ivʁɔɲʁi")
    (('', 'i', ''), ('vʁ', 'ɔ', 'ɲ'), ('ʁ', 'i', ''))
    >>> syllabify("sɛʃʁɛs")
    (('s', 'ɛ', 'ʃ'), ('ʁ', 'ɛ', 's'))
    >>> syllabify("sɔ̃ʒʁi")
    (('s', 'ɔ̃', 'ʒ'), ('ʁ', 'i', ''))
    >>> syllabify("devlɔpmɑ̃")
    (('d', 'e', ''), ('vl', 'ɔ', 'p'), ('m', 'ɑ̃', ''))
    >>> syllabify("/guvɛʁnœʁ ʒeneʁal/")
    (('g', 'u', ''), ('v', 'ɛ', 'ʁ'), ('n', 'œ', 'ʁ'), ('ʒ', 'e', ''), ('n', 'e', ''), ('ʁ', 'a', 'l'))
    >>> syllabify("abɛsɑ̃t")
    (('', 'a', ''), ('b', 'ɛ', ''), ('s', 'ɑ̃', 't'))
    >>> syllabify(XSAMPA.to_ipa("Egl@"))
    (('', 'ɛ', ''), ('gl', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("Ebl@"))
    (('', 'ɛ', ''), ('bl', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("Evl@"))
    (('', 'ɛ', ''), ('vl', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("EgR@"))
    (('', 'ɛ', ''), ('gʁ', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("EtR@"))
    (('', 'ɛ', ''), ('tʁ', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("REgl@mA~"))
    (('ʁ', 'ɛ', ''), ('gl', 'ə', ''), ('m', 'ɑ̃', ''))
    >>> syllabify(XSAMPA.to_ipa("afliZA~"))
    (('', 'a', ''), ('fl', 'i', ''), ('ʒ', 'ɑ̃', ''))
    >>> syllabify(XSAMPA.to_ipa("egliz@"))
    (('', 'e', ''), ('gl', 'i', ''), ('z', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("gRavite"))
    (('gʁ', 'a', ''), ('v', 'i', ''), ('t', 'e', ''))
    >>> syllabify(XSAMPA.to_ipa("eklezjastik"))
    (('', 'e', ''), ('kl', 'e', ''), ('zj', 'a', 's'), ('t', 'i', 'k'))
    >>> syllabify(XSAMPA.to_ipa("stRyktyR@"))
    (('stʁ', 'y', 'k'), ('t', 'y', ''), ('ʁ', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("stRyktyR"))
    (('stʁ', 'y', 'k'), ('t', 'y', 'ʁ'))
    >>> syllabify(XSAMPA.to_ipa("gnom@"))
    (('gn', 'o', ''), ('m', 'ə', ''))
    >>> syllabify(XSAMPA.to_ipa("agnOstik"))
    (('', 'a', ''), ('gn', 'ɔ', 's'), ('t', 'i', 'k'))
    >>> syllabify(XSAMPA.to_ipa("sHivR@"))
    (('sɥ', 'i', ''), ('vʁ', 'ə', ''))

    # TODO: psy, psaume, see issue #2

    ~~~
    """
    # initialization:
    syllables = list()
    syllables_append = syllables.append
    # actual work:
    for match in re.finditer(Syllable.pattern, mirrored(word)):
        match_group = match.group
        onset = mirrored(match_group("onset"))
        nucleus = mirrored(match_group("nucleus"))
        coda = mirrored(match_group("coda"))
        syllables_append(Syllable(onset, nucleus, coda))
    return Syllabification(*reversed(syllables))


if __name__ == '__main__':
    doctest.testmod()
