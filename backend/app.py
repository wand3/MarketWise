from flask import Flask
from flask_cors import CORS
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from product import Base, ProductListing, PriceHistory

# create and configure the app
app = Flask(__name__, instance_relative_config=True)

app.config.from_object(Config)
db = SQLAlchemy(model_class=Base)
db.init_app(app)
CORS(app)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


@app.shell_context_processor
def make_shell_context():
    """
        returns a dictionary that includes the database instance and the models in which
        the flask shell command will import these items automatically into the shell for user
        in flask terminal
    """

    # db.create_all()

    return dict(ProductListing=ProductListing, PriceHistory=PriceHistory)


if __name__ == '__main__':
    app.run()
