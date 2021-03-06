import cython

cdef class Rule():

    cpdef decode(
        self
    )

cdef class Model():

    cdef str sdata
    cdef public bint case_sensitive
    cdef public bint bypass
    cdef dict rules
    cdef dict _replacements

    cpdef add_rule(
        self,
        rule
    )

    cpdef remove_rule(
        self,
        rule
    )

cdef class Normalizer():

    cdef public bint debug
    cdef public bint verbose
    cdef public logger
    cdef public str tokenizer_name
    cdef public dict content
    cdef public dict normalizer_result

    @cython.locals(
        next_nodes=cython.set
    )
    cpdef set expand_instruction(
        self,
        dict g,
        str seed,
        set nodes=*,
        int hops=*
    )

    @cython.locals(
        ret=cython.str,
        replacements=cython.dict,
        line=cython.str,
        action=cython.str,
        parameter=cython.str,
        subject=cython.str,
        node=cython.str
    )
    cpdef str merge_replacements(
        self,
        str sdata
    )

    @cython.locals(
        updated = cython.str,
        x = cython.str
    )
    cpdef str update_str_with_chmap(
        self,
        str value,
        dict chmap
    )

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
    cpdef bint make_tokenizer(
        self,
        str sdata,
        bint update=*
    )

    cpdef int chargroup(
        self,
        str s
    )

    cpdef str align_case(
        self,
        str replacement,
        str original,
        int normalizer_option
    )

    @cython.locals(
        ret=cython.list,
        i=cython.int,
        j=cython.int,
        k=cython.int
    )
    cpdef list reverse_map(
        self,
        list m
    )

    @cython.locals(
        original_string=cython.str,
        parsed_string=cython.str,
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
    cpdef str normalize(
        self,
        str source_string,
        str word_separator=*,
        int normalizer_option=*,
        str control_character=*
    )

    cpdef save(
        self,
        str filename
    )

    cpdef load(
        self,
        str filename
    )

cdef class Builder():

    cdef public bint debug
    cdef public bint verbose
    cdef public logger

    cpdef bint wrap_result(
        self,
        root,
        str address,
        dict keyhole,
        str key,
        str parent,
        str child
    )

    @cython.locals(
        result=cython.dict
    )
    cpdef dict convert_xml(
        self,
        str filename,
        dict res,
        str batch_name
    )

    @cython.locals(
        data=cython.dict,
        ret=cython.str,
        key=cython.str,
        prop=cython.str,
        value=cython.str
    )
    cpdef tuple expose_tokenizer(
        self,
        str file_xml
    )

    @cython.locals(
        batch_name=cython.str,
        data=cython.str,
        built=cython.bint
    )
    cpdef build_normalizer(
        self,
        endpoint=*
    )
