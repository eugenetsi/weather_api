# config.py

# setting up the connection the db
# marshmallow for JSON serialization
# sqlalchemy for db interaction

import pathlib
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# set current directory to find db
basedir = pathlib.Path(__file__).parent.resolve()
connex_app = connexion.App(__name__, specification_dir=basedir)

# sqlalchemy init
app = connex_app.app
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{basedir/'meteo.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # not event-driven

db = SQLAlchemy(app)
ma = Marshmallow(app)
