# Specification

This is a rough overview of the subset of YAML, but it's best to think of it as a superset of JSON, with:

Like JSON:

- Root Objects can only be lists or objects, and not strings or numbers.
- Non-Zero Integers cannot have a leading 0
- Strings cannot be multi line

Like YAML:

- Trailing commas allowed in `[]`, or `{}`
- Byte Order Marks are ignored at start of document
- Trailing whitespace is ignored
- Objects and lists have *flow* syntax, or indented block forms.
- A ": " must follow a bareword key
- Strings can use the `\xFF` and `\UFFFFFFFF` along with `\uFFFF` to specify a codepoint
- Unquoted keys are supported that match an indentifier like format (leading character (not a number) followed by any number, char, `.` or `_`.

Unlike both:

- JSON allows surrogate pairs, SafeYAML requries utf-8 and codepoints.
- JSON and YAML allow duplicate keys, SafeYAML rejects them
- Indented maps/lists take a value on the same line *or* an indented map/list on the next line

Not in SafeYAML but in YAML

- `*` and `&` are unsupported operations.
- No tags allowed `!` `!!`.
- No multiline strings, or flow-forms for strings '|' '>'
- All YAML string escapes (except `x` `U` are unsupported)
- Merge keys or '<<' unsupported
- No '?' key syntax
- Indented blocks cannot be nested on the same line.

## Rough Grammar

ws :== (whitespace| newline | comment)*

document :== bom? ws root ws

root :== object | list | indented_object | indented_list

value :== object | list | string | number | builtin

object = '{' ws  key value ws (',' ws key value ws)* (',')? ws '}'

key = string ws ':' ws | bareword ': ' ws

list = '[' ws value  ws (',' ws value ws)* (',')? ws ']'

string = '"' string_contents '"' | '\'' string_contents '\''

number = integer | floating_point

builtin = 'null' | 'true' | 'false'

indented_key :== string | bareword

indented_value :== indented_object | indented_list | value

indented_object :== indent indented_key ': ' indented_value (nl indented_key ': ' idented_value)  dedent

indented_list :== indent '- ' indented_value (nl '- ' idented_value)  dedent

# Indentation Rules

Idented blocks `- item` or `name: value` cannot be nested on the same line, and nested items must be indented further in.

For example

```
- "One"
- "Two"
- 
  name_one: 3  
  name_two: 4

```

And not:

```
name:
- 1 # Error: shoud be indented one
```

Indented blocks must not share lines:

```
- a: thing  # a:thing needs to be on own line

- - thing_a # - thing_a needs own line
  - thing_b
```

Like so:

```
- 
 a: thing
-
 - thing
 - thing
```

# Barewords

Barewords are allowed as the keys for objects, that match a identifier like pattern

- Leading Character (non digit)

In repair, keys still have to match identifiers, but values can have a string until end of line (assuming no special characters)

- Then Alphanumeric, `_` and `.`
