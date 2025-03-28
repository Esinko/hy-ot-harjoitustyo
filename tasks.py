from invoke import task
from sys import platform
from subprocess import call

@task
def coverage(ctx):
    ctx.run("coverage run --branch -m pytest", pty=True)

@task()
def coverage_report(ctx):
    ctx.run("coverage html", pty=True)
    if platform == "win32":
        call(("start", "htmlcov/index.html"))
    else:
        call(("xdg-open", "htmlcov/index.html"))

@task
def test(ctx):
    ctx.run("pytest src", pty=True)

@task
def start(ctx):
    ctx.run("python3 src/index.py", pty=True)
