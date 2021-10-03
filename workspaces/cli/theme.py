import re
from typing import List

import click

_BOLD = "\x1b[1m"
_RESET = "\x1b[0m"


class Colors:
    white = 255
    green = 107
    turquoise = 73
    purple = 140
    yellow = 179
    red = 167


def echo(message=None, file=None, nl=True, err=True, color=None):
    click.echo(message=colorize(message), file=file, nl=nl, err=err, color=color)


def colorize(message: str) -> str:
    return "".join([token for token in _tokenize(message)])


def strip_tags(message: str) -> str:
    return "".join([token for token in _tokenize(message, strip_tags=True)])


def _tokenize(string: str, strip_tags: bool = False):
    style_tags = {
        "header": Colors.turquoise,
        "success": Colors.green,
        "accent": Colors.purple,
        "warning": Colors.yellow,
        "error": Colors.red,
    }
    tokens = {
        "TAGOPEN": r"<[A-Za-z_-]+>",
        "TAGCLOSE": r"</[(A-Za-z_-]+>",
        "DEFAULT": r".",
    }
    token_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in tokens.items())
    stack: List[str] = []

    def parse_tag(tag: str):
        tags = set(style_tags) | {"bold"}
        if tag in tags:
            return tag
        for full_tag in tags:
            if full_tag.startswith(tag):
                return full_tag

    def reset_code():
        style = next((tag for tag in reversed(stack) if tag in style_tags), None)
        bold = "bold" in stack
        result = _RESET
        if style:
            result = result + _color_code(style_tags[style])
        if bold:
            result = result + _BOLD
        return result

    for match in re.finditer(token_regex, string, re.DOTALL):
        kind = match.lastgroup
        token = match.group()
        if kind == "TAGOPEN":
            if strip_tags:
                continue
            tag = parse_tag(token[1:-1])
            if tag == "bold":
                yield _BOLD
            elif tag in style_tags:
                yield _color_code(style_tags[tag])
            else:
                assert False, f"Unknown token {token}"
            stack.append(tag)
        elif kind == "TAGCLOSE":
            if strip_tags:
                continue
            tag = parse_tag(token[2:-1])
            assert stack and (stack[-1] == tag), f"Invalid closing tag {token}"
            stack.pop()
            yield reset_code()
        else:
            yield token
    stack.clear()
    if not strip_tags:
        yield reset_code()


def _color_code(number: int):
    assert number < 256
    return f"\x1b[38;5;{number}m"


def demo_theme():
    echo(
        """<h><b>This is a header</b></h>

This is some regular text, with <a>accented</a> parts.

Let's draw attention to the <s>good</s> things.

<w>This is something to <b>watch out</b> for!

<e>Something here has gone <b>very wrong</b>!</e>

"""
    )
