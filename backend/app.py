from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from models import Base
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(model_class=Base)
# initialize
db.init_app(app)
CORS(app)


@app.shell_context_processor
def make_shell_context():
    """
        returns a dictionary that includes the database instance and the models in which
        the flask shell command will import these items automatically into the shell for user
        in flask terminal
    """

    from models.product import Product, ProductListing, Platform, PriceHistory
    # db.create_all()

    return dict(Product=Product, ProductListing=ProductListing, Platform=Platform, PriceHistory=PriceHistory)


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run()
