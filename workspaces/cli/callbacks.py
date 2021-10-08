from typing import Any

import click


def consume_stdin(ctx: click.core.Context, param: click.core.Parameter, value: Any):
    """Callback which optionally consumes stdin for arguments."""
    if not value and not click.get_text_stream("stdin").isatty():
        return param.process_value(ctx, [line.strip() for line in click.get_text_stream("stdin").readlines()])
    else:
        return value
