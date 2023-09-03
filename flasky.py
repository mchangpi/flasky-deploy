import os
import click
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User, Follow, Role, Permission, Post, Comment

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)

print("CONFIG ", os.getenv("FLASK_CONFIG") or "default")
print("DB_URI ", app.config["SQLALCHEMY_DATABASE_URI"])
print("MAIL_SERVER ", app.config["MAIL_SERVER"])
print("FLASKY_ADMIN ", app.config["FLASKY_ADMIN"])
# print("MAIL_PASSWORD", app.config["MAIL_PASSWORD"])


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Follow=Follow,
        Role=Role,
        Permission=Permission,
        Post=Post,
        Comment=Comment,
    )


@app.cli.command()
@click.argument("test_names", nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

    # create or update user roles
    Role.insert_roles()

    # ensure all users are following themselves
    User.add_self_follows()
