from invoke import task
from sys import platform
from subprocess import call, check_output

@task
def coverage(ctx):
    ctx.run("coverage run --branch -m pytest")

@task()
def coverage_report(ctx):
    ctx.run("coverage html")
    if platform == "win32":
        call(("start", "htmlcov/index.html"))
    else:
        call(("xdg-open", "htmlcov/index.html"))

@task
def test(ctx):
    ctx.run("pytest src")

@task
def start(ctx):
    ctx.run(f"cd ./src && poetry run python index.py")
