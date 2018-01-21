# specification

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

indented_value :== indented_object | indented_list | value

indented_object = indent key ': ' indented_value (key ': ' idented_value)  dedent

indented_list = indent '- ' indented_value (key ': ' idented_value)  dedent
