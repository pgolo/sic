import cython

cdef public __normalizer__

cpdef build_normalizer(
    str filename=*
)

@cython.locals(
    result=cython.str
)
cpdef str normalize(
    str source_string,
    str word_separator=*,
    int normalizer_option=*
)
