SafeYAML
========

NOTE: This is a speculative README from @aanand, and a speculative attempt at
implementation & specification by @tef.

SafeYAML is an aggressively small subset of YAML. It's everything you need for
human-readable-and-writable configuration files, and nothing more.

You don't need to integrate a new parser library: keep using your language's
best-maintained YAML parser, and drop the ``safeyaml`` linter into your CI
pipeline, pre-commit hook and/or text editor. It's a standalone script, so you
don't have any new dependencies to worry about.


What's allowed?
---------------

It's best described as JSON plus the following:

- You can use indentation for structure (braces are optional)
- Keys can be unquoted (``foo: 1``, rather than ``"foo": 1``), or quoted with ``''`` instead
- Single-line comments with ``#``
- Trailing commas allowed within ``[]`` or ``{}``

Here's an example::

  title: "SafeYAML Example"

  database:
    server: "192.168.1.1"

    ports:
      - 8000
      - 8001
      - 8002

    enabled: true

  servers:
    # JSON-style objects
    alpha: {
      "ip": "10.0.0.1",
      "names": [
        "alpha",
        "alpha.server",
      ],
    }
    beta: {
      "ip": "10.0.0.2",
      "names": ["beta"],
    }

As for what's disallowed: a lot. String values must always be quoted. Boolean
values must be written as ``true`` or ``false`` (``yes``, ``Y``, ``y``, ``on``
etc are not allowed). Indented blocks must start on their own line.

No anchors, no references. No multi-line strings. No multi-document streams. No
custom tagged values. No Octal, or Hexadecimal. *No sexagesimal numbers.*


Why?
----

The prevalence of YAML as a configuration format is testament to the
unfriendliness of JSON, but the YAML language is terrifyingly huge and full of
pitfalls for people just trying to write configuration (the number of ways to
write a Boolean value is a prime example).

There have been plenty of attempts to define other configuration languages
(TOML, Hugo, HJSON, etc). Subjectively, most of them are less friendly than YAML
(``.ini``-style formats quickly become cumbersome for structures with two or
more levels of nesting). Objectively, *all* of them face the uphill struggle of
needing a parser to be written and maintained in every popular programming
language.

A language which is a subset of YAML, however, needs no new parser - just a
linter to ensure that files conform. The ``safeyaml`` linter is an independent
executable, so whatever language and tooling you're currently using, you can
continue to use it - it's just one more step in your code quality process.


How do I use it?
----------------

The ``safeyaml`` executable will do its best to rewrite your YAML code, or fail
with an error if it can't. Here's an example of a rewrite::

  $ cat input.yaml
  title: My YAML file

  $ safeyaml input.yaml
  title: "My YAML file"

By default, the rewritten YAML is printed to standard output. You can pass
``-w`` to rewrite input files in-place instead.

Here's an example of an error, which must be fixed manually::

  $ cat input.yaml
  command: yes

  $ safeyaml input.yaml
  input.yaml:1:9: found unquoted value `yes`, which could be a string or a
  boolean. Please either surround it in quotes if it's a string, or replace it
  with `true` if it's a boolean.


How do I generate it?
---------------------

Don't. That's not what YAML is for. Generate JSON if you need to serialize data.
