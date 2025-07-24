from flask import Flask
from flask_migrate import Migrate
from .db import db
from .models import *  # This imports your models
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    Migrate(app, db)

    return app
