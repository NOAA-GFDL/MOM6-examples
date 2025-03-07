#!/usr/bin/env python
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

M = {}
M['start'] = (
    {c: 'name' for c in alpha}
    | {"'": 'str_a'}
    | {'"': 'str_q'}
    | {c: 'number' for c in digit}
    | {'.': 'decimal'}
    | {'-': 'op_negate'}
    | {'=': 'op_assign'}
    | {',': 'op_delim'}
    | {'%': 'op_deref'}
    | {'*': 'op_repeat'}
    | {c: 'space' for c in blank}
    | {'!': 'cmt'}
    | {'\n': 'end'}
)

# Identifiers (and logical True/False)

M['name'] = (
    {c: 'name' for c in alnum}
    | {c: 'end' for c in notchar(alnum)}
)

# Strings

# Apostrophe-delimited strings
M['str_a'] = (
    {c: 'str_a' for c in notchar("'")}
    | {"'": 'str_a_esc'}
)

M['str_a_esc'] = (
    {"'": 'str_a'}
    | {c: 'end' for c in notchar("'")}
)

# Quote-delimited strings
M['str_q'] = (
    {c: 'str_q' for c in notchar('"')}
    | {'"': 'str_q_esc'}
)

M['str_q_esc'] = (
    {'"': 'str_q'}
    | {c: 'end' for c in notchar('"')}
)

# Numbers

M['number'] = (
    {c: 'number' for c in digit}
    | {'.': 'decimal'}
    | {c: 'expmark' for c in 'eEdD'}
    | {c: 'end' for c in notchar(digit + '.eEdD')}
)

M['decimal'] = (
    {c: 'decimal' for c in digit}
    | {c: 'expmark' for c in 'eEdD'}
    | {c: 'end' for c in notchar(digit + 'eEdD')}
)

M['expmark'] = (
    {c: 'exp' for c in digit}
    | {c: 'exp' for c in '-+'}
)

M['exp'] = (
    {c: 'exp' for c in digit}
    | {c: 'end' for c in notchar(digit)}
)

M['op_negate'] = (
    {c: 'number' for c in digit}
    | {'.': 'decimal'}
    # Anything else is an error!
)

# Operators (all two of them!)

M['op_assign'] = (
    {c: 'end' for c in charset}
)

M['op_delim'] = (
    {c: 'end' for c in charset}
)

M['op_deref'] = (
    {c: 'end' for c in charset}
)

M['op_repeat'] = (
    {c: 'end' for c in charset}
    )

# Whitespace

M['space'] = (
    {c: 'space' for c in blank}
    | {c: 'end' for c in notchar(blank)}
)

M['cmt'] = (
    {'\n': 'end'}
    | {c: 'cmt' for c in notchar('\n')}
)


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
        assert(state == 'end')
        lexemes.append(lex)

    return lexemes


def parse_mom6_param(param_file):
    """Generate a dict from a MOM parameter file."""
    params = {}

    for line in param_file:
        try:
            lexemes = scan(line)
        except:
            print(line)
            raise

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

            try:
                assert(len(toks) > 2)
            except:
                print(toks)
                raise

            key = toks[0]
            assert(toks[1] == '=')

            if len(toks[2:]) == 1:
                value = toks[2]
            else:
                try:
                    assert(all(t in '*,' for t in toks[3::2]))
                except:
                    print(toks)
                    raise

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
    # TODO: argparse!
    if len(sys.argv) == 1:
        sys.exit('Usage: ./parse_mom_input.py [filename] [parameter]')

    filename = sys.argv[1]
    if not os.path.isfile(sys.argv[1]):
        sys.exit("File '{}' not found.".format(sys.argv[1]))

    with open(sys.argv[1]) as param_file:
        params = parse_mom6_param(param_file)

    if len(sys.argv) < 3:
        sys.exit('No parameter given.')

    if len(sys.argv) > 2:
        key = sys.argv[2]
        value = params.get(key, "")

        # Print in a shell-friendly format
        if isinstance(value, list):
            print(' '.join(value))
        else:
            print(value)
