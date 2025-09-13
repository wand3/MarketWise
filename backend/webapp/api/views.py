from flask import Blueprint, jsonify, request
from ..models.product import ProductListing
from .. import create_app, db
import json
from pathlib import Path
from datetime import datetime
import logging
from . import api_bp


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])


@api_bp.route('/load-products', methods=['POST'])
def load_products():
    """
    Load products from scraper JSON file into database
    Optional JSON payload: {
        "file_path": "custom/path/to/file.json",
        "clear_after_load": true
    }
    """
    logging.info('load products in')
    try:
        # Get parameters from request or use defaults
        # Handle different content types
        if request.content_type == 'application/json':
            data = request.get_json() or {}
        elif request.content_type.startswith('multipart/form-data'):
            data = request.form.to_dict()
        elif request.content_type.startswith('application/x-www-form-urlencoded'):
            data = request.form.to_dict()
        else:
            # Try to parse as JSON anyway for backward compatibility
            try:
                data = request.get_json(force=True) or {}
            except:
                data = {}

        result_folder = Path(__file__).resolve().parent.parent.parent
        result_file = result_folder / 'scraper' / 'result.json'

        file_path = data.get('file_path', result_file)
        logging.info(f'result file found {result_file}')

        # logging.info(f'file found {file_path}')

        clear_after_load = data.get('clear_after_load', True)
        logging.info(f'clear after load found  {clear_after_load}')

        # Convert to Path object
        json_path = Path(file_path)
        logging.info(f'json file found {json_path}')

        if not json_path.exists():
            return jsonify({
                "success": False,
                "message": f"JSON file not found: {json_path}"
            }), 404

        # Read products from JSON file
        with open(json_path, 'r') as f:
            products = json.load(f)

        # logging.info(f'products loaded {products}')

        if not products:
            return jsonify({
                "success": True,
                "message": "No products found in JSON file",
                "loaded_count": 0
            }), 400

        # Process and load products
        loaded_count = 0
        for product in products:
            logging.info(f'Product in {product} ---------')

            # Check if ProductListing already exists
            existing = None
            try:
                existing = db.session.query(ProductListing).filter_by(
                    url=product.get("product_url", "")
                ).first()
            except Exception as e:
                print(e)
                existing = False

            logging.info(f'Existing product to {existing}')

            logging.info(f'each product {product}')

            if not existing:
                # Clean price data
                price_str = product.get("product_price", "0")
                try:
                    price = float(price_str.replace('$', '').replace(',', ''))
                except (ValueError, TypeError):
                    price = 0.0

                logging.info(f'Not existing in')
                try:
                    # Create new product
                    new_product = ProductListing(
                        product_name=product.get("product_name", "Unknown")[:255],
                        image=product.get("image_url", "")[:255],
                        source=product.get("source", "unknown"),
                        url=product.get("product_url", "")[:500],
                        current_price=price,
                        currency=product.get("product_price")[0],
                        search_text=product.get("search_term", "")[:255],
                        created_at=datetime.utcnow()
                    )

                    db.session.add(new_product)
                    loaded_count += 1
                except Exception as e:
                    logging.info(f'Error adding file {e}')
                    db.session.rollback()
                    return jsonify({
                        "success": False,
                        "message": f"Failed to add product {loaded_count}",
                        "loaded_count": loaded_count
                    })

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
