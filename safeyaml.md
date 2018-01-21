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

## lint errors

- tabs in indentation
- allowed root objects
- missing values in dict
- empty document?
- Yes/No/Off/On
- octal, hex, sexagesimal errors
- tags, local/builtin
- anchors/aliases
- directives
- string contents: printables, unicode, surrogates
- string escapes: \nl & trailing whitespace
- dict contents: duplicate keys, normalisation
- document seperators
- "?" key syntax, "|"/">" flow modes
- barewords
- reserved '`' and '@'


