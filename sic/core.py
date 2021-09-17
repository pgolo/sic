import os
import xml.etree.ElementTree as et
import logging
import pickle

class Rule():
    """Generic tokenization rule for ad hoc model creation."""

    def __init__(self, action, value, key):
        self.action = action
        self.value = value
        self.key = key

    def decode(self):
        return '%s\t%s\t%s\n' % (self.action, self.key, self.value)

class SplitToken(Rule):
    """Instruction to split token."""

    def __init__(self, token, where):
        assert where.replace('l', '').replace('m', '').replace('r', '') == '', '`where` parameter can only include characters `l`, `m`, or `r`'
        super().__init__('s', token, where)

class ReplaceToken(Rule):
    """Instruction to replace token."""

    def __init__(self, replace_from, replace_to):
        super().__init__('r', replace_from, replace_to)

class ReplaceCharacter(Rule):
    """Instruction to replace character."""

    def __init__(self, replace_from, replace_to):
        super().__init__('c', replace_from, replace_to)

class Model():
    """This class represents set of tokenization rules for ad hoc model creation."""

    def __init__(self):
        self.sdata = ''
        self.case_sensitive = False
        self.bypass = False
        self.rules = dict()
        self._replacements = {'r': dict(), 'c': dict()}

    def __repr__(self):
        if self.bypass:
            return 'set\tbypass\t1\n'
        self.sdata = 'set\tcs\t%d\n' % (1 if self.case_sensitive else 0)
        for action in self.rules:
            for key in self.rules[action]:
                for value in self.rules[action][key]:
                    self.sdata += '%s\t%s\t%s\n' % (action, key, value)
        return self.sdata

    def add_rule(self, rule):
        """This method adds tokenization rule to model.

        Args:
            *rule* is Rule instance
        """
        if rule.action in self._replacements:
            if rule.value in self._replacements[rule.action]:
                obsolete_rule = Rule(rule.action, rule.value, self._replacements[rule.action][rule.value])
                self.remove_rule(obsolete_rule)
        if rule.action in self.rules:
            if rule.value in self.rules[rule.action]:
                if rule.key in self.rules[rule.action][rule.value]:
                    obsolete_rule = Rule(rule.action, rule.key, rule.value)
                    self.remove_rule(obsolete_rule)
        if rule.action not in self.rules:
            self.rules[rule.action] = dict()
        if rule.key not in self.rules[rule.action]:
            self.rules[rule.action][rule.key] = set()
        self.rules[rule.action][rule.key].add(rule.value)
        if rule.action in self._replacements:
            self._replacements[rule.action][rule.value] = rule.key

    def remove_rule(self, rule):
        """This method removes tokenization rule from model.

        Args:
            *rule* is Rule instance
        """
        if rule.action in self.rules:
            if rule.key in self.rules[rule.action]:
                if rule.value in self.rules[rule.action][rule.key]:
                    self.rules[rule.action][rule.key].remove(rule.value)
                    if len(self.rules[rule.action][rule.key]) == 0:
                        del self.rules[rule.action][rule.key]
                    if len(self.rules[rule.action]) == 0:
                        del self.rules[rule.action]

class Normalizer():
    """This class includes functions and methods for normalizing strings."""

    def __init__(self, tokenizer_name='', debug_mode=False, verbose_mode=False):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
        self.debug = debug_mode
        self.verbose = verbose_mode
        self.logger = logging.info if self.verbose else logging.debug
        if self.verbose:
            logging.root.setLevel(logging.INFO)
        if self.debug:
            logging.root.setLevel(logging.DEBUG)
        self.tokenizer_name = tokenizer_name
        self.normalizer_result = {'original': '', 'normalized': '', 'map': [], 'r_map': []}
        self.content = dict()

    @property
    def name(self):
        return self.tokenizer_name

    @name.setter
    def name(self, tokenizer_name):
        self.tokenizer_name = tokenizer_name

    @property
    def result(self):
        return self.normalizer_result

    @property
    def data(self):
        return self.content
    
    @data.setter
    def data(self, obj):
        self.content = obj

    def expand_instruction(self, g, seed, nodes=set(), hops=0):
        """Helper function that traverses a path and returns set of terminal nodes.
        For a directed graph *g*, it is assumed that each node has at most 1 descendant.

        Args:
            *g* is a dict(str, set) representing a graph
            *seed* is a node (str) to expand
            *nodes* is a set of nodes on the way of expansion
            *hops* is depth of expansion so far
        """
        next_nodes = set()
        if hops == 0:
            nodes = {seed}
        elif seed in nodes:
            raise RecursionError('Circular reference in replacement instruction regarding "%s"' % (seed))
        for node in nodes:
            if node in g:
                next_nodes = next_nodes.union(self.expand_instruction(g, seed, g[node], hops + 1))
            else:
                next_nodes.add(node)
        return next_nodes

    def merge_replacements(self, sdata):
        """This function takes *sdata* config string, merges classes of "c" and "r" tokenization rules,
        and returns corrected configuration string that accounts for transitive rules.

        Args:
            *sdata* is string with set of tokrules
        """
        ret = ''
        replacements = dict()
        for line in sdata.splitlines():
            if not line.strip().startswith('#'):
                [action, parameter, subject] = line.strip().split('\t')[0:3]
                if action in ['c', 'r']:
                    if action not in replacements:
                        replacements[action] = dict()
                    if subject not in replacements[action]:
                        replacements[action][subject] = set()
                    replacements[action][subject].add(parameter)
                    continue
            ret += '%s\n' % (line)
        for action in replacements:
            for node in replacements[action]:
                replacements[action][node] = self.expand_instruction(replacements[action], node)
                if len(replacements[action][node]) > 1:
                    raise ValueError('Conflicting instruction: (replace "%s" --> "%s") vs (replace "%s" --> "%s")' % (subject, replacements[action][subject], subject, parameter))
                ret += '%s\t%s\t%s\n' % (action, next(iter(replacements[action][node])), node)
        return ret

    def update_str_with_chmap(self, value, chmap):
        """This function zooms through a string *value*, replaces characters
        according to *chmap* dictionary object, and returns the updated string.
        """
        updated = ''
        for x in value:
            updated += chmap[x] if x in chmap else x
        return updated

    def make_tokenizer(self, sdata, update=False):
        """This function loads static set of tokienization rules stored in
        tab-delimited string into trie implemented as nested dictionary structure.

        Args:
            *sdata* is string with set of tokrules
            *update*: when True, existing trie will be updated rather than new trie created

        Returns:
            The dictionary object to store the output

        Tokenization rules string requirements:
            1) each line represents single tokenization rule;
            2) each line has at least 3 columns:
            `s`, `l`|`m`|`r` (or any combination of them), `word` == split `word` on the `left`|`middle`|`right`
            *or*
            `r`, `another_word`, `word` == replace `word` with `another_word`
            *or*
            `c`, `another_char`, `char` == replace `char` with `another_char`

        The returned dictionary object represents the uncompressed trie
        with the leaves designating the action that must be taken for a given prefix:
            '~_' => r (replace token)
            '~=' => c (replace character)
            '~l' => s l (split left)
            '~m' => s m (split middle)
            '~r' => s r (split right)
        """
        # TODO: review for refacting, stay dry
        sdata = self.merge_replacements(sdata)
        actions = {
            'r': {'': '~_'},
            's': {'l': '~l', 'm': '~m', 'r': '~r'},
            'c': {'': '~='}
        }
        if update:
            trie = self.content
        else:
            trie = dict()
            trie['_settings'] = dict()
            trie['_chmap'] = dict()
        for line in sdata.splitlines():
            if not line.strip().startswith('#'):
                [action, parameter, subject] = line.strip().split('\t')[0:3]
                if action != 'set':
                    continue
                trie['_settings'][parameter] = subject
        for line in sdata.splitlines():
            if not line.strip().startswith('#'):
                [action, parameter, subject] = line.strip().split('\t')[0:3]
                if 'cs' not in trie['_settings'] or trie['_settings']['cs'] == '0':
                    parameter = parameter.lower()
                    subject = subject.lower()
                if action != 'c':
                    continue
                trie['_chmap'][subject] = parameter
        for line in sdata.splitlines():
            if not line.strip().startswith('#'):
                [action, parameter, subject] = line.strip().split('\t')[0:3]
                if action in ['c', 'set']:
                    continue
                if 'cs' not in trie['_settings'] or trie['_settings']['cs'] == '0':
                    parameter = parameter.lower()
                    subject = subject.lower()
                parameter_key = parameter
                parameter_value = parameter
                if action == 'r':
                    parameter_key = ''
                    parameter_value = self.update_str_with_chmap(parameter, trie['_chmap'])
                else:
                    parameter_value = ''
                subtrie = trie
                for character in subject:
                    if character in trie['_chmap']:
                        character = trie['_chmap'][character]
                    if character not in subtrie:
                        subtrie[character] = dict()
                    subtrie = subtrie[character]
                if parameter_key != '':
                    for parameter_keylet in parameter_key:
                        subtrie[actions[action][parameter_keylet]] = parameter_value
                else:
                    subtrie[actions[action][parameter_key]] = parameter_value
        self.content = trie
        return True

    def chargroup(self, s):
        """This function takes a character and returns an integer designating
        group the character belongs to:
            1 => alphabetical
            2 => numeric
            0 => everything else
        """
        if s.isalpha():
            return 1
        elif s.isnumeric():
            return 2
        return 0

    def align_case(self, replacement, original, normalizer_option):
        """This function aligns letter case in *replacement* with that in *original*
        (only if *normalizer_option* assumes this is to be done)

        Args:
            *replacement* is string whose letter case is to be reviewed
            *original* is string that is to serve as letter case template
            *normalizer_option* is integer
        """
        if normalizer_option != 3:
            return replacement
        if original == original.upper():
            return replacement.upper()
        elif original[0] == original[0].upper() and original[1:] == original[1:].lower():
            return replacement[0].upper() + replacement[1:].lower()
        return replacement

    def reverse_map(self, m):
        """This function takes character location map in a form it is stored at self.normalizer_result['map']
        and returns list where item index is character index in original string, and item value is pair
        of lowest and highest character index in normalized string.
        """
        ret = [None] * (m[-1] + 1)
        for i in range(len(m)):
            if ret[m[i]] is None:
                ret[m[i]] = [i, i]
            else:
                ret[m[i]][1] = i
        j = 0
        for i in range(0, len(ret)):
            if ret[i] is not None:
                j = i
                for k in range(0, j):
                    ret[k] = ret[j]
                break
        for i in range(j+1, len(ret)):
            if ret[i] is None:
                ret[i] = ret[i-1]
        return ret

    def normalize(self, source_string, word_separator=' ', normalizer_option=0, control_character='\x00'):
        """This function zooms through the provided string character by character
        and returns string which is normalized representation of a given string.

        Args:
            *source_string* is input string to normalize
            *word_separator* is word separator to consider (must be single character)
            *normalizer_option* is integer either 0 (normal, default), 1 (list), 2 (set), 3 (join split tokens back)
        """
        assert len(word_separator) == 1, 'word_separator is not a single character (it must be)'
        assert len(control_character) == 1, 'control_character is not a single character (it must be)'
        assert word_separator != control_character, 'word_separator and control_character are same (they must not be)'
        # TODO: review for refactoring
        self.normalizer_result = {'original': source_string, 'normalized': '', 'map': [], 'r_map': []}
        if source_string == '':
            return ''
        original_string = source_string
        parsed_string = source_string
        subtrie = self.content
        if '_settings' in subtrie and 'bypass' in subtrie['_settings'] and subtrie['_settings']['bypass'] == '1':
            self.normalizer_result['normalized'] = original_string
            self.normalizer_result['map'] = [i for i in range(len(original_string))]
            self.normalizer_result['r_map'] = [(i, i) for i in range(len(original_string))]
            return original_string
        if '_settings' not in subtrie or 'cs' not in subtrie['_settings'] or subtrie['_settings']['cs'] != '1':
            parsed_string = parsed_string.lower()
            if normalizer_option != 3:
                original_string = parsed_string
        this_fragment = ''
        buffer = ''
        last_buffer = ''
        last_replacement = ''
        f_map = []
        b_map = []
        l_map = []
        t_map = []
        this_group = last_group = self.chargroup(parsed_string[0])
        total_length = int(len(parsed_string))
        character = parsed_string[0]
        last_character = ''
        current_index = 0
        temp_index = -1
        temp_buffer = ''
        began_reading = False
        on_the_left = True
        on_the_right = False
        added_separator = False
        while current_index < total_length:
            character, original_character = parsed_string[current_index], original_string[current_index]
            assert control_character not in (character, original_character), 'Operation aborted: control character is found in parsed string'
            if character in self.content['_chmap']:
                character = self.content['_chmap'][character]
                original_character = character
            this_group = self.chargroup(character)
            on_the_right = False
            added_separator = False
            if character not in (word_separator, control_character) and last_character not in (word_separator, control_character):
                if (this_group == 0 or this_group != last_group) and (subtrie is self.content or character not in subtrie):
                    if not buffer.endswith(word_separator) and not buffer.endswith(control_character):
                        buffer += control_character
                        if len(b_map) == len(buffer):
                            b_map[-1] = current_index
                        else:
                            b_map.append(current_index)
                    began_reading = False
                    on_the_right = True
                    added_separator = True
            if not (subtrie is self.content) and character in self.content and temp_index == -1:
                # mark this as potential head
                temp_index, temp_buffer, t_map = current_index, buffer, list(b_map)
            if character in subtrie:
                if not began_reading:
                    if on_the_left and this_fragment != '' and this_fragment[-1:] not in (word_separator, control_character):
                        this_fragment += control_character
                        if len(f_map) == len(this_fragment):
                            f_map[-1] = current_index
                        else:
                            f_map.append(current_index)
                    if (this_fragment.endswith(word_separator) or this_fragment.endswith(control_character)) and (buffer.startswith(word_separator) or buffer.startswith(control_character)):
                        f_map.pop()
                        this_fragment = this_fragment[:-1]
                    f_map += b_map
                    this_fragment += buffer
                    buffer = ''
                    b_map = []
                on_the_left = on_the_left or added_separator or last_character in (word_separator, control_character)
                began_reading = True
                subtrie = subtrie[character]
                buffer += original_character
                b_map += [current_index for x in character]
            else:
                on_the_right = on_the_right or character in (word_separator, control_character)
                on_the_left = this_fragment == '' or this_fragment[-1:] in (word_separator, control_character)
                began_reading = False
                # check what's in the buffer, and do the right thing
                if '~_' in subtrie:
                    # we may need to apply this replacement in future, so keep buffer value and subtrie['~_']
                    last_buffer = buffer
                    last_replacement = self.align_case(subtrie['~_'], last_buffer, normalizer_option)
                    l_map = [b_map[0] for i in range(len(last_replacement))]
                if '~_' in subtrie and ((on_the_left and on_the_right) or '~m' in subtrie or ('~l' in subtrie and on_the_left) or ('~r' in subtrie and on_the_right)):
                    # now buffer has token to be replaced
                    buffer = self.align_case(subtrie['~_'], buffer, normalizer_option) + control_character #if not buffer.endswith(word_separator) else ''
                    b_map = [b_map[0] for i in range(len(buffer))]
                    last_buffer = ''
                    l_map = []
                    temp_index = -1
                    # now buffer has replaced token
                if '~l' in subtrie and on_the_left:
                    if not buffer.endswith(word_separator) and not buffer.endswith(control_character):
                        buffer += control_character
                        if len(b_map) == len(buffer):
                            b_map[-1] = current_index
                        else:
                            b_map.append(current_index)
                    temp_index = -1
                if '~m' in subtrie and not on_the_left and not on_the_right:
                    if not buffer.startswith(word_separator) and not buffer.startswith(control_character):
                        buffer = control_character + buffer
                        b_map.insert(0, current_index)
                    if not buffer.endswith(word_separator) and not buffer.endswith(control_character):
                        buffer += control_character
                        if len(b_map) == len(buffer):
                            b_map[-1] = current_index
                        else:
                            b_map.append(current_index)
                    if last_buffer != '':
                        f_map = f_map[:-len(last_buffer)] + l_map
                        this_fragment = this_fragment[:-len(last_buffer)] + last_replacement
                    temp_index = -1
                if '~r' in subtrie and on_the_right:
                    if not buffer.startswith(word_separator) and not buffer.startswith(control_character):
                        buffer = control_character + buffer
                        b_map.insert(0, current_index)
                    temp_index = -1
                subtrie = self.content
                if temp_index > -1:
                    current_index, buffer, b_map = temp_index, temp_buffer, list(t_map) # plain jumping back which causes performance hit, think about better solution
                    temp_index, temp_buffer, t_map = -1, '', []
                    continue
                if on_the_left and this_fragment != '' and this_fragment[-1:] not in (word_separator, control_character) and character not in (word_separator, control_character) and not added_separator:
                    this_fragment += control_character
                    if len(f_map) == len(this_fragment):
                        f_map[-1] = current_index
                    else:
                        f_map.append(current_index)
                if (this_fragment.endswith(word_separator) or this_fragment.endswith(control_character)) and (buffer.startswith(word_separator) or buffer.startswith(control_character)):
                    f_map.pop()
                    this_fragment = this_fragment[:-1]
                f_map += b_map
                this_fragment += buffer
                buffer = original_character
                b_map = [current_index for x in character]
                on_the_left = False
                if character in self.content:
                    on_the_left = added_separator or last_character in (word_separator, control_character)
                    began_reading = True
                    subtrie = self.content[character]
            last_group = this_group
            last_character = character
            current_index += 1
        # check what's in the buffer, and do the right thing
        # DRY!
        on_the_right = True
        on_the_left = this_fragment == '' or this_fragment[-1:] in (word_separator, control_character)
        if '~_' in subtrie and ((on_the_left and on_the_right) or '~m' in subtrie or ('~l' in subtrie and on_the_left) or ('~r' in subtrie and on_the_right)):
            buffer = self.align_case(subtrie['~_'], buffer, normalizer_option)
            b_map = [b_map[0] for i in range(len(buffer))]
            last_buffer = ''
            l_map = []
        if '~r' in subtrie and on_the_right:
            if not buffer.startswith(word_separator) and not buffer.startswith(control_character):
                buffer = word_separator + buffer
                b_map.insert(0, total_length - 1)
            if last_buffer != '':
                f_map += l_map
                this_fragment = this_fragment[:-len(last_buffer)] + last_replacement
        if on_the_left and this_fragment[-1:] not in (word_separator, control_character):
            this_fragment += control_character
            f_map.append(total_length - 1)
        if (this_fragment.endswith(word_separator) or this_fragment.endswith(control_character)) and (buffer.startswith(word_separator) or buffer.startswith(control_character)):
            f_map.pop()
            this_fragment = this_fragment[:-1]
        f_map += b_map
        this_fragment += buffer
        while this_fragment.startswith(word_separator) or this_fragment.startswith(control_character):
            this_fragment = this_fragment[len(word_separator):]
            f_map = f_map[len(word_separator):]
        while this_fragment.endswith(word_separator) or this_fragment.endswith(control_character):
            this_fragment = this_fragment[:-len(word_separator)]
            f_map = f_map[:-len(word_separator)]
        normalized = this_fragment
        if normalizer_option == 3:
            normalized = normalized.replace(control_character, '')
        else:
            normalized = normalized.replace(control_character, word_separator)
        if normalizer_option == 1:
            normalized = word_separator.join(sorted(normalized.split(word_separator)))
        elif normalizer_option == 2:
            normalized = word_separator.join(sorted(set(normalized.split(word_separator))))
        elif len(f_map) > 0 and normalizer_option == 0:
            f_map[-1] = total_length - 1
            self.normalizer_result['map'] = f_map
            self.normalizer_result['r_map'] = self.reverse_map(self.normalizer_result['map'])
        self.normalizer_result['normalized'] = normalized
        return normalized

    def save(self, filename):
        """This method pickles normalizer to a file.

        Args:
            *filename* is path/filename to save Normalizer object to
        """
        with open(filename, mode='wb') as f:
            pickle.dump(self.data, f)

    def load(self, filename):
        """This function unpickles normalizer from a file.

        Args:
            *filename* is path/filename to load Normalizer object from
        """
        with open(filename, mode='rb') as f:
            self.data = pickle.load(f)

class Builder():
    """This class is the builder for Normalizer."""

    def __init__(self, debug_mode=False, verbose_mode=False):
        self.debug = debug_mode
        self.verbose = verbose_mode
        self.logger = logging.info if self.verbose else logging.debug
        if self.verbose:
            logging.root.setLevel(logging.INFO)
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

    def wrap_result(self, root, address, keyhole, key, parent, child):
        """This function populates dict object *keyhole* with the data retrieved from XML element *root* as follows:
            keyhole[key][root/address.col2][root/address.col3]

        Args:
            xml.etree.ElementTree.Element *root* is XML element object
            str *address* is path to element to wrap
            str *key* is key to group data under
            dict *keyhole* is dict object to populate
            str *parent* is attribute name whose value must be above child
            str *child* is attribute name whose value must be below parent
        """
        elements = root.findall(address)
        if key not in keyhole:
            keyhole[key] = dict()
        for element in elements:
            if element.attrib[parent] not in keyhole[key]:
                keyhole[key][element.attrib[parent]] = set()
            keyhole[key][element.attrib[parent]].add(element.attrib[child])
        return True

    def convert_xml(self, filename, res, batch_name):
        """This function zooms through XML file with a tokenizer config,
        resolves imports, and returns list of tokenization rules as a dict object.

        Args:
            str *filename* is XML file defining the configuration of a tokenizer
            dict *res* is initial dict with tokenization rules
            str *batch_name* is name of tokenizer
        """
        result = res if res else {'name': filename if batch_name == '' else batch_name}
        tree = et.parse(filename)
        root = tree.getroot()
        if 'name' in root.attrib and batch_name == '':
            result['name'] = root.attrib['name']
        import_elements = root.findall('./import')
        if import_elements:
            for import_element in import_elements:
                import_filename = '{0}/{1}'.format(os.path.dirname(filename), import_element.attrib['file']) if os.path.dirname(filename) else import_element.attrib['file']
                result = {**result, **self.convert_xml(import_filename, result, result['name'])}
        self.wrap_result(root, './setting', result, 'set', 'name', 'value')
        self.wrap_result(root, './split', result, 's', 'where', 'value')
        self.wrap_result(root, './token', result, 'r', 'to', 'from')
        self.wrap_result(root, './character', result, 'c', 'to', 'from')
        return result

    def expose_tokenizer(self, file_xml):
        """This function processes and compiles tokenizer config defined in XML,
        and returns tuple (str name, str rules) where "name" is the name of tokenizer, and "rules" is
        the complete list of tokenization rules used for building Tokenizer object.

        Args:
            str *file_xml* is XML file defining the configuration of a tokenizer
        """
        data = self.convert_xml(file_xml, None, '')
        if 'cs' in data['set'] and len(data['set']['cs']) > 1:
            del data['set']['cs']
            logging.warning('Multiple values for "cs" setting of tokenizer in {0} - ignoring this setting!'.format(file_xml))
        ret = ''
        for key in ['set', 's', 'r', 'c']:
            for prop in data[key]:
                for value in data[key][prop]:
                    ret += '%s\t%s\t%s\n' % (key, prop, value)
        return (data['name'], ret)

    def build_normalizer(self, endpoint=None):
        """This function loads configuration, constructs Normalizer with this configuration,
        and returns created Normalizer object.

        Args:
            *endpoint* is either Model instance, or path to XML file defining the configuration of a tokenizer
        """
        if not endpoint:
            endpoint = '%s/tokenizer.standard.xml' % (os.path.abspath(os.path.dirname(__file__)))
        if isinstance(endpoint, Model):
            batch_name, data = None, str(endpoint)
            machine = Normalizer(batch_name, self.debug, self.verbose)
        else:
            (batch_name, data) = self.expose_tokenizer(endpoint)
            machine = Normalizer(batch_name, self.debug, self.verbose)
        built = machine.make_tokenizer(data)
        if not built:
            logging.critical('Endpoint %s: Could not build normalizer' % (endpoint))
        return machine
