import fnmatch
import io
import os
import glob
import yaml
import pytest
import subprocess


@pytest.mark.parametrize("path", glob.glob("tests/validate/*.yaml"))
def test_validate(path):
    check_file(path, validate=True)


@pytest.mark.parametrize("path", glob.glob("tests/fix/*.yaml"))
def test_fix(path):
    check_file(path, fix=True)


def check_file(path, validate=False, fix=False):
    output_file = '{}.output'.format(path)
    error_file = '{}.error'.format(path)

    if os.path.exists(error_file):
        with open(error_file) as fh:
            expected_output = fh.read()

        with pytest.raises(subprocess.CalledProcessError) as excinfo:
            safeyaml(path, fix=fix)

        error = excinfo.value
        assert error.stdout.decode('utf-8') == ''
        assert_errors_match(expected_output, error.stderr.decode('utf-8'), path=path)
        return

    output = safeyaml(path, fix=fix)
    
    # FIXME: should be no output if fix=False
    if fix:
        with open(output_file) as fh:
            expected_output = fh.read()
            assert output == expected_output


def assert_errors_match(expected_output, actual_output, **format_vars):
    pattern_lines = expected_output.split("\n")
    output_lines = actual_output.split("\n")
    
    assert len(pattern_lines) == len(output_lines), \
        "Expected {} lines of output, got {}:\n{}" \
        .format(len(pattern_lines), len(output_lines), actual_output)

    for pattern, line in zip(pattern_lines, output_lines):
        pattern = pattern.format(**format_vars)
        assert fnmatch.fnmatch(line, pattern), \
            "Expected line:\n\n    {}\n\nto match pattern:\n\n    {}\n" \
            .format(line, pattern)


def safeyaml(path, fix=False):
    command = ["safeyaml"]
    if fix:
        command.append("--fix")
    command.append(path)

    output = subprocess.check_output(command, stderr=subprocess.PIPE)
    return output.decode('utf-8')


if __name__ == '__main__':
    pytest.main(['-q', __file__])
