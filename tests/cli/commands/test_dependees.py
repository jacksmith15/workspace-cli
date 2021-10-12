from tests.cli.commands.helpers import run


class TestDependees:
    @staticmethod
    def should_identify_direct_dependees():
        # GIVEN I have three projects
        paths = {"libs/library-one", "libs/library-two", "libs/library-three"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND one of them depends on the other
        run(["poetry", "add", "../library-one"], cwd="libs/library-two")
        # WHEN I run workspace dependees on the dependency project
        result = run(["workspace", "dependees", "library-one"])
        # THEN the target and dependent project should be included in the result
        assert set(result.text.splitlines()) == {"library-one", "library-two"}

    @staticmethod
    def should_identify_transitive_dependees():
        # GIVEN I have four projects
        paths = {"libs/library-one", "libs/library-two", "libs/library-three", "libs/library-four"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND the first depends on the second
        run(["poetry", "add", "../library-two"], cwd="libs/library-one")
        # AND the second depends on the third
        run(["poetry", "add", "../library-three"], cwd="libs/library-two")
        # WHEN I run workspace dependees on the third project
        result = run(["workspace", "dependees", "library-three"])
        # THEN the first three should be included in the result
        assert set(result.text.splitlines()) == {"library-one", "library-two", "library-three"}

    @staticmethod
    def should_ignore_transitive_dependees_when_specified():
        # GIVEN I have four projects
        paths = {"libs/library-one", "libs/library-two", "libs/library-three", "libs/library-four"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND the first depends on the second
        run(["poetry", "add", "../library-two"], cwd="libs/library-one")
        # AND the second depends on the third
        run(["poetry", "add", "../library-three"], cwd="libs/library-two")
        # WHEN I run workspace dependees with the --no-transitive flag on the third project
        result = run(["workspace", "dependees", "--no-transitive", "library-three"])
        # THEN only the second two should be included in the result
        assert set(result.text.splitlines()) == {"library-two", "library-three"}

    @staticmethod
    def should_return_csv_format_when_specified():
        # GIVEN I have two projects
        paths = {"libs/library-one", "libs/library-two"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND one of them depends on the other
        run(["poetry", "add", "../library-one"], cwd="libs/library-two")
        # WHEN I run workspace dependees on the dependency project
        result = run(["workspace", "dependees", "--output", "csv", "library-one"])
        # THEN the result should be in csv format
        assert result.text == "library-one,library-two"

    @staticmethod
    def should_warn_when_the_specified_project_does_not_match():
        # WHEN I run workspace dependees with an unknown project
        result = run(["workspace", "dependees", "library-one"])
        # THEN the exit code is 0
        assert result.returncode == 0
        # AND the expected error message is displayed
        assert "No projects selected" in result.text
