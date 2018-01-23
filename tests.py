import io
import os
import glob
import yaml
import pytest

import safeyaml

SMOKE_TESTS = {
    """ [0] """:            [0],
    """ [1.2] """:          [1.2],
    """ [-3.4] """:         [-3.4],
    """ [+5.6] """:         [+5.6],
    """ "test": 1 """:      {'test': 1},
    """ x: 'test' """:      {'x': 'test'},
    """ [1 ,2,3] """:       [1, 2, 3],
    """ [1,2,3,] """:       [1, 2, 3],
    """ {"a":1} """:        {'a': 1},
    """ {'b':2,} """:       {'b': 2},
    """ [1  #foo\n] """:    [1],
}


@pytest.mark.parametrize("code,ref_obj", SMOKE_TESTS.items())
def test_smoke(code, ref_obj):
    obj = safeyaml.parse(code)
    assert obj == ref_obj


@pytest.mark.parametrize("path", glob.glob("tests/validate/*.yaml"))
def test_validate(path):
    check_file(path, validate=True)


@pytest.mark.parametrize("path", glob.glob("tests/fix/*.yaml"))
def test_fix(path):
    check_file(path, fix=True)


def check_file(path, validate=False, fix=False):
    output_file = '{}.output'.format(path)
    error_file = '{}.error'.format(path)

    with open(path) as fh:
        contents = fh.read()

        if os.path.exists(error_file):
            with open(error_file) as fh:
                name, pos = fh.readline().split(':')
                pos = int(pos)

            with pytest.raises(safeyaml.ParserErr) as excinfo:
                safeyaml.parse(contents)

            error = excinfo.value
            assert error.name() == name
            assert error.pos == pos
            return

        options = safeyaml.Options(
            fix_unquoted=fix,
            fix_nodent=fix,
            fix_nospace=fix,
        )

        output = io.StringIO()
        obj = safeyaml.parse(contents, output=output, options=options)
        output = output.getvalue()

        if validate:
            try:
                ref_obj = yaml.load(contents)
            except yaml.YAMLError:
                raise Exception("input isn't valid YAML:\n{}".format(contents))

            assert obj == ref_obj

            try:
                parsed_output = yaml.load(output)
            except yaml.YAMLError:
                raise Exception("output isn't valid YAML:\n{}".format(output))

            assert parsed_output == ref_obj

        if fix:
            with open(output_file) as fh:
                expected_output = fh.read()
                assert output == expected_output


if __name__ == '__main__':
    pytest.main(['-q', __file__])
