import sys; sys.path.insert(0, '')
import timeit

def perf_tokenizer():
    n = 10000
    sample_label = 'acetyl(salicyllic)ac¡d,acid==alpha-labelled-base gentamycinnn nf-bkappa'
    for x in [('sic.core', '0'), ('sic.core', '1'), ('sic.core', '2'), ('dist.core', '0'), ('dist.core', '1'), ('dist.core', '2')]:
        print(
            '%s: processed %d entries "%s" in %s seconds' % (
                x, n, sample_label, str(
                    timeit.timeit(
                        setup='import %s; tokenizer_builder = %s.Builder(); machine = tokenizer_builder.build_tokenizer(\'./resources/tokenizer.standard.xml\')' % (x[0], x[0]),
                        stmt='_ = machine.tokenize(\'%s\', \' \', %s)' % (sample_label, x[1]),
                        number=n
                    )
                )
            )
        )

if __name__ == '__main__':
    perf_tokenizer()
