import click


class Palette:
    white = 255
    green = 107
    turquoise = 73
    purple = 140
    yellow = 179
    red = 167


def text(string: str) -> str:
    return click.style(string, fg="white")


def header(string: str) -> str:
    return click.style(string, fg=Palette.green)  # type: ignore[arg-type]


def accent(string: str, level: int = 0) -> str:
    """Use to accent text, separating from other text items.

    Two levels are available.
    """
    color = {
        0: Palette.turquoise,
        1: Palette.purple,
    }[level]
    return click.style(string, fg=color)  # type: ignore[arg-type]


def attention(string: str) -> str:
    """Use to call attention of the user, e.g. a warning."""
    return click.style(string, fg=Palette.yellow)  # type: ignore[arg-type]


def error(string: str, accent: bool = False) -> str:
    """Indicate to the user that something is wrong."""
    return click.style(string, fg=Palette.red, bold=accent)  # type: ignore[arg-type]


def demo_theme():
    """Print each style."""
    for style in (
        (header,),
        (text,),
        (accent, 0),
        (accent, 1),
        (attention,),
        (error,),
        (error, True),
    ):
        click.echo(style[0](f"{style[0].__name__}", *style[1:]))
