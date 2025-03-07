#!/usr/bin/env python3
import argparse
import os
import string
import sys

# The Fortran Alphabet
alpha = string.ascii_letters
digit = string.digits
alnum = alpha + digit + '_'
blank = ' \t\f\r'
special = '=+-*/\\()[]{},.:;!"%&~<>?\'`^|$#@\n'
charset = alnum + blank + special


def notchar(chars, source=charset):
    return ''.join([c for c in source if c not in chars])


# Scanner
# NOTE: Using legacy <3.9 syntax for dict updates
M = {
    'start': dict(
        **{c: 'name' for c in alpha},
        **{"'": 'str_a'},
        **{'"': 'str_q'},
        **{c: 'number' for c in digit},
        **{'.': 'decimal'},
        **{'-': 'op_negate'},
        **{'=': 'op_assign'},
        **{',': 'op_delim'},
        **{'%': 'op_deref'},
        **{'*': 'op_repeat'},
        **{c: 'space' for c in blank},
        **{'!': 'cmt'},
        **{'\n': 'end'},
    ),
    'name': dict(
        **{c: 'name' for c in alnum},
        **{c: 'end' for c in notchar(alnum)},
    ),
    'str_a': dict(
        **{c: 'str_a' for c in notchar("'")},
        **{"'": 'str_a_esc'},
    ),
    'str_a_esc': dict(
        **{"'": 'str_a'},
        **{c: 'end' for c in notchar("'")},
    ),
    # Quote-delimited strings
    'str_q': dict(
        **{c: 'str_q' for c in notchar('"')},
        **{'"': 'str_q_esc'},
    ),
    'str_q_esc': dict(
        **{'"': 'str_q'},
        **{c: 'end' for c in notchar('"')},
    ),
    'number': dict(
        **{c: 'number' for c in digit},
        **{'.': 'decimal'},
        **{c: 'expmark' for c in 'eEdD'},
        **{c: 'end' for c in notchar(digit + '.eEdD')},
    ),
    'decimal': dict(
        **{c: 'decimal' for c in digit},
        **{c: 'expmark' for c in 'eEdD'},
        **{c: 'end' for c in notchar(digit + 'eEdD')},
    ),
    'expmark': dict(
        **{c: 'exp' for c in digit},
        **{c: 'exp' for c in '-+'},
    ),
    'exp': dict(
        **{c: 'exp' for c in digit},
        **{c: 'end' for c in notchar(digit)},
    ),
    'op_negate': dict(
        **{c: 'number' for c in digit},
        **{'.': 'decimal'},
        # Anything else is an error!
    ),
    'op_assign': dict(
        **{c: 'end' for c in charset},
    ),
    'op_delim': dict(
        **{c: 'end' for c in charset},
    ),
    'op_deref': dict(
        **{c: 'end' for c in charset},
    ),
    'op_repeat': dict(
        **{c: 'end' for c in charset},
    ),
    'space': dict(
        **{c: 'space' for c in blank},
        **{c: 'end' for c in notchar(blank)},
    ),
    'cmt': dict(
        **{'\n': 'end'},
        **{c: 'cmt' for c in notchar('\n')},
    ),
}


def scan(line):
    """Generate a list of lexemes from a character string."""
    lexemes = []
    lex = ''
    state = 'start'

    for char in line:
        state = M[state][char]

        if state != 'end':
            lex += char

        else:
            lexemes.append(lex)
            lex = char
            state = M['start'][char]

    # Finalize a non-terminated line
    if char != '\n':
        state = M[state]['\n']
        lexemes.append(lex)

    return lexemes


def parse_mom6_param(param_file):
    """Generate a dict from a MOM parameter file."""
    params = {}

    for line in param_file:
        lexemes = scan(line)

        # Remove the whitespace and comment tokens
        toks = [lx for lx in lexemes if lx.strip() and not lx[0] == '!']
        if toks:
            # Hand-parsing the content!

            # Exit current parameter block
            # TODO: Verify that we are actually in a block!
            if toks[0] == '%':
                break

            if toks[1] == '%':
                params[toks[0]] = parse_mom6_param(param_file)
                continue

            # TODO: Long-form blocks? A%B%C = 1

            key = toks[0]

            if len(toks[2:]) == 1:
                value = toks[2]
            else:
                # First strip out the list delimiters
                value = [v for v in toks[2:] if v != ',']

                # Replace any repeat tokens if present
                if '*' in value:
                    count = None
                    new_value = []
                    for v in value:
                        if count is not None:
                            new_value += count * [v]
                            count = None
                        elif v == '*':
                            count = int(new_value.pop())
                        else:
                            new_value.append(v)

                    value = new_value

            # Not entirely sure how to handle data types, but for now just
            # strip away string delimiters.
            if (isinstance(value, str) and value[0] in ("'", '"') and
                    value[0] == value[-1]):
                value = value[1:-1]

            params[key] = value

    return params


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to input parameter file")
    parser.add_argument("param", help="Parameter name")
    args = parser.parse_args()

    filename = args.input
    if not os.path.isfile(filename):
        sys.exit("File '{}' not found.".format(filename))

    with open(filename) as param_file:
        params = parse_mom6_param(param_file)

    key = args.param
    value = params.get(key, "")

    # Print in a shell-friendly format
    if isinstance(value, list):
        print(' '.join(value))
    else:
        print(value)
