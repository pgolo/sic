import cython

cdef class Normalizer():

    cdef bint debug
    cdef bint verbose
    cdef logger
    cdef str filename
    cdef str tokenizer_name
    cdef dict data
    cdef dict normalizer_result

    @cython.locals(
        updated = cython.str,
        x = cython.str
    )
    cdef str update_str_with_chmap(self, str value, dict chmap)

    @cython.locals(
        actions=cython.dict,
        trie=cython.dict,
        line=cython.str,
        action=cython.str,
        parameter=cython.str,
        subject=cython.str,
        parameter_key=cython.str,
        parameter_keylet=cython.str,
        parameter_value=cython.str,
        subtrie=cython.dict
    )
    cdef bint make_tokenizer(self, str sdata)

    cdef int chargroup(self, str s)

    @cython.locals(
        original_string=cython.str,
        subtrie=cython.dict,
        this_fragment=cython.str,
        buffer=cython.str,
        last_buffer=cython.str,
        last_replacement=cython.str,
        f_map=cython.list,
        b_map=cython.list,
        l_map=cython.list,
        t_map=cython.list,
        this_group=cython.int,
        last_group=cython.int,
        total_length=cython.int,
        character=cython.str,
        last_character=cython.str,
        current_index=cython.int,
        temp_index=cython.int,
        temp_buffer=cython.str,
        began_reading=cython.bint,
        on_the_left=cython.bint,
        on_the_right=cython.bint,
        added_separator=cython.bint,
        normalized=cython.str,
        i=cython.int,
        x=cython.str
    )
    cpdef str normalize(self, str source_string, str word_separator=*, int normalizer_option=*)

cdef class Builder():

    cdef bint debug
    cdef bint verbose
    cdef logger

    cdef bint wrap_result(self, root, str address, dict keyhole, str key, str parent, str child)

    @cython.locals(
        result=cython.dict
    )
    cdef dict convert_xml(self, str filename, dict res, str batch_name)

    @cython.locals(
        data=cython.dict,
        ret=cython.str,
        key=cython.str,
        prop=cython.str,
        value=cython.str
    )
    cdef tuple expose_tokenizer(self, str file_xml)

    @cython.locals(
        batch_name=cython.str,
        data=cython.str,
        built=cython.bint
    )
    cpdef build_normalizer(self, str filename=*)