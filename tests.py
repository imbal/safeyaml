import io
import os
import glob
import yaml
import pytest


safeyaml_globals = {}
with open('safeyaml') as fh:
    exec(fh.read(), safeyaml_globals, safeyaml_globals)

class safeyaml:
    ParserErr = safeyaml_globals['ParserErr']
    parse = safeyaml_globals['parse']


SMOKE_TESTS = {
    """ [0] """:            [0],
    """ [1.2] """:          [1.2],
    """ [-3.4] """:         [-3.4],
    """ [+5.6] """:         [+5.6],
    """ "test": 1 """:      {'test':1},
    """ n: 'test' """:      {'n':'test'},
    """ [1 ,2,3] """:       [1,2,3],
    """ [1,2,3,] """:       [1,2,3],
    """ {"a":1} """:        {'a':1},
    """ {'b':2,} """:       {'b':2},
    """ [1  #foo\n] """:    [1],
}


@pytest.mark.parametrize("code,ref_obj", SMOKE_TESTS.items())
def test_smoke(code, ref_obj):
    obj = safeyaml.parse(code)
    assert obj == ref_obj


@pytest.mark.parametrize("path", glob.glob("tests/*.yaml"))
def test_file(path):
    with open(path) as fh:
        contents = fh.read()
        try:
            ref_obj = yaml.load(contents)
        except:
            raise Exception("input isn't valid YAML: {}".format(contents))

        try:
            output = io.StringIO()
            obj = safeyaml.parse(contents, output=output)
            output = output.getvalue()

        except safeyaml.ParserErr as p:
            with open('{}.bad'.format(path)) as fh:
                name, pos = fh.readline().split(':')
                pos = int(pos)

            assert p.name() == name and p.pos == pos
            return

        assert obj == ref_obj

        try:
            parsed_output = yaml.load(output)
        except Exception as e:
            raise Exception("output isn't valid YAML: {}".format(output))

        assert parsed_output == ref_obj

        with open('{}.ok'.format(path)) as fh:
            expected_output = fh.read()

        assert output == expected_output


if __name__ == '__main__':
    pytest.main(['-q', __file__])
