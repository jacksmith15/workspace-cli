import re
from textwrap import dedent, indent

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class GithubFlavorAdmonitionsExtension(Extension):
    """Extension which converts github flavor admonitions to regular admonitions.

    Allows writing admonitions with quotes, and converts them to admonitions, e.g.

    > â ī¸ This is a warning!

    Becomes

    ::: warning
        This is a warning!
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(GithubFlavorAdmonitionsPreprocessor(md), "github_flavor_admonitions", 27)


class GithubFlavorAdmonitionsPreprocessor(Preprocessor):

    TYPE_MAPPING = {
        "đ": "note",
        "đ": "abstract",
        "âšī¸": "info",
        "đĄ": "tip",
        "â": "success",
        "âī¸": "success",
        "â": "question",
        "â ī¸": "warning",
        "â": "failure",
        "âĄ": "danger",
        "đ": "bug",
        "đ": "example",
        "đī¸": "quote",
    }

    GITHUB_MAPPING = {
        ":memo:": "đ",
        ":page_with_curl:": "đ",
        ":information_source:": "âšī¸",
        ":bulb:": "đĄ",
        ":white_check_mark:": "â",
        ":heavy_check_mark:": "âī¸",
        ":question:": "â",
        ":warning:": "â ī¸",
        ":x:": "â",
        ":zap:": "âĄ",
        ":bug:": "đ",
        ":open_book:": "đ",
        ":studio_microphone:": "đī¸",
    }

    QUOTE_BLOCK_RE = re.compile(rf"""
^>[ ]*(?P<icon>{"|".join([*TYPE_MAPPING, *GITHUB_MAPPING])})(?P<content>.*?)(?=\n[^>])
""",
    re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    def run(self, lines):
        text = "\n".join(lines)
        match = self.QUOTE_BLOCK_RE.search(text)
        while match:
            admonition = self.format_admonition(match)
            # placeholder = self.md.htmlStash.store(admonition)
            text = "{}\n{}\n{}".format(text[: match.start()], admonition, text[match.end() :])
            match = self.QUOTE_BLOCK_RE.search(text)
        return text.split("\n")

    def format_admonition(self, match):
        icon = self.GITHUB_MAPPING.get(match.group("icon"), match.group("icon"))
        type_ = self.TYPE_MAPPING[icon]
        content = dedent("\n\n".join([line.lstrip(">") for line in match.group("content").splitlines()]))
        return "\n".join([f"!!! {type_}", indent(content, " " * 4)])


def makeExtension(**kwargs):
    return GithubFlavorAdmonitionsExtension(**kwargs)
