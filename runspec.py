import safeyaml
import os
import glob
import yaml

if __name__ != '__main__':
    raise Exception('no')

for test in glob.glob("spec/*.yaml"):
    with open(test) as fh:
        contents = fh.read()

        print("---")
        for line in contents.split('\n'):
            print(">", line)
        print("---")

        expected = yaml.load(contents)
        
        obj, output = safeyaml.parse(contents)

        print(obj)
        print(expected)

        print("---")
        for line in output.split('\n'):
            print("<", line)
        print("---")
