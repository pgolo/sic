import cython

cdef public __normalizer__
cdef public dict __normalizer_result__

cpdef build_normalizer(
    endpoint=*
)

cpdef result()

cpdef reset()
