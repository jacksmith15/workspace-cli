import traceback

from workspaces.cli.exceptions import WorkspacesCLIError


class TestWorkspacesCLIError:
    @staticmethod
    def should_strip_tags_in_on_error():
        try:
            raise WorkspacesCLIError("Some text with a <bold>tag</bold>.")
        except WorkspacesCLIError as exc:
            exception = exc

        assert "bold" in exception.display
        assert str(exception) == "Some text with a tag."
        assert repr(exception) == "WorkspacesCLIError('Some text with a tag.')"

        output = "\n".join(traceback.format_exception(type(exception), exception, None))
        assert "bold" not in output
