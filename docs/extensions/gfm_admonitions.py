import re
from textwrap import dedent, indent

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class GithubFlavorAdmonitionsExtension(Extension):
    """Extension which converts github flavor admonitions to regular admonitions.

    Allows writing admonitions with quotes, and converts them to admonitions, e.g.

    > ⚠️ This is a warning!

    Becomes

    ::: warning
        This is a warning!
    """

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(GithubFlavorAdmonitionsPreprocessor(md), "github_flavor_admonitions", 27)


class GithubFlavorAdmonitionsPreprocessor(Preprocessor):

    TYPE_MAPPING = {
        "📝": "note",
        "📃": "abstract",
        "ℹ️": "info",
        "💡": "tip",
        "✅": "success",
        "✔️": "success",
        "❓": "question",
        "⚠️": "warning",
        "❌": "failure",
        "⚡": "danger",
        "🐛": "bug",
        "📖": "example",
        "🎙️": "quote",
    }

    GITHUB_MAPPING = {
        ":memo:": "📝",
        ":page_with_curl:": "📃",
        ":information_source:": "ℹ️",
        ":bulb:": "💡",
        ":white_check_mark:": "✅",
        ":heavy_check_mark:": "✔️",
        ":question:": "❓",
        ":warning:": "⚠️",
        ":x:": "❌",
        ":zap:": "⚡",
        ":bug:": "🐛",
        ":open_book:": "📖",
        ":studio_microphone:": "🎙️",
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
