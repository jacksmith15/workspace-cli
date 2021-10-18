import re
from textwrap import dedent, indent

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

DEFAULT_CONFIG = {
    "startDelay": 600,
    "typeDelay": 90,
    "lineDelay": 1500,
    "cursor": "▋",
}


class TermynalExtension(Extension):
    def __init__(self, **kwargs):
        # Define config options and defaults
        self.config = {
            "startDelay": [600, "Delay before animation, in ms."],
            "typeDelay": [90, "Delay between each typed character, in ms."],
            "lineDelay": [1500, "Delay between each line, in ms."],
            "cursor": ["▋", "Character to use for cursor."],
        }
        # Call the parent class's __init__ method to configure options
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(TermynalPreprocessor(md, self.getConfigs()), "termynal_block", 26)


class TermynalPreprocessor(Preprocessor):
    FENCED_BLOCK_RE = re.compile(
        dedent(
            r"""
(?P<fence>^(?:~{3,}|`{3,}))[ ]*                          # opening fence
(\.?(?P<lang>[console|terminal]+)[ ]*)                   # language to trap
\n                                                       # newline (end of opening fence)
(?P<code>.*?)(?<=\n)                                     # the code block
(?P=fence)[ ]*$                                          # closing fence
"""
        ),
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    def __init__(self, md, config):
        super().__init__(md)
        self.config = {**DEFAULT_CONFIG, **config}

    def run(self, lines):
        text = "\n".join(lines)
        index = 0
        match = self.FENCED_BLOCK_RE.search(text)
        while match:
            code = self.format_termynal(match, index)
            placeholder = self.md.htmlStash.store(code)
            text = "{}\n{}\n{}".format(text[: match.start()], placeholder, text[match.end() :])
            match = self.FENCED_BLOCK_RE.search(text)
            index += 1
        return text.split("\n")

    def format_termynal(self, match: re.Match, index: int):
        """Convert a code block to a termynal."""
        entries = []
        for line in match.group("code").splitlines():
            if line.startswith("$"):
                entries.append(f'<span data-ty="input">{html_escape(line.lstrip("$").lstrip())}</span>')
            else:
                entries.append(f"<span data-ty>{html_escape(line)}</span>")

        body = "\n".join(entries)
        return f"""
<div id="termynal-{index}" data-termynal class="termynal" {self.config_attributes}>
{indent(body, " " * 4)}
</div>
"""

    @property
    def config_attributes(self):
        return " ".join(f"data-ty-{key}={value}" for key, value in self.config.items())


def html_escape(txt):
    """ basic html escaping """
    txt = txt.replace("&", "&amp;")
    txt = txt.replace("<", "&lt;")
    txt = txt.replace(">", "&gt;")
    txt = txt.replace('"', "&quot;")
    return txt


def makeExtension(**kwargs):
    return TermynalExtension(**kwargs)
