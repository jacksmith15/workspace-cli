import traceback

from workspace.cli.exceptions import WorkspaceCLIError


class TestWorkspaceCLIError:
    @staticmethod
    def should_strip_tags_in_on_error():
        try:
            raise WorkspaceCLIError("Some text with a <bold>tag</bold>.")
        except WorkspaceCLIError as exc:
            exception = exc

        assert "bold" in exception.display
        assert str(exception) == "Some text with a tag."
        assert repr(exception) == "WorkspaceCLIError('Some text with a tag.')"

        output = "\n".join(traceback.format_exception(type(exception), exception, None))
        assert "bold" not in output
