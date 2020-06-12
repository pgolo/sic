import os
import xml.etree.ElementTree as et
import logging

class Tokenizer():
    """This class includes functions and methods for tokenizing strings."""

    def __init__(self, filename, tokenizer_name='', debug_mode=False, verbose_mode=False):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
        self.debug = debug_mode
        self.verbose = verbose_mode
        self.logger = logging.info if self.verbose else logging.debug
        if self.verbose:
            logging.root.setLevel(logging.INFO)
        if self.debug:
            logging.root.setLevel(logging.DEBUG)
        self.filename = filename
        self.tokenizer_name = tokenizer_name
        self.tokenizer_result = {'original': '', 'tokenized': '', 'map': []}
        self.data = dict()

    @property
    def name(self):
        return self.tokenizer_name

    @name.setter
    def name(self, tokenizer_name):
        self.tokenizer_name = tokenizer_name

    @property
    def result(self):
        return self.tokenizer_result

    def update_str_with_chmap(self, value, chmap):
        """This function zooms through a string *value*, replaces characters
        according to *chmap* dictionary object, and returns the updated string.
        """
        updated = ''
        for x in value:
            updated += chmap[x] if x in chmap else x
        return updated

    def make_tokenizer(self, sdata):
        """This function loads static set of tokienization rules stored in
        tab-delimited string into trie implemented as nested dictionary structure.

        Args:
            *sdata* is string with set of tokrules

        Returns:
            The dictionary object to store the output

        Tokenization rules string requirements:
            1) each line represents single tokenization rule;
            2) each line has at least 3 columns:
            `s`, `l`|`m`|`r` (or any combination of them), `word` == `split` `word` on the `left`|`middle`|`right`
            *or*
            `r`, `another_word`, `word` == `replace` `word` with `another_word`
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
        actions = {
            'r': {'': '~_'},
            's': {'l': '~l', 'm': '~m', 'r': '~r'},
            'c': {'': '~='}
        }
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
                if parameter_key:
                    for parameter_keylet in parameter_key:
                        subtrie[actions[action][parameter_keylet]] = parameter_value
                else:
                    subtrie[actions[action][parameter_key]] = parameter_value
        self.data = trie
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

    def tokenize(self, source_string, word_separator=' ', tokenizer_option=0):
        """This function zooms through the provided string character by character
        and returns string which is tokenized representation of a given string.

        Args:
            *source_string* is input string to tokenize
            *word_separator* is word separator to consider (must be single character)
            *tokenizer_option* is integer either 0 (normal, default), 1 (list), or 2 (set)
        """
        assert len(word_separator) == 1, 'word_separator must be single character'
        # TODO: review for refactoring
        self.tokenizer_result = {'original': source_string, 'tokenized': '', 'map': []}
        if source_string == '':
            return ''
        original_string = source_string
        subtrie = self.data
        if '_settings' in subtrie and 'bypass' in subtrie['_settings'] and subtrie['_settings']['bypass'] == '1':
            self.tokenizer_result['tokenized'] = original_string
            self.tokenizer_result['map'] = [i for i in range(len(original_string))]
            return original_string
        if '_settings' not in subtrie or 'cs' not in subtrie['_settings'] or subtrie['_settings']['cs'] != '1':
            original_string = original_string.lower()
        this_fragment = ''
        buffer = ''
        last_buffer = ''
        last_replacement = ''
        f_map = []
        b_map = []
        l_map = []
        t_map = []
        this_group = last_group = self.chargroup(original_string[0])
        total_length = int(len(original_string))
        character = original_string[0]
        last_character = ''
        current_index = 0
        temp_index = -1
        temp_buffer = ''
        began_reading = False
        on_the_left = True
        on_the_right = False
        added_separator = False
        while current_index < total_length:
            character = original_string[current_index]
            if character in self.data['_chmap']:
                character = self.data['_chmap'][character]
            this_group = self.chargroup(character)
            on_the_right = False
            added_separator = False
            if character != word_separator and last_character != word_separator:
                if this_group == 0 or this_group != last_group:
                    if not buffer.endswith(word_separator):
                        buffer += word_separator
                        if len(b_map) == len(buffer):
                            b_map[-1] = current_index
                        else:
                            b_map.append(current_index)
                    began_reading = False
                    on_the_right = True
                    added_separator = True
            if not (subtrie is self.data) and character in self.data and temp_index == -1:
                # mark this as potential head
                temp_index, temp_buffer, t_map = current_index, buffer, list(b_map)
            if character in subtrie:
                if not began_reading:
                    if on_the_left and this_fragment and this_fragment[-1:] != word_separator:
                        this_fragment += word_separator
                        if len(f_map) == len(this_fragment):
                            f_map[-1] = current_index
                        else:
                            f_map.append(current_index)
                    if this_fragment.endswith(word_separator) and buffer.startswith(word_separator):
                        f_map.pop()
                        this_fragment = this_fragment[:-1]
                    f_map += b_map
                    this_fragment += buffer
                    buffer = ''
                    b_map = []
                on_the_left = on_the_left or added_separator or last_character == word_separator
                began_reading = True
                subtrie = subtrie[character]
                buffer += character
                b_map += [current_index for x in character]
            else:
                on_the_right = on_the_right or character == word_separator
                on_the_left = not this_fragment or this_fragment[-1:] == word_separator
                began_reading = False
                # check what's in the buffer, and do the right thing
                if '~_' in subtrie:
                    # we may need to apply this replacement in future, so keep buffer value and subtrie['~_']
                    last_buffer = buffer
                    last_replacement = subtrie['~_']
                    l_map = [b_map[0] for i in range(len(last_replacement))]
                if '~_' in subtrie and on_the_left and on_the_right:
                    # now buffer has token to be replaced
                    buffer = subtrie['~_'] + word_separator #if not buffer.endswith(word_separator) else ''
                    b_map = [b_map[0] for i in range(len(buffer))]
                    last_buffer = ''
                    l_map = []
                    temp_index = -1
                    # now buffer has replaced token
                if '~l' in subtrie and on_the_left:
                    if not buffer.endswith(word_separator):
                        buffer += word_separator
                        if len(b_map) == len(buffer):
                            b_map[-1] = current_index
                        else:
                            b_map.append(current_index)
                    temp_index = -1
                if '~m' in subtrie and not on_the_left and not on_the_right:
                    if not buffer.startswith(word_separator):
                        buffer = word_separator + buffer
                        b_map.insert(0, current_index)
                    if not buffer.endswith(word_separator):
                        buffer += word_separator
                        if len(b_map) == len(buffer):
                            b_map[-1] = current_index
                        else:
                            b_map.append(current_index)
                    if last_buffer:
                        f_map = f_map[:-len(last_buffer)] + l_map
                        this_fragment = this_fragment[:-len(last_buffer)] + last_replacement
                    temp_index = -1
                if '~r' in subtrie and on_the_right:
                    if not buffer.startswith(word_separator):
                        buffer = word_separator + buffer
                        b_map.insert(0, current_index)
                    temp_index = -1
                subtrie = self.data
                if temp_index > -1:
                    current_index, buffer, b_map = temp_index, temp_buffer, list(t_map) # plain jumping back which causes performance hit, think about better solution
                    temp_index, temp_buffer, t_map = -1, '', []
                    continue
                if on_the_left and this_fragment and this_fragment[-1:] != word_separator and character != word_separator and not added_separator:
                    this_fragment += word_separator
                    if len(f_map) == len(this_fragment):
                        f_map[-1] = current_index
                    else:
                        f_map.append(current_index)
                if this_fragment.endswith(word_separator) and buffer.startswith(word_separator):
                    f_map.pop()
                    this_fragment = this_fragment[:-1]
                f_map += b_map
                this_fragment += buffer
                buffer = character
                b_map = [current_index for x in character]
                on_the_left = False
                if character in self.data:
                    on_the_left = added_separator or last_character == word_separator
                    began_reading = True
                    subtrie = self.data[character]
            last_group = this_group
            last_character = character
            current_index += 1
        # check what's in the buffer, and do the right thing
        # DRY!
        on_the_right = True
        on_the_left = this_fragment[-1:] == word_separator
        if '~_' in subtrie and on_the_left and on_the_right:
            # now buffer has token to be replaced
            buffer = subtrie['~_'] + word_separator #if not buffer.endswith(word_separator) else ''
            if len(b_map) == len(buffer):
                b_map[-1] = total_length - 1
            else:
                b_map.append(total_length - 1)
            last_buffer = ''
            l_map = []
            # now buffer has replaced token
        if '~r' in subtrie and on_the_right:
            if not buffer.startswith(word_separator):
                buffer = word_separator + buffer
                b_map.insert(0, total_length - 1)
            if last_buffer:
                f_map += l_map
                this_fragment = this_fragment[:-len(last_buffer)] + last_replacement
        if on_the_left and this_fragment[-1:] != word_separator:
            this_fragment += word_separator
            f_map.append(total_length - 1)
        if this_fragment.endswith(word_separator) and buffer.startswith(word_separator):
            f_map.pop()
            this_fragment = this_fragment[:-1]
        f_map += b_map
        this_fragment += buffer
        while this_fragment.startswith(word_separator):
            this_fragment = this_fragment[len(word_separator):]
            f_map = f_map[len(word_separator):]
        while this_fragment.endswith(word_separator):
            this_fragment = this_fragment[:-len(word_separator)]
            f_map = f_map[:-len(word_separator)]
        tokenized = this_fragment
        if tokenizer_option == 1:
            tokenized = word_separator.join(sorted(tokenized.split(word_separator)))
        elif tokenizer_option == 2:
            tokenized = word_separator.join(sorted(set(tokenized.split(word_separator))))
        else:
            self.tokenizer_result['map'] = f_map
        self.tokenizer_result['tokenized'] = tokenized
        return tokenized

class Builder():
    """This class is the builder for Tokenizer."""

    def __init__(self, debug_mode=False, verbose_mode=False):
        self.debug = debug_mode
        self.verbose = verbose_mode
        self.logger = logging.info if self.verbose else logging.debug
        if self.verbose:
            logging.root.setLevel(logging.INFO)
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

    def wrap_result(self, root, address, keyhole, key, parent, child):
        """This function populates dict object *keyhole* with the data retrieved from XML elemebt *root* as follows:
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
        result = res if res else {'name': filename if not batch_name else batch_name}
        tree = et.parse(filename)
        root = tree.getroot()
        if 'name' in root.attrib and not batch_name:
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
                    ret += '{0}\t{1}\t{2}\n'.format(key, prop, value)
        return (data['name'], ret)

    def build_tokenizer(self, filename=None):
        """This function loads configuration, constructs Tokenizer with this configuration,
        and returns this Tokenizer object.

        Args:
            str *filename* is XML file defining the configuration of a tokenizer
        """
        if not filename:
            filename = '%s/tokenizer.standard.xml' % (os.path.abspath(os.path.dirname(__file__)))
        (batch_name, data) = self.expose_tokenizer(filename)
        machine = Tokenizer(filename, batch_name)
        built = machine.make_tokenizer(data)
        if not built:
            logging.critical('Could not build tokenizer using "{0}"!'.format(filename))
        return machine
