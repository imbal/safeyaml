import safeyaml
import os
import glob
import yaml

def smoke_tests():
    tests = {
        """ [0] """:            0,
        """ [1.2] """:           1.2,
        """ [-3.4] """:         -3.4,
        """ [+5.6] """:         +5.6,
        """ "test": 1 """:      {'test':1},
        """ n: 'test' """:      {'n':'test'},
        """ [1 ,2,3] """:       [1,2,3],
        """ [1,2,3,] """:       [1,2,3],
        """ {"a":1} """:        {'a':1},
        """ {'b':2,} """:     {'b':2},
        """ [1  #foo\n] """:    [1],
    }
    for test in tests:
        try:
            out = safeyaml.parse(test)
            print('.', end='', flush=True)
        except safeyaml.ParserErr as p:
            print()
            print('X',repr(test),"gave",p.name())

def test_spec(test):
    with open(test) as fh:
        contents = fh.read()
        try:
            ref_obj = yaml.load(contents)
        except:
            print()
            print('X', test, "isn't valid vaml")
            return
        
        try:
            obj, output = safeyaml.parse(contents)
        except safeyaml.ParserErr as p:
            with open('{}.bad'.format(test)) as fh:
                name, pos = fh.readline().split(':')
                pos = int(pos)
            if p.name() == name and p.pos == pos:
                print('.', end='', flush=True)
                return
            else:
                print()
                print('X',test, "failed, expecting {}:{} got {}:{}".format(name,pos, p.name(), p.pos))
                return

        if obj != ref_obj:
            print()
            print('X', test, 'failed, safeyaml parsed different object from reference parser')

        try:
            parsed_output = yaml.load(output)
        except Exception as e:
            print()
            print('X', test, 'failed, producing invalid YAML as output')
            return

        if parsed_output != ref_obj:
            print()
            print('X', test, 'failed, parsed safeyaml output is different from reference parse of input')
            return

        with open('{}.ok'.format(test)) as fh:
            expected_output = fh.read()

        if expected_output != output:
            print()
            print('X', test, 'failed. output and {}.ok do not match'.format(test))
            return

        print('.',end='', flush=True)

if __name__ == '__main__':
    smoke_tests()
    for spec in glob.glob("spec/*.yaml"):
        test_spec(spec)
    print()

