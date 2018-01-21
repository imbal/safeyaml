#!/usr/bin/env python3

import re
import io
import base64
import json

from collections import namedtuple, OrderedDict

whitespace = re.compile(r"(?:\ |\t|\r|\n)+")
        
comment = re.compile(r"(#[^\r\n]*(?:\r?\n|$))+")

int_b10 = re.compile(r"\d[\d]*")
flt_b10 = re.compile(r"\.[\d]+")
exp_b10 = re.compile(r"[eE](?:\+|-)?[\d+]")

string_dq = re.compile(
    r'"(?:[^"\\\n\x00-\x1F\uD800-\uDFFF]|\\(?:[\'"\\/bfnrt]|\\\r?\n|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}))*"')
string_sq = re.compile(
    r"'(?:[^'\\\n\x00-\x1F\uD800-\uDFFF]|\\(?:[\"'\\/bfnrt]|\\\r?\n|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}))*'")

identifier = re.compile(r"(?!\d)[\w\.]+")

str_escapes = {
    'b': '\b',
    'n': '\n',
    'f': '\f',
    'r': '\r',
    't': '\t',
    '/': '/',
    '"': '"',
    "'": "'",
    '\\': '\\',
}

builtin_names = {'null': None, 'true': True, 'false': False}

class ParserErr(Exception):
    def __init__(self, buf, pos, reason=None):
        self.buf = buf
        self.pos = pos
        if reason is None:
            nl = buf.rfind(' ', pos - 10, pos)
            if nl < 0:
                nl = pos - 5
            reason = "Unknown Character {} (context: {})".format(
                repr(buf[pos]), repr(buf[pos - 10:pos + 5]))
        Exception.__init__(self, "{} (at pos={})".format(reason, pos))



def parse(buf, transform=None):
    pos = 1 if buf.startswith("\uFEFF") else 0
    obj, pos = parse_structure(buf, pos, transform)

    m = whitespace.match(buf, pos)
    while m:
        pos = m.end()
        m = comment.match(buf, pos)
        if m:
            pos = m.end()
            m = whitespace.match(buf, pos)

    if pos != len(buf):
        raise ParserErr(buf, pos, "Trailing content: {}".format(
            repr(buf[pos:pos + 10])))

    return obj


def parse_structure(buf, pos, transform):
    return parse_object(buf, pos,transform)

def parse_object(buf, pos, transform=None):
    m = whitespace.match(buf, pos)
    while m:
        pos = m.end()
        m = comment.match(buf, pos)
        if m:
            pos = m.end()
            m = whitespace.match(buf, pos)

    peek = buf[pos]

    if peek == '{':
        out = OrderedDict()

        pos += 1
        m = whitespace.match(buf, pos)
        if m:
            pos = m.end()

        while buf[pos] != '}':
            key, pos = parse_object(buf, pos, transform)

            if key in out:
                raise SemanticErr('duplicate key: {}, {}'.format(key, out))

            m = whitespace.match(buf, pos)
            if m:
                pos = m.end()

            peek = buf[pos]
            if peek == ':':
                pos += 1
                m = whitespace.match(buf, pos)
                if m:
                    pos = m.end()
            else:
                raise ParserErr(
                    buf, pos, "Expected key:value pair but found {}".format(repr(peek)))

            item, pos = parse_object(buf, pos, transform)

            out[key] = item

            peek = buf[pos]
            if peek == ',':
                pos += 1
                m = whitespace.match(buf, pos)
                if m:
                    pos = m.end()
            elif peek != '}':
                raise ParserErr(
                    buf, pos, "Expecting a ',', or a '}' but found {}".format(repr(peek)))
        if transform is not None:
            out = transform(out)
        return out, pos + 1

    elif peek == '[':
        out = []

        pos += 1

        m = whitespace.match(buf, pos)
        if m:
            pos = m.end()

        while buf[pos] != ']':
            item, pos = parse_object(buf, pos, transform)
            out.append(item)

            m = whitespace.match(buf, pos)
            if m:
                pos = m.end()

            peek = buf[pos]
            if peek == ',':
                pos += 1
                m = whitespace.match(buf, pos)
                if m:
                    pos = m.end()
            elif peek != ']':
                raise ParserErr(
                    buf, pos, "Expecting a ',', or a ']' but found {}".format(repr(peek)))

        pos += 1

        if transform is not None:
            out = transform(out)
        return out, pos

    elif peek == "'" or peek == '"':
        s = io.StringIO()

        # validate string
        if peek == "'":
            m = string_sq.match(buf, pos)
            if m:
                end = m.end()
            else:
                raise ParserErr(buf, pos, "Invalid single quoted string")
        else:
            m = string_dq.match(buf, pos)
            if m:
                end = m.end()
            else:
                raise ParserErr(buf, pos, "Invalid double quoted string")

        lo = pos + 1  # skip quotes
        while lo < end - 1:
            hi = buf.find("\\", lo, end)
            if hi == -1:
                s.write(buf[lo:end - 1])  # skip quote
                break

            s.write(buf[lo:hi])

            esc = buf[hi + 1]
            if esc in str_escapes:
                s.write(str_escapes[esc])
                lo = hi + 2
            elif esc == 'x':
                n = int(buf[hi + 2:hi + 4], 16)
                s.write(chr(n))
                lo = hi + 4
            elif esc == 'u':
                n = int(buf[hi + 2:hi + 6], 16)
                if 0xD800 <= n <= 0xDFFF:
                    raise ParserErr(
                        buf, hi, 'string cannot have surrogate pairs')
                s.write(chr(n))
                lo = hi + 6
            elif esc == 'U':
                n = int(buf[hi + 2:hi + 10], 16)
                if 0xD800 <= n <= 0xDFFF:
                    raise ParserErr(
                        buf, hi, 'string cannot have surrogate pairs')
                s.write(chr(n))
                lo = hi + 10
            elif esc == '\n':
                lo = hi + 2
            elif (buf[hi + 1:hi + 3] == '\r\n'):
                lo = hi + 3
            else:
                raise ParserErr(
                    buf, hi, "Unkown escape character {}".format(repr(esc)))

        out = s.getvalue()

        if transform is not None:
            out = transform(out)
        return out, end

    elif peek in "-+0123456789":

        flt_end = None
        exp_end = None

        sign = +1

        start = pos

        if buf[pos] in "+-":
            if buf[pos] == "-":
                sign = -1
            pos += 1
        peek = buf[pos]

        leading_zero = (peek == '0')
        m = int_b10.match(buf, pos)
        if m:
            int_end = m.end()
            end = int_end
        else:
            raise ParserErr(buf, pos, "Invalid number")

        t = flt_b10.match(buf, end)
        if t:
            flt_end = t.end()
            end = flt_end

        e = exp_b10.match(buf, end)
        if e:
            exp_end = e.end()
            end = exp_end

        if flt_end or exp_end:
            out = sign * float(buf[pos:end])
        else:
            out = sign * int(buf[pos:end])
            if leading_zero and out != 0:
                raise Exception('Nope')

        if transform is not None:
            out = transform(out)
        return out, end

    else:
        m = identifier.match(buf, pos)
        if m:
            end = m.end()
            item = buf[pos:end]
        else:
            raise ParserErr(buf, pos)

        if item not in builtin_names:
            raise ParserErr(
                buf, pos, "{} is not a recognised built-in".format(repr(item)))

        out = builtin_names[item]

        if transform is not None:
            out = transform(out)
        return out, end

    raise ParserErr(buf, pos)


if __name__ == '__main__':
    tests = """
        0
        1.2
        -3.4
        +5.6
        "test"
        'test'
        [1,2,3]
        [1,2,3]
        {"a":1}
        {'b':2}
        1 # foo """
    for test in tests.split("\n"):
        test.strip()
        if not test: continue
        print(repr(test))
        print('=>', parse(test))
