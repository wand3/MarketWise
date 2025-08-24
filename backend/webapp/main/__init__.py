from flask import Blueprint

main_bp = Blueprint('/', __name__)

from webapp.main import views
