import pytest

from workspace.cli.theme import colorize, strip_tags


class TestColorize:
    @staticmethod
    def should_convert_tags_to_escape_code():
        text = """<h><b>This is a header</b></h>

This is some regular text, with <a>accented</a> parts.

Let's draw attention to the <s>good</s> things.

<w>This is something to <bold>watch out</bold> for!</w>

<e>Something here has gone <b>very wrong</b>!</e>

"""
        output = colorize(text)
        assert (
            output
            == """\x1b[38;5;73m\x1b[1mThis is a header\x1b[0m\x1b[38;5;73m\x1b[0m

This is some regular text, with \x1b[38;5;140maccented\x1b[0m parts.

Let's draw attention to the \x1b[38;5;107mgood\x1b[0m things.

\x1b[38;5;179mThis is something to \x1b[1mwatch out\x1b[0m\x1b[38;5;179m for!\x1b[0m

\x1b[38;5;167mSomething here has gone \x1b[1mvery wrong\x1b[0m\x1b[38;5;167m!\x1b[0m

\x1b[0m"""
        )

        assert (
            strip_tags(text)
            == """This is a header

This is some regular text, with accented parts.

Let's draw attention to the good things.

This is something to watch out for!

Something here has gone very wrong!

"""
        )

    @staticmethod
    def should_fail_for_unknown_token():
        with pytest.raises(AssertionError):
            colorize("<foo>bar</foo>")
