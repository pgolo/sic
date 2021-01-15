import os
import sys
import unittest

class TestNormalizer(unittest.TestCase):

    assets_dir = './test/assets'
    tokenizer_filenames = [
        'tokenizer_basic_ci.xml',
        'tokenizer_basic_cs.xml',
        'tokenizer_bypass.xml',
        'tokenizer_ci_child_of_ci_parent.xml',
        'tokenizer_ci_child_of_cs_parent.xml',
        'tokenizer_cs_child_of_ci_parent.xml',
        'tokenizer_cs_child_of_cs_parent.xml',
        'tokenizer_grandchild_ci_of_ci_ci.xml',
        'tokenizer_grandchild_ci_of_ci_cs.xml',
        'tokenizer_grandchild_ci_of_cs_ci.xml',
        'tokenizer_grandchild_ci_of_cs_cs.xml',
        'tokenizer_grandchild_cs_of_ci_ci.xml',
        'tokenizer_grandchild_cs_of_ci_cs.xml',
        'tokenizer_grandchild_cs_of_cs_ci.xml',
        'tokenizer_grandchild_cs_of_cs_cs.xml',
        'tokenizer_parent_ci.xml',
        'tokenizer_parent_cs.xml',
        'tokenizer_split_extension.xml',
        'tokenizer_split_replace.xml'
    ]

    def normalize(self, config_filename, string):
        builder = sic.Builder()
        worker = builder.build_normalizer('%s/%s' % (self.assets_dir, config_filename))
        word_separator = ' '
        options = {0: 'normal', 1: 'list', 2: 'set'}
        return (worker.name, {options[x]: worker.normalize(string, word_separator, x) for x in [0, 1, 2]})

    def assert_normalization(self, tokenizer_filename, tokenizer_name, testcases):
        for testcase in testcases:
            name, result = (self.normalize(tokenizer_filename, testcase['original']))
            assert name == tokenizer_name, 'Unexpected tokenizer name (expected "%s", got "%s" instead).' % (tokenizer_name, name)
            for option in ['normal', 'list', 'set']:
                assert result[option] == testcase['expected'][option], 'Unexpected normalization result for %s (option "%s"): "%s" => "%s" (expected "%s").' % (name, option, testcase['original'], result[option], testcase['expected'][option])
        return True

    def assert_map(self, config_filename, testcases):
        for testcase in testcases:
            builder = sic.Builder()
            worker = builder.build_normalizer('%s/%s' % (self.assets_dir, config_filename))
            _ = worker.normalize(testcase['original'], testcase['word_separator'], testcase['option'])
            result = worker.result
            assert result['original'] == testcase['original'], 'Case "%s": Original strings in input and output do not match for %s (word_separator="%s", option="%s": "%s" => "%s" (expected "%s").' % (testcase['original'], worker.name, testcase['word_separator'], testcase['option'], testcase['original'], result['original'], testcase['original'])
            assert result['normalized'] == testcase['normalized'], 'Case "%s": Unexpected normalization result for %s (word_separator="%s", option "%s"): "%s" => "%s" (expected "%s").' % (testcase['original'], worker.name, testcase['word_separator'], testcase['option'], testcase['original'], result['normalized'], testcase['normalized'])
            assert len(result['map']) == len(testcase['map']), 'Case "%s": Unexpected map length for %s: expected %d, got %d.' % (testcase['original'], worker.name, len(testcase['map']), len(result['map']))
            if testcase['option'] == 0:
                assert len(result['map']) == len(result['normalized']), 'Case "%s": Legth of map does not match length of normalized string (config %s, expected %d; got normalized=%d, map=%d instead).' % (testcase['original'], worker.name, len(testcase['map']), len(result['normalized']), len(result['map']))
                for i, j in enumerate(result['map']):
                    if result['normalized'][i] != testcase['word_separator']:
                        assert testcase['map'][i] == j, 'Case "%s": Unexpected map for %s (word_separator="%s", option "%s"): value at index %d is supposed to be %d (got %d instead), unless character at that position is "%s" (got "%s" instead).' % (testcase['original'], worker.name, testcase['word_separator'], testcase['option'], i, testcase['map'][i], j, testcase['word_separator'], result['normalized'][i])
        return True

    def test_expose_tokenizer(self):
        builder = sic.Builder()
        for filename in self.tokenizer_filenames:
            ret = builder.expose_tokenizer('%s/%s' % (self.assets_dir, filename))
            assert type(ret) == tuple, 'Expected tuple, returned %s' % str(type(ret))
            assert len(ret) == 2, 'Expected length 2, returned %s' % str(len(ret))
            assert type(ret[0]) == str, 'Expected ret[0] to be str, returned %s' % str(type(ret[0]))
            assert type(ret[1]) == str, 'Expected ret[1] to be str, returned %s' % str(type(ret[1]))

    def test_build_normalizer(self):
        builder = sic.Builder()
        for filename in self.tokenizer_filenames:
            ret = builder.build_normalizer('%s/%s' % (self.assets_dir, filename))
            assert type(ret) == sic.Normalizer, 'Expected Normalizer, returned %s' % str(type(ret))

    def test_tokenizer_basic_ci(self):
        testcases = [
            {
                'original': 'abc123-DEF123ghi234def-555DEF ABC',
                'expected': {
                    'normal': 'abc 123 - def 123 ghi 234 def - 555 def abc',
                    'list': '- - 123 123 234 555 abc abc def def def ghi',
                    'set': '- 123 234 555 abc def ghi'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_basic_ci.xml', 'tokenizer_basic_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_basic_cs(self):
        testcases = [
            {
                'original': 'abc123-DEF123ghi234def-555DEF ABC',
                'expected': {
                    'normal': 'abc 123 - DEF 123 ghi 234 def - 555 DEF ABC',
                    'list': '- - 123 123 234 555 ABC DEF DEF abc def ghi',
                    'set': '- 123 234 555 ABC DEF abc def ghi'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_basic_cs.xml', 'tokenizer_basic_cs', testcases) == True, 'Something is wrong.'

    def test_tokenizer_bypass(self):
        testcases = [
            {
                'original': 'abc123-DEF123ghi234def-555DEF ABC',
                'expected': {
                    'normal': 'abc123-DEF123ghi234def-555DEF ABC',
                    'list': 'abc123-DEF123ghi234def-555DEF ABC',
                    'set': 'abc123-DEF123ghi234def-555DEF ABC'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_bypass.xml', 'tokenizer_bypass', testcases) == True, 'Something is wrong.'

    def test_tokenizer_ci_child_of_ci_parent(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD, ALPHAbetaGAmma qwebetaqwe',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild , alpha beta gamma qwe beta qwe',
                    'list': ', , - - - alpha beta beta gamma hey is qwe qwe replacetochild replacetoparent this',
                    'set': ', - alpha beta gamma hey is qwe replacetochild replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_ci_child_of_ci_parent.xml', 'test_ci_child_of_ci_parent', testcases) == True, 'Something is wrong.'

    def test_tokenizer_ci_child_of_cs_parent(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD, ALPHAbetaGAmma',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild , alpha beta gamma',
                    'list': ', , - - - alpha beta gamma hey is replacetochild replacetoparent this',
                    'set': ', - alpha beta gamma hey is replacetochild replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_ci_child_of_cs_parent.xml', 'test_ci_child_of_cs_parent', testcases) == True, 'Something is wrong.'

    def test_tokenizer_cs_child_of_ci_parent(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD, ALPHAbetaGAmma',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild , alpha beta gamma',
                    'list': ', , - - - alpha beta gamma hey is replacetochild replacetoparent this',
                    'set': ', - alpha beta gamma hey is replacetochild replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_ci_child_of_cs_parent.xml', 'test_ci_child_of_cs_parent', testcases) == True, 'Something is wrong.'

    def test_tokenizer_cs_child_of_cs_parent(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD, ALPHAbetaGAmma',
                'expected': {
                    'normal': 'this - is replaCeToPARENT - EMPTYONE hey , - replaCeToCHILD , ALPHA beta GAmma',
                    'list': ', , - - - ALPHA EMPTYONE GAmma beta hey is replaCeToCHILD replaCeToPARENT this',
                    'set': ', - ALPHA EMPTYONE GAmma beta hey is replaCeToCHILD replaCeToPARENT this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_cs_child_of_cs_parent.xml', 'test_cs_child_of_cs_parent', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_ci_of_ci_ci(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild / replacetogchld , alpha beta gamma /',
                    'list': ', , - - - / / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this',
                    'set': ', - / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_ci_of_ci_ci.xml', 'test_grandchild_ci_of_ci_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_ci_of_ci_cs(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild / replacetogchld , alpha beta gamma /',
                    'list': ', , - - - / / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this',
                    'set': ', - / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_ci_of_ci_cs.xml', 'test_grandchild_ci_of_ci_cs', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_ci_of_cs_ci(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild / replacetogchld , alpha beta gamma /',
                    'list': ', , - - - / / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this',
                    'set': ', - / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_ci_of_cs_ci.xml', 'test_grandchild_ci_of_cs_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_ci_of_cs_cs(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild / replacetogchld , alpha beta gamma /',
                    'list': ', , - - - / / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this',
                    'set': ', - / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_ci_of_cs_cs.xml', 'test_grandchild_ci_of_cs_cs', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_cs_of_ci_ci(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild / replacetogchld , alpha beta gamma /',
                    'list': ', , - - - / / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this',
                    'set': ', - / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_cs_of_ci_ci.xml', 'test_grandchild_cs_of_ci_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_cs_of_ci_cs(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild / replacetogchld , alpha beta gamma /',
                    'list': ', , - - - / / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this',
                    'set': ', - / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_cs_of_ci_cs.xml', 'test_grandchild_cs_of_ci_cs', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_cs_of_cs_ci(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replacetoparent - hey , - replacetochild / replacetogchld , alpha beta gamma /',
                    'list': ', , - - - / / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this',
                    'set': ', - / alpha beta gamma hey is replacetochild replacetogchld replacetoparent this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_cs_of_cs_ci.xml', 'test_grandchild_cs_of_cs_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_grandchild_cs_of_cs_cs(self):
        testcases = [
            {
                'original': 'this-is replaceFromPARENT-EMPTYONE hey, emptyTwo-replaceFromCHILD/replaceFromGCHLD, ALPHAbetaGAmma emptythree/emptyThree',
                'expected': {
                    'normal': 'this - is replaCeToPARENT - EMPTYONE hey , - replaCeToCHILD / replaCeToGCHLD , ALPHA beta GAmma emptythree /',
                    'list': ', , - - - / / ALPHA EMPTYONE GAmma beta emptythree hey is replaCeToCHILD replaCeToGCHLD replaCeToPARENT this',
                    'set': ', - / ALPHA EMPTYONE GAmma beta emptythree hey is replaCeToCHILD replaCeToGCHLD replaCeToPARENT this'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_grandchild_cs_of_cs_cs.xml', 'test_grandchild_cs_of_cs_cs', testcases) == True, 'Something is wrong.'

    def test_replace_token_after_split_token_agglutinated(self):
        testcases = [
            {
                'original': 'alphareplacefromparent',
                'expected': {
                    'normal': 'alpha replacetoparent',
                    'list': 'alpha replacetoparent',
                    'set': 'alpha replacetoparent'
                }
            },
            {
                'original': 'replacefromparentalpha',
                'expected': {
                    'normal': 'replacetoparent alpha',
                    'list': 'alpha replacetoparent',
                    'set': 'alpha replacetoparent'
                }
            },
            {
                'original': 'replacefromparentalphareplacefromparent',
                'expected': {
                    'normal': 'replacetoparent alpha replacetoparent',
                    'list': 'alpha replacetoparent replacetoparent',
                    'set': 'alpha replacetoparent'
                }
            },
            {
                'original': 'alphareplacefromparentalpha',
                'expected': {
                    'normal': 'alpha replacetoparent alpha',
                    'list': 'alpha alpha replacetoparent',
                    'set': 'alpha replacetoparent'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_parent_ci.xml', 'test_ci_parent', testcases) == True, 'Something is wrong.'

    def test_tokenizer_multiple_tokens_ci(self):
        testcases = [
            {
                'original': 'here are three different words, I say',
                'expected': {
                    'normal': 'here are two words , i say',
                    'list': ', are here i say two words',
                    'set': ', are here i say two words'
                }
            },
            {
                'original': 'several words can be turned into one',
                'expected': {
                    'normal': 'word can be turned into different words',
                    'list': 'be can different into turned word words',
                    'set': 'be can different into turned word words'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_multiple_tokens_ci.xml', 'tokenizer_multiple_tokens_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_multiple_tokens_cs(self):
        testcases = [
            {
                'original': 'here are three Different words, I say',
                'expected': {
                    'normal': 'here are three Different words , I say',
                    'list': ', Different I are here say three words',
                    'set': ', Different I are here say three words'
                }
            },
            {
                'original': 'several words can be turned into One',
                'expected': {
                    'normal': 'word can be turned into One',
                    'list': 'One be can into turned word',
                    'set': 'One be can into turned word'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_multiple_tokens_cs.xml', 'tokenizer_multiple_tokens_cs', testcases) == True, 'Something is wrong.'

    def test_tokenizer_multiple_split_actions_in_one_instruction(self):
        testcases = [
            {
                'original': 'aaaaz zaaaaz zaaaa aaabz zaaabz zaaab aaacz zaaacz zaaac aaadz zaaadz zaaad aaaez zaaaez zaaae aaafz zaaafz zaaaf lllz zlllz zlll mmmz zmmmz zmmm rrrz zrrrz zrrr lmz zlmz zlm mlz zmlz zml rmz zrmz zrm mrz zmrz zmr lrz zlrz zlr rlz zrlz zrl',
                'expected': {
                    'normal': 'aaaa z z aaaa z z aaaa aaab z z aaab z z aaab aaac z z aaac z z aaac aaad z z aaad z z aaad aaae z z aaae z z aaae aaaf z z aaaf z z aaaf lll z zlllz zlll mmmz z mmm z zmmm rrrz zrrrz z rrr lm z z lm z zlm ml z z ml z zml rmz z rm z z rm mrz z mr z z mr lr z zlrz z lr rl z zrlz z rl',
                    'list': 'aaaa aaaa aaaa aaab aaab aaab aaac aaac aaac aaad aaad aaad aaae aaae aaae aaaf aaaf aaaf lll lm lm lr lr ml ml mmm mmmz mr mr mrz rl rl rm rm rmz rrr rrrz z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z z zlll zlllz zlm zlrz zml zmmm zrlz zrrrz',
                    'set': 'aaaa aaab aaac aaad aaae aaaf lll lm lr ml mmm mmmz mr mrz rl rm rmz rrr rrrz z zlll zlllz zlm zlrz zml zmmm zrlz zrrrz'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_split_extension.xml', 'test_split_extension', testcases) == True, 'Something is wrong.'

    def test_tokenizer_split_replace(self):
        testcases = [
            {
                'original': 'qweαrty αqwerty qwertyα ααα',
                'expected': {
                    'normal': 'qwe alpha rty alpha qwerty qwerty alpha alpha alpha alpha',
                    'list': 'alpha alpha alpha alpha alpha alpha qwe qwerty qwerty rty',
                    'set': 'alpha qwe qwerty rty'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_split_replace.xml', 'test_split_replace', testcases) == True, 'Something is wrong.'

    def test_tokenizer_tokens_overlap_ci(self):
        testcases = [
            {
                'original': 'abc123defalpha',
                'expected': {
                    'normal': 'abc 123 def alpha',
                    'list': '123 abc alpha def',
                    'set': '123 abc alpha def'
                }
            },
            {
                'original': 'abc123defalphabe',
                'expected': {
                    'normal': 'abc 123 def alpha be',
                    'list': '123 abc alpha be def',
                    'set': '123 abc alpha be def'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_tokens_overlap_ci.xml', 'test_tokens_overlap_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_bypass(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'This is test for inactive tokenizer.',
                'normalized': 'This is test for inactive tokenizer.',
                'map': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
            }
        ]
        assert self.assert_map('tokenizer_bypass.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_only_tokenize(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'ABC123def-ghi.',
                'normalized': 'abc 123 def - ghi .',
                'map': [0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 13]
            }
        ]
        assert self.assert_map('tokenizer_basic_ci.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_split(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'abcgammadef',
                'normalized': 'abc gamma def',
                'map': [0, 1, 2, 3, 3, 4, 5, 6, 7, 8, 8, 9, 10]
            }
        ]
        assert self.assert_map('tokenizer_ci_child_of_ci_parent.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_replace_to_longer(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'give me one please',
                'normalized': 'give me different words please',
                'map': [0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 11, 12, 13, 14, 15, 16, 17]
            }
        ]
        assert self.assert_map('tokenizer_multiple_tokens_ci.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_replace_to_shorter(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'give me several words please',
                'normalized': 'give me word please',
                'map': [0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 21, 22, 23, 24, 25, 26, 27]
            }
        ]
        assert self.assert_map('tokenizer_multiple_tokens_ci.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_replace_to_nothing(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'abc,emptytwo,def',
                'normalized': 'abc , , def',
                'map': [0, 1, 2, 3, 3, 12, 12, 13, 13, 14, 15]
            }
        ]
        assert self.assert_map('tokenizer_ci_child_of_ci_parent.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_replace_character(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'Dr. Emmet is Brown',
                'normalized': 'Dr . Emmet is brown',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            }
        ]
        assert self.assert_map('tokenizer_parent_cs.xml', testcases) == True, 'Something is wrong.'


    def test_tokenizer_map_split_replace_to_longer(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplitshort.',
                'normalized': 'un split longer .',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 12, 12]
            },
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplitshort',
                'normalized': 'un split longer',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 11]
            }
        ]
        assert self.assert_map('tokenizer_split_replace_for_map.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_split_replace_to_shorter(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplitsuperlong.',
                'normalized': 'un split shorter .',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7, 16, 16]
            },
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplitsuperlong',
                'normalized': 'un split shorter',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 15]
            }
        ]
        assert self.assert_map('tokenizer_split_replace_for_map.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_split_replace_to_nothing(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplitnothing.',
                'normalized': 'un split .',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 14, 14]
            },
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplitnothing',
                'normalized': 'un split',
                'map': [0, 1, 2, 2, 3, 4, 5, 13]
            }
        ]
        assert self.assert_map('tokenizer_split_replace_for_map.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_split_replace_character(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplity.',
                'normalized': 'un split x .',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 7, 7, 8, 8]
            },
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'unsplity',
                'normalized': 'un split x',
                'map': [0, 1, 2, 2, 3, 4, 5, 6, 7, 7]
            }
        ]
        assert self.assert_map('tokenizer_split_replace_for_map.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_option_list(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 1,
                'original': 'ABC123def-ghi-jkl.',
                'normalized': '- - . 123 abc def ghi jkl',
                'map': []
            }
        ]
        assert self.assert_map('tokenizer_basic_ci.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_option_set(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 2,
                'original': 'ABC123def-ghi-jkl.',
                'normalized': '- . 123 abc def ghi jkl',
                'map': []
            }
        ]
        assert self.assert_map('tokenizer_basic_ci.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_default(self):
        builder = sic.Builder()
        worker = builder.build_normalizer()
        testcase = 'Abc123def-ghdeLtai456-jkl'
        expected = 'abc 123 def - gh delta i 456 - jkl'
        tokenized = worker.normalize(testcase)
        assert tokenized == expected, 'Unexpected tokenization result for default config: "%s" => "%s" (expected "%s")' % (testcase, tokenized, expected)

    def test_tokenizer_map_nothing(self):
        testcases = [
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'nothing.',
                'normalized': '.',
                'map': [7]
            },
            {
                'word_separator': ' ',
                'option': 0,
                'original': 'nothing',
                'normalized': '',
                'map': []
            }
        ]
        assert self.assert_map('tokenizer_split_replace_for_map.xml', testcases) == True, 'Something is wrong.'

    def test_tokenizer_plurals_left(self):
        testcases = [
            {
                'original': 'plurals plurals',
                'expected': {
                    'normal': 'lurals lurals',
                    'list': 'lurals lurals',
                    'set': 'lurals'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_plurals_left.xml', 'test_plurals', testcases) == True, 'Something is wrong.'

    def test_tokenizer_plurals_middle(self):
        testcases = [
            {
                'original': 'plurals plurals',
                'expected': {
                    'normal': 'plu als plu als',
                    'list': 'als als plu plu',
                    'set': 'als plu'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_plurals_middle.xml', 'test_plurals', testcases) == True, 'Something is wrong.'

    def test_tokenizer_plurals_right(self):
        testcases = [
            {
                'original': 'plurals plurals',
                'expected': {
                    'normal': 'plural plural',
                    'list': 'plural plural',
                    'set': 'plural'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_plurals_right.xml', 'test_plurals', testcases) == True, 'Something is wrong.'

    def test_tokenizer_plurals_all(self):
        testcases = [
            {
                'original': 'plurals plurals',
                'expected': {
                    'normal': 'lu al lu al',
                    'list': 'al al lu lu',
                    'set': 'al lu'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_plurals_all.xml', 'test_plurals', testcases) == True, 'Something is wrong.'

    def test_tokenizer_no_plurals_right(self):
        testcases = [
            {
                'original': 'plurals plurals',
                'expected': {
                    'normal': 'plurals plurals',
                    'list': 'plurals plurals',
                    'set': 'plurals'
                }
            }
        ]
        assert self.assert_normalization('tokenizer_no_plurals_right.xml', 'test_plurals', testcases) == True, 'Something is wrong.'
    
    def test_implicit_default_normalize(self):
        sic.reset()
        result = sic.normalize('nfkappab')
        expected = 'nf kappa b'
        if isinstance(sic.result, dict):
            result_map = sic.result
        else:
            result_map = sic.result()
        expected_map = {
            'original': 'nfkappab',
            'normalized': 'nf kappa b',
            'map': [0, 1, 7, 2, 3, 4, 5, 6, 7, 7],
            'r_map': [[0, 0], [1, 1], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [2, 9]]
        }
        assert result == expected, 'Expected "%s", got "%s".' % (expected, result)
        assert result_map == expected_map, 'Expected "%s", got "%s".' % (str(expected_map), str(result_map))

    def test_implicit_normalize_with_parameters(self):
        result = [
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_ci.xml' % (self.assets_dir)),
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_cs.xml' % (self.assets_dir)),
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_ci.xml' % (self.assets_dir), word_separator='|'),
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_cs.xml' % (self.assets_dir), word_separator='|'),
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_ci.xml' % (self.assets_dir), normalizer_option=1),
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_cs.xml' % (self.assets_dir), normalizer_option=1),
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_ci.xml' % (self.assets_dir), word_separator='|', normalizer_option=1),
            sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_cs.xml' % (self.assets_dir), word_separator='|', normalizer_option=1)
        ]
        expected = [
            'abc , def 123 ghi',
            'abc , Def 123 ghi',
            'abc|,|def|123|ghi',
            'abc|,|Def|123|ghi',
            ', 123 abc def ghi',
            ', 123 Def abc ghi',
            ',|123|abc|def|ghi',
            ',|123|Def|abc|ghi'
        ]
        for i in range(0, len(result)-1):
            assert result[i] == expected[i], 'Test case #%d: expected "%s", got "%s".' % (i, expected[i], result[i])

    def test_implicit_build_normalize(self):
        result, expected = [], []
        sic.build_normalizer('%s/tokenizer_basic_ci.xml' % (self.assets_dir))
        result.append(sic.normalize('abc,Def123ghi'))
        expected.append('abc , def 123 ghi')
        sic.build_normalizer('%s/tokenizer_basic_cs.xml' % (self.assets_dir))
        result.append(sic.normalize('abc,Def123ghi'))
        expected.append('abc , Def 123 ghi')
        result.append(sic.normalize('abc,Def123ghi', tokenizer_config='%s/tokenizer_basic_ci.xml' % (self.assets_dir)))
        expected.append('abc , def 123 ghi')
        result.append(sic.normalize('abc,Def123ghi'))
        expected.append('abc , Def 123 ghi')
        for i in range(0, len(result)-1):
            assert result[i] == expected[i], 'Test case #%d: expected "%s", got "%s".' % (i, expected[i], result[i])

    def test_ad_hoc_model_empty(self):
        model = sic.Model()
        model.case_sensitive = False
        expected = 'set\tcs\t0\n'
        result = str(model)
        assert result == expected, 'Expected "%s", got "%s".' % (expected, result)

    def test_ad_hoc_model_add_rule(self):
        model = sic.Model()
        model.case_sensitive = False
        model.add_rule(sic.ReplaceToken('bad', 'good'))
        expected = 'set\tcs\t0\nr\tgood\tbad\n'
        result = str(model)
        assert result == expected, 'Expected "%s", got "%s".' % (expected, result)

    def test_ad_hoc_model_remove_rule(self):
        model = sic.Model()
        model.case_sensitive = False
        model.add_rule(sic.ReplaceToken('bad', 'good'))
        model.add_rule(sic.ReplaceToken('worse', 'better'))
        model.remove_rule(sic.ReplaceToken('bad', 'good'))
        expected = 'set\tcs\t0\nr\tbetter\tworse\n'
        result = str(model)
        assert result == expected, 'Expected "%s", got "%s".' % (expected, result)

    def test_ad_hoc_model_direct(self):
        model = sic.Model()
        model.case_sensitive = False
        model.add_rule(sic.SplitToken('beta', 'lmr'))
        normalizer = sic.Normalizer(None)
        normalizer.make_tokenizer(str(model))
        expected = 'a beta z'
        result = normalizer.normalize('abetaz')
        assert result == expected, 'Expected "%s", got "%s".' % (expected, result)

    def test_ad_hoc_model_builder(self):
        builder = sic.Builder()
        model = sic.Model()
        model.add_rule(sic.SplitToken('beta', 'lmr'))
        normalizer = builder.build_normalizer(model)
        expected = 'a beta z'
        result = normalizer.normalize('abetaz')
        assert result == expected, 'Expected "%s", got "%s".' % (expected, result)

    def test_ad_hoc_model_implicit(self):
        model = sic.Model()
        model.add_rule(sic.SplitToken('beta', 'lmr'))
        sic.build_normalizer(model)
        expected = 'a beta z'
        result = sic.normalize('abetaz')
        assert result == expected, 'Expected "%s", got "%s".' % (expected, result)

    def test_save_load_compiled_save_explicit_load_explicit(self):
        test_string = 'original string, transformed string'
        expected = 'transformed string , transformed string'
        pickled_path = '%s/test_save_load_compiled_save_explicit_load_explicit.pic' % (self.assets_dir)
        builder = sic.Builder()
        normalizer1 = builder.build_normalizer('%s/tokenizer_replace_token.xml' % (self.assets_dir))
        normalized1 = normalizer1.normalize(test_string)
        normalizer1.save(pickled_path)
        normalizer2 = sic.Normalizer()
        normalizer2.load(pickled_path)
        os.remove(pickled_path)
        normalized2 = normalizer2.normalize(test_string)
        assert expected == normalized1, 'Expected "%s", got "%s".' % (expected, normalized1)
        assert expected == normalized2, 'Expected "%s", got "%s".' % (expected, normalized2)

    def test_save_load_compiled_save_explicit_load_implicit(self):
        test_string = 'original string, transformed string'
        expected = 'transformed string , transformed string'
        pickled_path = '%s/test_save_load_compiled_save_explicit_load_implicit.pic' % (self.assets_dir)
        builder = sic.Builder()
        normalizer1 = builder.build_normalizer('%s/tokenizer_replace_token.xml' % (self.assets_dir))
        normalized1 = normalizer1.normalize(test_string)
        normalizer1.save(pickled_path)
        sic.load(pickled_path)
        os.remove(pickled_path)
        normalized2 = sic.normalize(test_string)
        assert expected == normalized1, 'Expected "%s", got "%s".' % (expected, normalized1)
        assert expected == normalized2, 'Expected "%s", got "%s".' % (expected, normalized2)

    def test_save_load_compiled_save_implicit_load_explicit(self):
        test_string = 'original string, transformed string'
        expected = 'transformed string , transformed string'
        pickled_path = '%s/test_save_load_compiled_save_implicit_load_explicit.pic' % (self.assets_dir)
        sic.build_normalizer('%s/tokenizer_replace_token.xml' % (self.assets_dir))
        normalized1 = sic.normalize(test_string)
        sic.save(pickled_path)
        normalizer2 = sic.Normalizer()
        normalizer2.load(pickled_path)
        os.remove(pickled_path)
        normalized2 = normalizer2.normalize(test_string)
        assert expected == normalized1, 'Expected "%s", got "%s".' % (expected, normalized1)
        assert expected == normalized2, 'Expected "%s", got "%s".' % (expected, normalized2)

    def test_save_load_compiled_save_implicit_load_implicit(self):
        test_string = 'original string, transformed string'
        expected = 'transformed string , transformed string'
        pickled_path = '%s/test_save_load_compiled_save_implicit_load_implicit.pic' % (self.assets_dir)
        sic.build_normalizer('%s/tokenizer_replace_token.xml' % (self.assets_dir))
        normalized1 = sic.normalize(test_string)
        sic.save(pickled_path)
        sic.reset()
        sic.load(pickled_path)
        os.remove(pickled_path)
        normalized2 = sic.normalize(test_string)
        assert expected == normalized1, 'Expected "%s", got "%s".' % (expected, normalized1)
        assert expected == normalized2, 'Expected "%s", got "%s".' % (expected, normalized2)

    def test_decode_rule(self):
        rule = sic.ReplaceCharacter('f', 't')
        decoded = rule.decode()
        expected = 'c\tt\tf\n'
        assert expected == decoded, 'Expected "%s", got "%s".' % (expected, decoded)

    def test_updated_compiled_normalizer(self):
        builder = sic.Builder()
        worker = builder.build_normalizer('%s/tokenizer_replace_token.xml' % (self.assets_dir))
        rules = [sic.ReplaceCharacter('t', 'n')]
        decoded = ''.join([x.decode() for x in rules])
        worker.make_tokenizer(decoded, update=True)
        test_string = 'original string, transformed string'
        normalized = worker.normalize(test_string)
        expected = 'transformed snring , nransformed snring'
        assert expected == normalized, 'Expected "%s", got "%s".' % (expected, normalized)

    def test_expanded_tokenizer(self):
        builder = sic.Builder()
        worker = builder.build_normalizer('%s/tokenizer_expanded.xml' % (self.assets_dir))
        test_string1 = '123abc456mmm'
        test_string2 = '123def456mmm'
        test_string3 = '123ghi456mmm'
        expected1 = '123 jkl 456 nnn'
        test_string4 = '123xyz456 nnn'
        expected2 = '123 www 456 nnn'
        test_string5 = '123qwe456'
        test_string6 = '123rty456'
        expected3 = '123 uiop 456'
        normalized1 = worker.normalize(test_string1)
        normalized2 = worker.normalize(test_string2)
        normalized3 = worker.normalize(test_string3)
        normalized4 = worker.normalize(test_string4)
        normalized5 = worker.normalize(test_string5)
        normalized6 = worker.normalize(test_string6)
        assert expected1 == normalized1, 'Expected "%s", got "%s".' % (expected1, normalized1)
        assert expected1 == normalized2, 'Expected "%s", got "%s".' % (expected1, normalized2)
        assert expected1 == normalized3, 'Expected "%s", got "%s".' % (expected1, normalized3)
        assert expected2 == normalized4, 'Expected "%s", got "%s".' % (expected2, normalized4)
        assert expected3 == normalized5, 'Expected "%s", got "%s".' % (expected3, normalized5)
        assert expected3 == normalized6, 'Expected "%s", got "%s".' % (expected3, normalized6)

    def test_conflict_converging_tokenizer(self):
        builder = sic.Builder()
        worker = builder.build_normalizer('%s/tokenizer_conflict_converging.xml' % (self.assets_dir))
        test_string1 = '123abc456mmm'
        test_string2 = '123def456mmm'
        test_string3 = '123ghi456mmm'
        expected1 = '123 jkl 456 nnn'
        test_string4 = '123xyz456 nnn'
        expected2 = '123 www 456 nnn'
        test_string5 = '123qwe456'
        test_string6 = '123rty456'
        expected3 = '123 uiop 456'
        normalized1 = worker.normalize(test_string1)
        normalized2 = worker.normalize(test_string2)
        normalized3 = worker.normalize(test_string3)
        normalized4 = worker.normalize(test_string4)
        normalized5 = worker.normalize(test_string5)
        normalized6 = worker.normalize(test_string6)
        assert expected1 == normalized1, 'Expected "%s", got "%s".' % (expected1, normalized1)
        assert expected1 == normalized2, 'Expected "%s", got "%s".' % (expected1, normalized2)
        assert expected1 == normalized3, 'Expected "%s", got "%s".' % (expected1, normalized3)
        assert expected2 == normalized4, 'Expected "%s", got "%s".' % (expected2, normalized4)
        assert expected3 == normalized5, 'Expected "%s", got "%s".' % (expected3, normalized5)
        assert expected3 == normalized6, 'Expected "%s", got "%s".' % (expected3, normalized6)

    def test_spelling_correction(self):
        builder = sic.Builder()
        worker = builder.build_normalizer('%s/tokenizer_spelling_ci.xml' % (self.assets_dir))
        worker2 = builder.build_normalizer()
        test_string1 = '123speling-Is-Corrected'; expected1 = '123spelling-Is-Corrected'; normalized1 = worker.normalize(test_string1, normalizer_option=3)
        test_string2 = '123Speling-Is-Corrected'; expected2 = '123Spelling-Is-Corrected'; normalized2 = worker.normalize(test_string2, normalizer_option=3)
        test_string3 = '123SPELING-Is-Corrected'; expected3 = '123SPELLING-Is-Corrected'; normalized3 = worker.normalize(test_string3, normalizer_option=3)
        test_string4 = '123SpeLING-Is-Corrected'; expected4 = '123spelling-Is-Corrected'; normalized4 = worker.normalize(test_string4, normalizer_option=3)
        test_string5 = '123speLIng-Is-Corrected'; expected5 = '123spelling-Is-Corrected'; normalized5 = worker.normalize(test_string5, normalizer_option=3)
        test_string6 = '123speLING-Is-Corrected'; expected6 = '123spelling-Is-Corrected'; normalized6 = worker.normalize(test_string6, normalizer_option=3)
        test_string7 = 'Halfsplitted Is Incorrect'; expected7 = 'Halfsplit Is Correct'; normalized7 = worker.normalize(test_string7, normalizer_option=3)
        test_string8 = 'Misspeling Is Incorrect'; expected8 = 'Misspelling Is Correct'; normalized8 = worker.normalize(test_string8, normalizer_option=3)
        test_string9 = 'Misspeling'; expected9 = 'Misspelling'; normalized9 = worker.normalize(test_string9, normalizer_option=3)
        test_string10 = 'Incorrect'; expected10 = 'Correct'; normalized10 = worker.normalize(test_string10, normalizer_option=3)
        test_string11 = 'Do Not, don''t Correct Me'; expected11 = 'Do Not, don''t Correct Me'; normalized11 = worker.normalize(test_string11, normalizer_option=3)
        test_string12 = 'Alpha-2-macroglobulin'; expected12 = 'Alpha-2-macroglobulin'; normalized12 = worker2.normalize(test_string12, normalizer_option=3)
        test_string13 = 'Alpha 1B-glycoprotein'; expected13 = 'Alpha 1B-glycoprotein'; normalized13 = worker2.normalize(test_string13, normalizer_option=3)
        test_string14 = 'Alpha 1B-glycoprotein'; expected14 = 'Alpha 1B-glycoprotein'; normalized14 = worker.normalize(test_string14, normalizer_option=3)
        test_string15 = 'AI3-05966'; expected15 = 'AI3-05966'; normalized15 = worker2.normalize(test_string15, normalizer_option=3)
        assert expected1 == normalized1, 'Expected "%s", got "%s".' % (expected1, normalized1)
        assert expected2 == normalized2, 'Expected "%s", got "%s".' % (expected2, normalized2)
        assert expected3 == normalized3, 'Expected "%s", got "%s".' % (expected3, normalized3)
        assert expected4 == normalized4, 'Expected "%s", got "%s".' % (expected4, normalized4)
        assert expected5 == normalized5, 'Expected "%s", got "%s".' % (expected5, normalized5)
        assert expected6 == normalized6, 'Expected "%s", got "%s".' % (expected6, normalized6)
        assert expected7 == normalized7, 'Expected "%s", got "%s".' % (expected7, normalized7)
        assert expected8 == normalized8, 'Expected "%s", got "%s".' % (expected8, normalized8)
        assert expected9 == normalized9, 'Expected "%s", got "%s".' % (expected9, normalized9)
        assert expected10 == normalized10, 'Expected "%s", got "%s".' % (expected10, normalized10)
        assert expected11 == normalized11, 'Expected "%s", got "%s".' % (expected11, normalized11)
        assert expected12 == normalized12, 'Expected "%s", got "%s".' % (expected12, normalized12)
        assert expected13 == normalized13, 'Expected "%s", got "%s".' % (expected13, normalized13)
        assert expected14 == normalized14, 'Expected "%s", got "%s".' % (expected14, normalized14)
        assert expected15 == normalized15, 'Expected "%s", got "%s".' % (expected15, normalized15)

    def test_spelling_correction_implicit(self):
        sic.build_normalizer('%s/tokenizer_spelling_ci.xml' % (self.assets_dir))
        test_string1 = 'AI3-05966'; expected1 = 'AI3-05966'; normalized1 = sic.normalize(test_string1, normalizer_option=3)
        sic.build_normalizer()
        test_string2 = 'AI3-05966'; expected2 = 'AI3-05966'; normalized2 = sic.normalize(test_string2, normalizer_option=3)
        assert expected1 == normalized1, 'Expected "%s", got "%s".' % (expected1, normalized1)
        assert expected2 == normalized2, 'Expected "%s", got "%s".' % (expected2, normalized2)

if __name__ == '__main__':
    sys.path.insert(0, '')
    import sic # pylint: disable=E0611,F0401
    unittest.main(exit=False)
    try:
        import bin as sic # pylint: disable=E0611,F0401
        unittest.main()
    except ModuleNotFoundError:
        print('Could not import module from /bin, test skipped.')
