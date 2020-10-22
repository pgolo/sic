from .core import Normalizer, Builder

__normalizer__ = None

def build_normalizer(filename=None):
    global __normalizer__
    __builder__ = Builder()
    __normalizer__ = __builder__.build_normalizer(filename)

def normalize(*args, **kwargs):
    kwargs['source_string'] = args[0] if len(args) > 0 else kwargs['source_string'] if 'source_string' in kwargs else ''
    kwargs['word_separator'] = args[1] if len(args) > 1 else kwargs['word_separator'] if 'word_separator' in kwargs else ' '
    kwargs['normalizer_option'] = args[2] if len(args) > 2 else kwargs['normalizer_option'] if 'normalizer_option' in kwargs else 0
    if 'tokenizer_config' in kwargs:
        builder = Builder()
        normalizer = builder.build_normalizer(kwargs['tokenizer_config'])
        result = normalizer.normalize(kwargs['source_string'], kwargs['word_separator'], kwargs['normalizer_option'])
        return result
    global __normalizer__
    if not  __normalizer__:
        build_normalizer()
    result = __normalizer__.normalize(kwargs['source_string'], kwargs['word_separator'], kwargs['normalizer_option'])
    return result

def reset():
    global __normalizer__
    __normalizer__ = None
