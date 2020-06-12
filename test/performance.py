import sys; sys.path.insert(0, '')
import timeit

def perf_normalizer():
    n = 10000
    sample_label = 'acetyl(salicyllic)ac¡d,acid==alpha-labelled-base gentamycinnn nf-bkappa'
    for x in [('sic.core', '0'), ('sic.core', '1'), ('sic.core', '2'), ('dist.core', '0'), ('dist.core', '1'), ('dist.core', '2')]:
        print(
            '%s: processed %d entries "%s" in %s seconds' % (
                x, n, sample_label, str(
                    timeit.timeit(
                        setup='import %s; builder = %s.Builder(); machine = builder.build_normalizer(\'./sic/tokenizer.standard.xml\')' % (x[0], x[0]),
                        stmt='_ = machine.normalize(\'%s\', \' \', %s)' % (sample_label, x[1]),
                        number=n
                    )
                )
            )
        )

if __name__ == '__main__':
    perf_normalizer()
