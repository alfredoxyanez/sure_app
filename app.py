from flask.cli import FlaskGroup
from server.api.index import create_app
from server.api.helpers import db_seed
from server.api.db import db

cli = FlaskGroup(create_app())


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db_seed(db)
    db.session.commit()


if __name__ == "__main__":
    cli()
