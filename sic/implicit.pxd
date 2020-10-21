import cython

cdef public __normalizer__

cpdef build_normalizer(
    str filename=*
)

cpdef str normalize(
    str source_string,
    str word_separator=*,
    int normalizer_option=*
)
