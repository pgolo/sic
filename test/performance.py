import sys; sys.path.insert(0, '')
import timeit

def perf_normalizer_many_short_strings():
    n = 10000
    sample_label = 'acetyl(salicyllic)ac¡d,acid==alpha-labelled-base gentamycinnn nf-bkappa'
    for x in [('sic.core', '0'), ('sic.core', '1'), ('sic.core', '2'), ('sic.core', '3'), ('bin.core', '0'), ('bin.core', '1'), ('bin.core', '2'), ('bin.core', '3')]:
        print(
            '%s: processed %d entr%s "%s" in %s seconds' % (
                x, n, 'y' if n==1 else 'ies', sample_label, str(
                    timeit.timeit(
                        setup='import %s; builder = %s.Builder(); machine = builder.build_normalizer(\'./sic/tokenizer.standard.xml\')' % (x[0], x[0]),
                        stmt='_ = machine.normalize(\'%s\', \' \', %s)' % (sample_label, x[1]),
                        number=n
                    )
                )
            )
        )

def perf_normalizer_one_long_string():
    n = 1
    sample_label = 'acetyl(salicyllic)ac¡d,acid==alpha-labelled-base gentamycinnn nf-bkappa' * 10000
    sample_label_length = len(sample_label)
    for x in [('sic.core', '0'), ('sic.core', '1'), ('sic.core', '2'), ('sic.core', '3'), ('bin.core', '0'), ('bin.core', '1'), ('bin.core', '2'), ('bin.core', '3')]:
        print(
            '%s: processed %d entr%s (len=%d) in %s seconds' % (
                x, n, 'y' if n==1 else 'ies', sample_label_length, str(
                    timeit.timeit(
                        setup='import %s; builder = %s.Builder(); machine = builder.build_normalizer(\'./sic/tokenizer.standard.xml\')' % (x[0], x[0]),
                        stmt='_ = machine.normalize(\'%s\', \' \', %s)' % (sample_label, x[1]),
                        number=n
                    )
                )
            )
        )

if __name__ == '__main__':
    perf_normalizer_many_short_strings()
    perf_normalizer_one_long_string()
