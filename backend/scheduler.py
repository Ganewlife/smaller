# from app import app
from flask_apscheduler import APScheduler
from datetime import datetime
from models import db, Tache
# import logging
from utils.logger import get_logger
# Initialiser le logger pour routes
logger = get_logger()
scheduler = APScheduler()  # Créez le scheduler ici
        
def update_task_status():
    from app import app
    with app.app_context():  # Assurez-vous de disposer du bon contexte d'application
        # print("Tentative de changement de statut de tâche pour retard.")
        # logger.info("Tentative de changement de statut de tâche pour retard.")
        now = datetime.now()
        # Définir le début de la journée actuelle (minuit)
        # today_midnight = datetime.combine(now.date(), datetime.min.time())
        today = now.date()
        tasks = Tache.query.filter(
            Tache.statut.in_(["EN_COURS", "A_FAIRE", "EN_ATTENTE"]),
            Tache.date_fin < today
        ).all()
        if len(tasks) > 0:
            print(f"TAches {tasks}")
            for task in tasks:
                # logger.info("Tentative de changement de statut de tâche pour retard.")
                task.changer_statut('EN_RETARD')
            db.session.commit()

# Ajouter la tâche planifiée
scheduler.add_job(
    id='update_task_status',
    func=update_task_status,
    trigger='interval',
    minutes=1
)

# Démarrer le scheduler
# scheduler.start()

""" scheduler.add_job(
    my_task,  # La fonction à exécuter
    CronTrigger(
        minute='0',  # Exécuter à 0 minutes
        hour='12',   # Exécuter à 12 heures
        day='*',     # Tous les jours du mois
        month='*',   # Tous les mois
        day_of_week='*'  # Tous les jours de la semaine
    ),
    id='my_cron_job'
) """