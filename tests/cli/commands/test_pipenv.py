from tests.cli.commands.helpers import PROJECT_ROOT, run


class TestPipenvE2E:
    @staticmethod
    def should_manage_pipenv_projects():
        # WHEN I create two pipenv projects
        workspaces = ["library-one", "library-two"]
        for workspace in workspaces:
            run(["workspaces", "new", "--type", "pipenv", f"libs/{workspace}"])
        # THEN they should both exist
        assert set(run(["workspaces", "list"]).text.splitlines()) == {"library-one", "library-two"}
        # AND I should be able to run commands in them
        assert set(run(["workspaces", "run", "pwd"]).stdout.splitlines()) == {
            str(PROJECT_ROOT / f"libs/{workspace}") for workspace in workspaces
        }
        # AND GIVEN one depends on the other
        with open(PROJECT_ROOT / "libs/library-two/setup.py", "w", encoding="utf-8") as file:
            file.write(
                """from setuptools import setup, find_packages

setup(
    name="library-two",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
)
"""
            )
        run(["pipenv", "install", "--editable", "../library-two"], cwd="libs/library-one")
        # WHEN I check dependees
        result = run(["workspaces", "dependees", "library-two"])
        # THEN the correct dependees are identified
        assert set(result.text.splitlines()) == {"library-one", "library-two"}
        # AND I can sync dependencies
        run(["workspaces", "sync", "library-one"])
