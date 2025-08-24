from flask import Blueprint, jsonify, request
from ..models.product import ProductListing
from .. import create_app
import json
from pathlib import Path
from datetime import datetime
import logging
from . import main_bp


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])


@main_bp.route("/results", methods=["POST"])
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


@main_bp.route('/all-results', methods=['GET'])
def get_results():
    results = ProductListing.query.all()
    product_results = []
    # print(dir(results))

    for result in results:
        print(result)
        product_results.append({
            'product_name': result.product_name,
            'url': result.url,
            'product_price': result.current_price,
            "img": result.image,
            'date': result.created_at,
            "created_at": result.created_at,
            "search_text": result.search_text,
            "source": result.source
        })

    return jsonify(product_results)
