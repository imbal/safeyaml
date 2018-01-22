import safeyaml
import os
import glob
import yaml

if __name__ != '__main__':
    raise Exception('no')
tests = """
    [0]
    [1.2]
    [-3.4]
    [+5.6]
    ["test"]
    ['test']
    [1,2,3]
    [1,2,3,]
    {"a":1}
    {'b':2,}
    [1 ] #foo """
for test in tests.split("\n"):
    test.strip()
    if not test: continue
    print(repr(test))
    print('=>', safeyaml.parse(test)[0])

for test in glob.glob("spec/*.yaml"):
    print()
    print()
    with open(test) as fh:
        contents = fh.read()

        expected = yaml.load(contents)
        
        obj, output = safeyaml.parse(contents)
        print("---")
        for line in zip(contents.split('\n'),output.split('\n')):
            print(">", line[0],'$')
            print("<", line[1], '$')
            if line[0] != line[1]:
                raise('butt')
        print("---")
        expected_out = yaml.load(output)

        if expected != expected_out:
            raise Exception('no')

