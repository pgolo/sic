from .core import Normalizer, Builder

__normalizer__ = None
__normalizer_result__ = None

def __getattr__(name):
    global __normalizer_result__
    if name == 'result':
        return __normalizer_result__
    raise AttributeError('Module "{__name__}" has no attribute "{name}".')

def build_normalizer(endpoint=None):
    """This method loads configuration and constructs Normalizer with this configuration.

    Args:
        *endpoint* is either sic.Model instance, or path to XML file defining the configuration of a tokenizer
    """
    global __normalizer__
    __builder__ = Builder()
    __normalizer__ = __builder__.build_normalizer(endpoint)

def normalize(*args, **kwargs):
    """This function zooms through the provided string character by character
    and returns string which is normalized representation of a given string.

    Args:
        *source_string* is input string to normalize
        *word_separator* is word separator to consider (must be single character)
        *normalizer_option* is integer either 0 (normal, default), 1 (list), or 2 (set)
    """
    kwargs['source_string'] = args[0] if len(args) > 0 else kwargs['source_string'] if 'source_string' in kwargs else ''
    kwargs['word_separator'] = args[1] if len(args) > 1 else kwargs['word_separator'] if 'word_separator' in kwargs else ' '
    kwargs['normalizer_option'] = args[2] if len(args) > 2 else kwargs['normalizer_option'] if 'normalizer_option' in kwargs else 0
    kwargs['control_character'] = args[3] if len(args) > 3 else kwargs['control_character'] if 'control_character' in kwargs else '\x00'
    global __normalizer_result__
    if 'tokenizer_config' in kwargs:
        builder = Builder()
        normalizer = builder.build_normalizer(kwargs['tokenizer_config'])
        result = normalizer.normalize(kwargs['source_string'], kwargs['word_separator'], kwargs['normalizer_option'], kwargs['control_character'])
        __normalizer_result__ = normalizer.normalizer_result
        return result
    global __normalizer__
    if not  __normalizer__:
        build_normalizer()
    result = __normalizer__.normalize(kwargs['source_string'], kwargs['word_separator'], kwargs['normalizer_option'], kwargs['control_character'])
    __normalizer_result__ = __normalizer__.normalizer_result
    return result

def result():
    """This function returns normalization results of most recent normalization task.
    """
    return __normalizer_result__

def reset():
    """This method resets all loaded normalization rules.
    """
    global __normalizer__
    __normalizer__ = None

def save(filename):
    """This method pickles normalizer to a file.

    Args:
        *filename* is path/filename to save Normalizer object to
    """
    global __normalizer__
    __normalizer__.save(filename)

def load(filename):
    """This function unpickles normalizer from a file.

    Args:
        *filename* is path/filename to load Normalizer object from
    """
    global __normalizer__
    build_normalizer()
    __normalizer__.load(filename)
