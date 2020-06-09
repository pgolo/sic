import sys; sys.path.insert(0, '')
import unittest
import sic.core as tokenizer # pylint: disable=E0611,F0401

class TestTokenizer(unittest.TestCase):

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

    def tokenize(self, config_filename, string):
        tokenizer_builder = tokenizer.Builder()
        worker = tokenizer_builder.build_tokenizer('%s/%s' % (self.assets_dir, config_filename))
        word_separator = ' '
        options = {0: 'normal', 1: 'list', 2: 'set'}
        return (worker.name, {options[x]: worker.tokenize(string, word_separator, x) for x in [0, 1, 2]})

    def assert_tokenization(self, tokenizer_filename, tokenizer_name, testcases):
        for testcase in testcases:
            name, result = (self.tokenize(tokenizer_filename, testcase['original']))
            assert name == tokenizer_name, 'Unexpected tokenizer name (expected "%s", got "%s" instead).' % (tokenizer_name, name)
            for option in ['normal', 'list', 'set']:
                assert result[option] == testcase['expected'][option], 'Unexpected tokenization result for %s (option "%s"): "%s" => "%s" (expected "%s").' % (name, option, testcase['original'], result[option], testcase['expected'][option])
        return True

    def test_expose_tokenizer(self):
        tokenizer_builder = tokenizer.Builder()
        for filename in self.tokenizer_filenames:
            ret = tokenizer_builder.expose_tokenizer('%s/%s' % (self.assets_dir, filename))
            assert type(ret) == tuple, 'Expected tuple, returned %s' % str(type(ret))
            assert len(ret) == 2, 'Expected length 2, returned %s' % str(len(ret))
            assert type(ret[0]) == str, 'Expected ret[0] to be str, returned %s' % str(type(ret[0]))
            assert type(ret[1]) == str, 'Expected ret[1] to be str, returned %s' % str(type(ret[1]))

    def test_build_tokenizer(self):
        tokenizer_builder = tokenizer.Builder()
        for filename in self.tokenizer_filenames:
            ret = tokenizer_builder.build_tokenizer('%s/%s' % (self.assets_dir, filename))
            assert type(ret) == tokenizer.Tokenizer, 'Expected Tokenizer, returned %s' % str(type(ret))

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
        assert self.assert_tokenization('tokenizer_basic_ci.xml', 'tokenizer_basic_ci', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_basic_cs.xml', 'tokenizer_basic_cs', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_bypass.xml', 'tokenizer_bypass', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_ci_child_of_ci_parent.xml', 'test_ci_child_of_ci_parent', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_ci_child_of_cs_parent.xml', 'test_ci_child_of_cs_parent', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_ci_child_of_cs_parent.xml', 'test_ci_child_of_cs_parent', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_cs_child_of_cs_parent.xml', 'test_cs_child_of_cs_parent', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_ci_of_ci_ci.xml', 'test_grandchild_ci_of_ci_ci', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_ci_of_ci_cs.xml', 'test_grandchild_ci_of_ci_cs', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_ci_of_cs_ci.xml', 'test_grandchild_ci_of_cs_ci', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_ci_of_cs_cs.xml', 'test_grandchild_ci_of_cs_cs', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_cs_of_ci_ci.xml', 'test_grandchild_cs_of_ci_ci', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_cs_of_ci_cs.xml', 'test_grandchild_cs_of_ci_cs', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_cs_of_cs_ci.xml', 'test_grandchild_cs_of_cs_ci', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_grandchild_cs_of_cs_cs.xml', 'test_grandchild_cs_of_cs_cs', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_parent_ci.xml', 'test_ci_parent', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_multiple_tokens_ci.xml', 'tokenizer_multiple_tokens_ci', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_multiple_tokens_cs.xml', 'tokenizer_multiple_tokens_cs', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_split_extension.xml', 'test_split_extension', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_split_replace.xml', 'test_split_replace', testcases) == True, 'Something is wrong.'

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
        assert self.assert_tokenization('tokenizer_tokens_overlap_ci.xml', 'test_tokens_overlap_ci', testcases) == True, 'Something is wrong.'

    def test_tokenizer_map_bypass(self):
        pass

    def test_tokenizer_map_only_tokenize(self):
        pass

    def test_tokenizer_map_split(self):
        pass

    def test_tokenizer_map_replace_to_longer(self):
        pass

    def test_tokenizer_map_replace_to_shorter(self):
        pass

    def test_tokenizer_map_replace_to_nothing(self):
        pass

    def test_tokenizer_map_replace_character(self):
        pass

    def test_tokenizer_map_split_replace_to_longer(self):
        pass

    def test_tokenizer_map_split_replace_to_shorter(self):
        pass

    def test_tokenizer_map_split_replace_to_nothing(self):
        pass

    def test_tokenizer_map_split_replace_character(self):
        pass

    def test_tokenizer_map_option_list(self):
        pass

    def test_tokenizer_map_option_set(self):
        pass

    def test_tokenizer_default(self):
        pass

if __name__ == '__main__':
    unittest.main()
