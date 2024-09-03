from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import db  # Importez vos modèles ici
from routes import main

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)
