from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from webapp import create_app, db
from webapp.models.product import ProductListing, PriceHistory


app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
        returns a dictionary that includes the database instance and the models in which
        the flask shell command will import these items automatically into the shell for user
        in flask terminal
    """

    # db.create_all()

    return dict(db=db, ProductListing=ProductListing, PriceHistory=PriceHistory)


if __name__ == '__main__':
    app.run()
