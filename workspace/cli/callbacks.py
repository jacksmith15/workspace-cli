from typing import Any

import click


def consume_stdin(ctx: click.core.Context, param: click.core.Parameter, value: Any):
    """Callback which optionally consumes stdin for arguments."""
    stdin = click.get_text_stream("stdin")
    if not value and not stdin.isatty():
        return param.type_cast_value(ctx, [line.strip() for line in stdin.readlines()])
    else:
        return value
