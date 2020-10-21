from .core import Normalizer, Builder

__normalizer__ = None

def build_normalizer(filename=None):
    global __normalizer__
    __builder__ = Builder()
    __normalizer__ = __builder__.build_normalizer(filename)

def normalize(source_string, word_separator=' ', normalizer_option=0):
    global __normalizer__
    if not  __normalizer__:
        build_normalizer()
    result = __normalizer__.normalize(source_string, word_separator, normalizer_option)
    return result
