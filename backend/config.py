import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'ff77d5462390b9149a7f29d6858712a245101b4b0cc2ba5cbf7130d09a0aae68'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'assopilot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration pour Flask-APScheduler
    SCHEDULER_API_ENABLED = True  # Permettre l'accès API au scheduler (optionnel)