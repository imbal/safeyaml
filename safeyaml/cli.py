import argparse
import io
import sys

from .parser import Options
from .parser import ParserErr
from .parser import parse


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
                    output = io.StringIO()
                    obj = parse(fh.read(), output=output, options=options)
                except ParserErr as p:
                    line, col = p.position()
                    print("{}:{}:{}:{}".format(filename, line,
                                               col, p.explain()), file=sys.stderr)
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
            filename = args.file

        try:
            output = io.StringIO()
            obj = parse(input_fh.read(), output=output, options=options)
        except ParserErr as p:
            line, col = p.position()
            print("{}:{}:{}:{}".format(filename, line,
                                       col, p.explain()), file=sys.stderr)
            sys.exit(-2)

        if not args.quiet:

            if args.json:
                json.dump(obj, output_fh)
            else:
                output_fh.write(output.getvalue())

    sys.exit(0)
