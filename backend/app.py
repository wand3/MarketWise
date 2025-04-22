from datetime import datetime

from flask import Flask, request, jsonify
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


@app.route("/results", methods=["POST"])
def submit_results():
    results = request.json.get('data')
    search_text = request.json.get("search_text")

    for result in results:
        product_result = ProductListing(
            product_name=result['product_name'],
            url=result['product_url'],
            image=result["image_url"],
            current_price=result['product_price'],
            search_text=search_text,
            source=result['source'],
            currency=str(result['product_price'])[0],
            created_at=datetime.utcnow
        )
        db.session.add(product_result)

    db.session.commit()
    response = {'message': 'Received data successfully'}
    return jsonify(response), 200


@app.route('/all-results', methods=['GET'])
def get_results():
    results = db.ProductListing.query.all()
    product_results = []
    for result in results:
        product_results.append({
            'name': result.name,
            'url': result.url,
            'price': result.price,
            "img": result.img,
            'date': result.created_at,
            "created_at": result.created_at,
            "search_text": result.search_text,
            "source": result.source
        })

    return jsonify(product_results)
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
