from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route('/api/membres', methods=['GET'])
def get_membres():
    # Exemple de réponse JSON
    return jsonify({"membres": ["Membre1", "Membre2"]})
