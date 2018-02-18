import json
import yaml
from yaml import nodes
from collections import namedtuple


class Issue(namedtuple('_Issue', 'type node')):
    def line(self):
        return self.node.start_mark.line
    
    def col(self):
        return self.node.start_mark.column

    def explain(self):
        if self.type == 'unquoted_string':
            return "UnquotedString:{} should be quoted".format(self.node.value)
        elif self.type == 'ambiguous_value':
            if get_tag(self.node) == 'bool':
                bool_value = yaml.load(self.node.value)
                return (
                    "AmbiguousValue:`{}` could be a string or a boolean. "
                    "Either surround it in quotes or replace it with `{}`."
                    .format(self.node.value, ('true' if bool_value else 'false'))
                )


class PrecheckFailed(Exception):
    def __init__(self, issues):
        self.issues = issues


def check(source):
    issues = all_issues(source)
    if issues:
        raise PrecheckFailed(issues)


def fix(source):
    issues = all_issues(source)
    unfixable_issues = [i for i in issues if i.type != 'unquoted_string']

    if unfixable_issues:
        raise PrecheckFailed(unfixable_issues)

    return replace_substrings(source, (
        (i.node.start_mark.index, i.node.end_mark.index, json.dumps(i.node.value))
        for i in issues
    ))


def all_issues(source):
    return list(find_issues(find_scalars(yaml.compose(source))))


def find_scalars(node):
    if isinstance(node, nodes.ScalarNode):
        yield node
    elif isinstance(node, nodes.MappingNode):
        for (key, value) in node.value:
            for n in find_scalars(value):
                yield n
    elif isinstance(node, nodes.SequenceNode):
        for value in node.value:
            for n in find_scalars(value):
                yield n


def find_issues(nodes):
    for node in nodes:
        # TODO: cover all possible ambiguous values
        if get_tag(node) == 'bool' and node.value not in ['true', 'false']:
            yield Issue(type='ambiguous_value', node=node)

        if get_tag(node) == 'str' and node.style not in ["'", '"']:
            yield Issue(type='unquoted_string', node=node)


def get_tag(node):
    return node.tag.rpartition(':')[2]


def replace_substrings(source, substitutions):
    output = ''
    pos = 0

    for (start, end, replacement) in substitutions:
        output += source[pos:start]
        output += replacement
        pos = end
    
    output += source[pos:]

    return output
