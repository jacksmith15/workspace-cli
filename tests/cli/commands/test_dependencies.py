from tests.cli.commands.helpers import run


class TestDependencies:
    @staticmethod
    def should_identify_direct_dependencies():
        # GIVEN I have three projects
        paths = {"libs/library-one", "libs/library-two", "libs/library-three"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND one of them depends on the other
        run(["poetry", "add", "../library-one"], cwd="libs/library-two")
        # WHEN I run workspace dependencies on the dependee project
        result = run(["workspace", "dependencies", "library-two"])
        # THEN the target and dependent project should be included in the result
        assert set(result.text.splitlines()) == {"library-one", "library-two"}

    @staticmethod
    def should_identify_transitive_dependencies():
        # GIVEN I have four projects
        paths = {"libs/library-one", "libs/library-two", "libs/library-three", "libs/library-four"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND the first depends on the second
        run(["poetry", "add", "../library-two"], cwd="libs/library-one")
        # AND the second depends on the third
        run(["poetry", "add", "../library-three"], cwd="libs/library-two")
        # WHEN I run workspace dependencies on the first project
        result = run(["workspace", "dependencies", "library-one"])
        # THEN the first three should be included in the result
        assert set(result.text.splitlines()) == {"library-one", "library-two", "library-three"}

    @staticmethod
    def should_ignore_transitive_dependencies_when_specified():
        # GIVEN I have four projects
        paths = {"libs/library-one", "libs/library-two", "libs/library-three", "libs/library-four"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND the first depends on the second
        run(["poetry", "add", "../library-two"], cwd="libs/library-one")
        # AND the second depends on the third
        run(["poetry", "add", "../library-three"], cwd="libs/library-two")
        # WHEN I run workspace dependencies with the --no-transitive flag on the first project
        result = run(["workspace", "dependencies", "--no-transitive", "library-one"])
        # THEN only the second two should be included in the result
        assert set(result.text.splitlines()) == {"library-one", "library-two"}

    @staticmethod
    def should_return_csv_format_when_specified():
        # GIVEN I have two projects
        paths = {"libs/library-one", "libs/library-two"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND one of them depends on the other
        run(["poetry", "add", "../library-one"], cwd="libs/library-two")
        # WHEN I run workspace dependencies on the dependency project
        result = run(["workspace", "dependencies", "--output", "csv", "library-two"])
        # THEN the result should be in csv format
        assert result.text == "library-one,library-two"

    @staticmethod
    def should_warn_when_the_specified_project_does_not_match():
        # WHEN I run workspace dependencies with an unknown project
        result = run(["workspace", "dependencies", "library-one"])
        # THEN the exit code is 0
        assert result.returncode == 0
        # AND the expected error message is displayed
        assert "No projects selected" in result.text
