import logging
import json
import os
from logging.handlers import RotatingFileHandler

# Création du dossier pour les logs
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs')
os.makedirs(LOG_DIR, exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom formatter for logging in JSON format."""
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage()
        }
        # Utiliser une gestion correcte des caractères spéciaux
        return json.dumps(log_entry, ensure_ascii=False)

def get_logger():
    """Configure logging for the entire application with JSON format."""
    # Logger principal
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)

    # Création du formatter JSON personnalisé
    formatter = JSONFormatter()

    # Fichier pour les logs généraux (info.json)
    info_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'info.json'), maxBytes=5_000_000, backupCount=5, encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Fichier pour les logs d'erreurs (error.json)
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'error.json'), maxBytes=5_000_000, backupCount=5, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Console pour les avertissements et erreurs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # Ajout des handlers au logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger
