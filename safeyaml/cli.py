import argparse
import io
import sys

from .parser import Options
from .parser import ParserErr
from .parser import parse

from . import precheck


def main():
    parser = argparse.ArgumentParser(
        description="SafeYAML Linter, checks (or formats) a YAML file for common ambiguities")

    parser.add_argument("file", nargs="*", default=None,
                        help="filename to read, without will read from stdin")
    parser.add_argument("--fix",  action='store_true',
                        default=False, help="ask the parser to hog wild")
    parser.add_argument("--fix-unquoted",  action='store_true', default=False,
                        help="ask the parser to try its best to parse unquoted strings/barewords")
    parser.add_argument("--fix-nospace",  action='store_true',
                        default=False, help="fix map keys not to have ' ' after a ':'")
    parser.add_argument("--force-string-keys",  action='store_true',
                        default=False, help="quote every bareword")
    parser.add_argument("--force-commas",  action='store_true',
                        default=False, help="trailing commas")
    parser.add_argument("--quiet", action='store_true',
                        default=False, help="don't print cleaned file")
    parser.add_argument("--in-place", action='store_true',
                        default=False, help="edit file")

    parser.add_argument("--json", action='store_true',
                        default=False, help="output json instead of yaml")

    args = parser.parse_args()  # will only return when action is given

    options = Options(
        fix_unquoted=args.fix_unquoted or args.fix,
        fix_nospace=args.fix_nospace or args.fix,
        force_string_keys=args.force_string_keys,
        force_commas=args.force_commas,
    )

    if args.in_place:
        if args.json:
            print('error: safeyaml --in-place cannot be used with --json')
            print()
            sys.exit(-2)

        if len(args.file) < 1:
            print('error: safeyaml --in-place takes at least one file')
            print()
            sys.exit(-2)

        for filename in args.file:
            with open(filename, 'r+') as fh:
                try:
                    source = fh.read()
                    precheck.check(source)
                    output = io.StringIO()
                    obj = parse(source, output=output, options=options)
                except precheck.PrecheckFailed as p:
                    report_precheck_issues(p.issues, filename, sys.stderr)
                    sys.exit(-2)
                except ParserErr as p:
                    line, col = p.position()
                    print("{}:{}:{}:{}:{}".format(
                        filename, line, col, p.__class__.__name__, p.explain()),
                        file=sys.stderr)
                    sys.exit(-2)
                else:
                    fh.seek(0)
                    fh.truncate(0)
                    fh.write(output.getvalue())

    else:
        input_fh, output_fh = sys.stdin, sys.stdout
        filename = "<stdin>"

        if args.file:
            if len(args.file) > 1:
                print(
                    'error: safeyaml only takes one file as argument, unless --in-place given')
                print()
                sys.exit(-1)

            input_fh = open(args.file[0])  # closed on exit
            filename = args.file[0]

        try:
            source = input_fh.read()

            if args.fix:
                output = precheck.fix(source)
            else:
                precheck.check(source)
                output = ""

            obj = parse(source, options=options)
        except precheck.PrecheckFailed as p:
            report_precheck_issues(p.issues, filename, sys.stderr)
            sys.exit(-2)
        except ParserErr as p:
            line, col = p.position()
            print("{}:{}:{}:{}:{}".format(
                filename, line, col, p.__class__.__name__, p.explain()),
                file=sys.stderr)
            sys.exit(-2)

        if not args.quiet:

            if args.json:
                json.dump(obj, output_fh)
            else:
                output_fh.write(output)

    sys.exit(0)


def report_precheck_issues(issues, filename, output):
    for i in issues:
        print("{}:{}:{}:{}".format(
            filename, i.line(), i.col(), i.explain()),
            file=output)
