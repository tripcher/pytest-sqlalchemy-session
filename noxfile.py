import nox


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("sqlalchemy_version", ["1.4.48"])
@nox.parametrize("pytest_version", ["7"])
def tests(session: nox.Session, sqlalchemy_version: str, pytest_version: str):
    session.install("-r", "requirements/base.txt")
    session.install(f"sqlalchemy=={sqlalchemy_version}")
    session.install(f"pytest=={pytest_version}")
    session.install("-r", "requirements/test.txt")
    session.run("pytest")
