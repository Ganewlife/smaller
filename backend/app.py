from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from utils.logger import get_logger
from models import db  
from routes import main
from scheduler import scheduler


app = Flask(__name__)
app.config.from_object('config.Config')

# Initialiser le logger
logger = get_logger()

# Initialiser l'application Flask
db.init_app(app)
migrate = Migrate(app, db)

# Configuration du scheduler
# Démarrer le scheduler manuellement après avoir configuré l'application
scheduler.start()  # Lance le scheduler

# Enregistrer les blueprints
# app.register_blueprint(main)
app.register_blueprint(main, url_prefix='/api')

logger.info("Application Flask démarrée")

if __name__ == "__main__":
    app.run(debug=True)
