# specification

## grammar

ws = (whitespace| newline | comment)*

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

where indent/dedent happen like in python's lexer, when the indent is bigger/smaller, with an implied indent/dedent
around whole stream

i.e

```
- 1
- 2
```

```
name:
 - list
otherName: {"a": value}
```

can't nest indentation directives on same line

```
- a: thing
- - thing
  - thing
```

```
- 
 a: thing
-
 - thing
 - thing
```

indentation level must increase

```
a: 
- what
```

but

```
a:
 - what
```

## lint errors

- `- - 1` not using a new line for a new indented block

- bareword keys without trailing space
- duplicate key error
- tabs in indentation
- string or int as  root objects
- indented dict with key and empty value
- empty indented list
- reject empty document
- Yes/No/Off/On error
- leading zeros
- octal, hex, sexagesimal errors
- tags, local/builtin !, !! errors
- anchors/aliases & * errors
- directives '%'
- string contents: printables, unicode, surrogates
  cleanup/errors/normalization
  errors for non-json escapes, exce ptfor x,u,U
- errors for document seperators
- errors for "?" key syntax, "|"/">" flow modes
- errors for barewords
- errors for reserved '`' and '@'


