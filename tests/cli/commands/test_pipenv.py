from tests.cli.commands.helpers import WORKSPACE_ROOT, run


class TestPipenvE2E:
    @staticmethod
    def should_manage_pipenv_projects():
        # WHEN I create two pipenv projects
        projects = ["library-one", "library-two"]
        for project in projects:
            run(["workspace", "new", "--type", "pipenv", f"libs/{project}"])
        # THEN they should both exist
        assert set(run(["workspace", "list", "--output", "names"]).text.splitlines()) == {"library-one", "library-two"}
        # AND I should be able to run commands in them
        assert set(run(["workspace", "run", "-c", "pwd"]).stdout.splitlines()) == {
            str(WORKSPACE_ROOT / f"libs/{project}") for project in projects
        }
        # AND GIVEN one depends on the other
        with open(WORKSPACE_ROOT / "libs/library-two/setup.py", "w", encoding="utf-8") as file:
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
        result = run(["workspace", "dependees", "library-two"])
        # THEN the correct dependees are identified
        assert set(result.text.splitlines()) == {"library-one", "library-two"}
        # AND I can sync dependencies
        run(["workspace", "sync", "library-one"])
