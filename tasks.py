from invoke import task
from sys import platform
from subprocess import call

@task
def coverage(ctx):
    ctx.run("coverage run --branch -m pytest")

@task(coverage)
def coverage_report(ctx):
    ctx.run("coverage html")
    if platform == "win32":
        call(("start", "./htmlcov/index.html"), shell=True)
    else:
        call(("xdg-open", "htmlcov/index.html"))

@task
def test(ctx):
    ctx.run("pytest src")

@task
def start(ctx):
    ctx.run(f"cd ./src && poetry run python index.py")

@task
def build(ctx):
    # In case of dumpbin on Windows issues manually execute BEFORE running this task (or fix your path):
    # set PATH=%PATH%;C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.41.34120\bin\Hostx64\x64
    ctx.run(f"pyside6-deploy ./src/index.py --name \"Blocky Dungeon Mapper\"")

@task
def lint(ctx):
    ctx.run(f"pylint src")

@task
def format(ctx):
    ctx.run(f"autopep8 --in-place --recursive src")