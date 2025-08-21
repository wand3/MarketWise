from flask import Blueprint, jsonify, request
from ..models.product import ProductListing
from .. import create_app
import json
from pathlib import Path
from datetime import datetime
import logging
from . import api_bp


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])


# Create a blueprint for data loading routes
# data_bp = Blueprint('data', __name__, url_prefix='/api/data')


@api_bp.route('/load-products', methods=['POST'])
def load_products():
    """
    Load products from scraper JSON file into database
    Optional JSON payload: {
        "file_path": "custom/path/to/file.json",
        "clear_after_load": true
    }
    """
    try:
        # Get parameters from request or use defaults
        data = request.get_json() or {}
        file_path = data.get('file_path', 'backend/scraper/result.json')
        clear_after_load = data.get('clear_after_load', True)

        # Convert to Path object
        json_path = Path(file_path)

        if not json_path.exists():
            return jsonify({
                "success": False,
                "message": f"JSON file not found: {json_path}"
            }), 404

        # Read products from JSON file
        with open(json_path, 'r') as f:
            products = json.load(f)

        if not products:
            return jsonify({
                "success": True,
                "message": "No products found in JSON file",
                "loaded_count": 0
            })

        # Process and load products
        loaded_count = 0
        for product in products:
            # Check if product already exists
            existing = Product.query.filter_by(
                product_url=product.get("product_url")
            ).first()

            if not existing:
                # Clean price data
                price_str = product.get("product_price", "0")
                try:
                    price = float(price_str.replace('$', '').replace(',', ''))
                except (ValueError, TypeError):
                    price = 0.0

                # Create new product
                new_product = ProductListing(
                    product_name=product_data.get("product_name", "Unknown")[:255],
                    image=product_data.get("image_url", "")[:255],
                    source=product_data.get("source", "unknown"),
                    url=product_data.get("product_url", "")[:500],
                    current_price=price_value,
                    currency=currency,
                    search_text=product_data.get("search_term", "")[:255],
                    created_at=datetime.utcnow()
                )

                db.session.add(new_product)
                loaded_count += 1

        # Commit to database
        db.session.commit()

        # Clear JSON file if requested
        if clear_after_load:
            with open(json_path, 'w') as f:
                json.dump([], f)

        return jsonify({
            "success": True,
            "message": f"Successfully loaded {loaded_count} products",
            "loaded_count": loaded_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error loading products: {str(e)}"
        }), 500
