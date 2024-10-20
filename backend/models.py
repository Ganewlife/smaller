import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, Column, Integer, String
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

db = SQLAlchemy()

# BaseModel avec les champs created_at et updated_at (à faire heriter par le reste de class)
class BaseModel(db.Model):
    __abstract__ = True # Indique que cette classe ne sera pas directement utilisée pour créer des tables
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    # Methode pour creer
    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj

    # Methode pour faire update
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.utcnow()  # Met à jour la date de modification
        db.session.commit()
        
    # Méthode pour récupérer un enregistrement par ID
    @classmethod
    def get_by_id(cls, record_id):
        # return cls.query.get(record_id)
        return cls.query.get_or_404(record_id)

    # Méthode pour récupérer tous les enregistrements actifs
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(active=True).all()

    # Méthode générique de suppression
    def delete(self):
        self.active = False
        db.session.commit()
        
    # Fonction pour réactiver un membre désactivé
    def reactivate(self):
        self.active = True
        db.session.commit()
        
class Transaction(BaseModel):
    __abstract__ = True
    montant = db.Column(db.Float, nullable=False)
    date_transaction = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def valider(self) -> bool:
        """Valider la transaction."""
        # Logique de validation générique à définir
        return self.montant > 0  # Exemple de validation de base


# Classe Admin héritant de BaseModel
class Admin(BaseModel):
    __tablename__ = 'admins'
    
    # id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    @classmethod
    def create(cls, username, password):
        """Créer un nouvel admin avec un mot de passe haché."""
        admin = cls(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        return admin


    def set_password(self, password):
        """Hacher le mot de passe."""
        self.password_hash = generate_password_hash(password)
        # print(f"Mot de passe haché : {self.password_hash}")  # Debugging

    def check_password(self, password):
        """Vérifier si le mot de passe est correct."""
        result = check_password_hash(self.password_hash, password)
        # print(f"Vérification du mot de passe : {result}")  # Debugging
        return result

    def __repr__(self):
        return f'Admin {self.username}'
    

class Membre(BaseModel):
    __tablename__ = 'membres'
    
    # id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    date_naissance = db.Column(db.Date)
    profil_photo = db.Column(db.String(200))
    # active = db.Column(db.Boolean, default=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Clé étrangère
    statut_id = db.Column(db.Integer, db.ForeignKey('statuts.id'), nullable=True)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, default = 1)
    
    # Relation
    categorie_membre = db.relationship('CategorieMembre', backref='membre', lazy=True)
    statut_membre = db.relationship('Statut', backref='membre', lazy=True)
    inscriptions = db.relationship('Inscription', backref='membre', lazy=True)
    cotisations = db.relationship('Cotisation', backref='membre', lazy=True)
    
    # Relation many-to-many avec Tache via MembreTache
    taches = db.relationship('Tache', secondary='membre_taches', backref=db.backref('membres_associes', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Membre {self.nom} {self.prenom}>'


    @classmethod
    def get_participations(cls, membre_id):
        """Récupère toutes les participations d'un membre donné où la présence est marquée"""
        membre = cls.query.get(membre_id)
        
        # Utilisation de la compréhension de liste pour filtrer les participations présentes
        participations = [
            {
                'evenement': participation.inscription.evenement.nom,
                'date_evenement': participation.inscription.evenement.date,
                'lieu': participation.inscription.evenement.lieu,
                'presence': participation.presence
            }
            for inscription in membre.inscriptions
            for participation in inscription.participations
            if participation.presence  # Ne garder que ceux où la présence est True
        ]
        
        return participations

    # Fonction Create
    """ @classmethod
    def create(cls, nom, prenom, email, telephone, date_naissance, profil_photo, categorie_id,statut_id):
        membre = cls(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            date_naissance=date_naissance,
            profil_photo=profil_photo,
            categorie_id=categorie_id ,
            statut_id=statut_id
        )
        db.session.add(membre)
        db.session.commit()
        return membre """

    """ # Fonction Read
    @classmethod
    def get_by_id(cls, membre_id):
        return cls.query.filter_by(id=membre_id, active=True).first()

    @classmethod
    def get_all(cls):
        return cls.query.filter_by(active=True).all() """

    # Fonction Update
    """ def update(self, nom=None, prenom=None, email=None, telephone=None, date_naissance=None, profil_photo=None):
        if nom:
            self.nom = nom
        if prenom:
            self.prenom = prenom
        if email:
            self.email = email
        if telephone:
            self.telephone = telephone
        if date_naissance:
            self.date_naissance = date_naissance
        if profil_photo:
            self.profil_photo = profil_photo
        db.session.commit() """

    """ # Fonction Delete (désactivation)
    def deactivate(self):
        self.active = False
        db.session.commit() """

    # Fonction pour la gestion de la photo de profil
    def update_profile_photo(self, photo_path):
        # Suppression de l'ancienne photo si nécessaire
        if self.profil_photo and os.path.exists(self.profil_photo):
            os.remove(self.profil_photo)
        self.profil_photo = photo_path
        db.session.commit()

    """ # Fonction pour réactiver un membre désactivé
    def reactivate(self):
        self.active = True
        db.session.commit() """


class CategorieMembre(BaseModel):
    __tablename__ = 'categories'

    # id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    # active = db.Column(db.Boolean, default=True)
    
    # Relation vers Membre
    membres = db.relationship('Membre', backref='categorie', lazy=True)

    def __repr__(self):
        return f'<CategorieMembre {self.nom}>'

    # Fonction Create
    """ @classmethod
    def create(cls, nom, description):
        categorie = cls(
            nom=nom,
            description=description
        )
        db.session.add(categorie)
        db.session.commit()
        return categorie """

    """ # Fonction Read
    @classmethod
    def get_by_id(cls, categorie_id):
        return cls.query.filter_by(id=categorie_id, active=True).first()

    @classmethod
    def get_all(cls):
        return cls.query.filter_by(active=True).all() """

    # Fonction Update
    """ def update(self, nom=None, description=None):
        if nom:
            self.nom = nom
        if description:
            self.description = description
        db.session.commit() """

    """ # Fonction Delete (désactivation)
    def deactivate(self):
        self.active = False
        db.session.commit()

    # Fonction pour réactiver une catégorie désactivée
    def reactivate(self):
        self.active = True
        db.session.commit() """



class Statut(BaseModel):
    __tablename__ = 'statuts'

    # id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    # active = db.Column(db.Boolean, default=True)

    # Relation avec Membre
    membres = db.relationship('Membre', backref='statut', lazy=True)
    def __repr__(self):
        return f'<Statut {self.nom}>'
    
    """ @classmethod
    def create(cls, nom):
        statut = cls(nom=nom)
        db.session.add(statut)
        db.session.commit()
        return statut """
    
    """ # Fonction Read statut
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(active=True).all()
    
    # Fonction Read a statut
    @classmethod
    def get_by_id(cls, statut_id):
        return cls.query.filter_by(id=statut_id, active=True).first() """

    """ # Fonction Update
    def update(self, nom=None):
        if nom:
            self.nom = nom
        db.session.commit() """

    """ # Fonction Delete (désactivation)
    def deactivate(self):
        self.active = False
        db.session.commit()

    # Fonction pour réactiver une catégorie désactivée
    def reactivate(self):
        self.active = True
        db.session.commit() """


class HistoriqueStatut(BaseModel):
    __tablename__ = 'historique_statuts'

    # Clés primaires et étrangères
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    statut_id = db.Column(db.Integer, db.ForeignKey('statuts.id'), nullable=False)
    
    # Autres colonnes
    date_changement = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    motif = db.Column(db.String(255), nullable=True)

    # Relations
    membre = db.relationship('Membre', backref=db.backref('historique_statuts', lazy=True))
    statut = db.relationship('Statut', backref=db.backref('historique_statuts', lazy=True))

    def enregistrer_changement(self, membre_id, statut_id, motif=None):
        """Enregistre un changement de statut pour un membre."""
        historique = HistoriqueStatut(
            membre_id=membre_id,
            statut_id=statut_id,
            motif=motif
        )
        db.session.add(historique)
        db.session.commit()

    def __repr__(self):
        return f'<HistoriqueStatut Membre ID {self.membre_id}, Statut ID {self.statut_id}>'
    # Exemple d'enregistrement d'un changement de statut pour un membre
    # historique_statut = HistoriqueStatut()
    # historique_statut.enregistrer_changement(membre_id=1, statut_id=3, motif="Changement après renouvellement de cotisation")


class Evenement(BaseModel):
    __tablename__ = 'evenements'

    # id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    lieu = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=True,)
    nb_participants_max = db.Column(db.Integer)
    est_recurrent = db.Column(db.Boolean, default=False)
    recurrence_details = db.Column(db.String(100))

    # participations = db.relationship('Participation', backref='evenement', lazy=True)
    inscriptions = db.relationship('Inscription', backref='evenement', lazy=True)

    def __repr__(self):
        return f'<Evenement {self.nom} à {self.lieu}>'
    
    """ @classmethod
    def create(cls, **kwargs):
        # Appel direct à la méthode create de BaseModel
        return super().create(**kwargs) """
    
    @classmethod
    def planifier_evenement(cls, nom, date, lieu, nb_participants_max=100, est_recurrent=False, recurrence_details=None):
        """Utilise la méthode 'create' de BaseModel pour planifier un événement"""
        evenement = cls.create(
            nom=nom,
            date=date,
            lieu=lieu,
            nb_participants_max=nb_participants_max,
            est_recurrent=est_recurrent,
            recurrence_details=recurrence_details
        )

        # Envoyer des notifications après la création de l'événement
        evenement.envoyer_notifications()

        return evenement
    
    def definir_recurrence(self, type_recurrence, intervalle=None, jour_semaine=None, jour_mois=None):
        """Définir la récurrence d'un événement"""
        self.est_recurrent = True
        
        # Gestion des différents types de récurrence
        if type_recurrence == 'quotidienne':
            if intervalle and intervalle >1:
                self.recurrence_details = f"Récurrence quotidienne tous les {intervalle} jours"
            else:
                self.recurrence_details = f"Récurrence quotidienne tous les jours"
                
        elif type_recurrence == 'hebdomadaire':
            self.recurrence_details = f"Récurrence hebdomadaire, chaque {jour_semaine or 'lundi'} de semaine"
        elif type_recurrence == 'mensuelle':
            self.recurrence_details = f"Récurrence mensuelle le {jour_mois or '1er'} jour de chaque mois"
        elif type_recurrence == 'annuelle':
            self.recurrence_details = f"Récurrence annuelle tous les {intervalle or 1} ans le {self.date.strftime('%d %B')}"
        else:
            raise ValueError("Type de récurrence non supporté")

        # Sauvegarder les changements dans la base de données
        db.session.commit()

        print(f"Récurrence définie: {self.recurrence_details}")

    def envoyer_notifications(self):
        """Envoyer des notifications aux participants"""
        print(f"Notifications envoyées pour l'événement '{self.nom}' planifié le {self.date} à {self.lieu}.")
        
    # Vérifier si des places sont disponibles
    def places_disponibles(self):
        inscriptions_validees = Inscription.query.filter_by(envenement_id=self.id, en_liste_attente=False).count()
        return self.nb_participants_max > inscriptions_validees
    
    def augmenter_places(self, nombre_places):
        """Augmente le nombre de places disponibles pour cet événement."""
        self.nb_participants_max += nombre_places
        db.session.commit()
    
    cotisations = db.relationship('Cotisation', backref='evenement', lazy=True)

    # Liste des membres présent à un evenement
    @classmethod
    def get_membres_presents(cls, evenement_id):
        """Récupère tous les membres présents à un événement donné en utilisant une jointure"""
        
        # Requête avec jointure entre les tables Evenement, Inscription, Participation et Membre
        membres_presents = db.session.query(Membre.nom, Membre.prenom, Membre.email).\
            join(Inscription, Inscription.membre_id == Membre.id).\
            join(Participation, Participation.inscription_id == Inscription.id).\
            join(Evenement, Inscription.envenement_id == Evenement.id).\
            filter(Evenement.id == evenement_id, Participation.presence == True).all()

        # Retourner la liste des membres présents
        return [{'nom': nom, 'prenom': prenom, 'email': email} for nom, prenom, email in membres_presents]
    

    """ @classmethod
    def get_membres_presents(cls, evenement_id):
        # Récupère tous les membres présents à un événement donné
        evenement = cls.query.get(evenement_id)
        
        # Filtrer les inscriptions validées et récupérer les participations où la présence est marquée
        membres_presents = [
            {
                'membre_id': participation.inscription.membre.id,
                'nom': participation.inscription.membre.nom,
                'prenom': participation.inscription.membre.prenom,
                'email': participation.inscription.membre.email
            }
            for inscription in evenement.inscriptions
            for participation in inscription.participations
            if participation.presence  # Ne garder que les membres marqués comme présents
        ]
        
        return membres_presents """
    
    """ @classmethod
    def create(cls, nom, date, lieu, nb_participants_max=100, est_recurrent=False, recurrence_details=None):
        evenement = cls(nom=nom, date=date, lieu=lieu, nb_participants_max=nb_participants_max, est_recurrent=est_recurrent, recurrence_details=recurrence_details)
        db.session.add(evenement)
        db.session.commit()
        return evenement

    # Fonction Update
    def update(self, nom=None, date=None, lieu=None, nb_participants_max=None, est_recurrent=None, recurrence_details=None):
        if nom:
            self.nom = nom
        if date:
            self.prenom = date
        if nb_participants_max:
            self.nb_participants_max = nb_participants_max
        if lieu:
            self.lieu = lieu
        if est_recurrent:
            self.est_recurrent = est_recurrent
        if recurrence_details:
            self.recurrence_details = recurrence_details
        db.session.commit() """
        
class Inscription(BaseModel):
    __tablename__ = 'inscriptions'
    en_liste_attente = db.Column(db.Boolean, default=True)
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    envenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=False)
    
    # Relation
    inscription_membre = db.relationship('Membre', backref='membre', lazy=True)
    inscription_evenement = db.relationship('Evenement', backref='membre', lazy=True)
    # participations = db.relationship('Participation', backref='inscription', lazy=True)
    
    def __repr__(self):
        return f"<Inscription Membre {self.membre_id} pour l'événement {self.envenement_id}>"
    

    @classmethod
    def create(cls, **kwargs):
        """Surcharge de la méthode create de BaseModel pour gérer la validation des inscriptions."""
        # Obtenir l'événement lié à cette inscription
        evenement = Evenement.query.get(kwargs.get('envenement_id'))

        if evenement is None:
            raise ValueError("L'événement spécifié intern n'existe pas.")

        # Vérification des places disponibles
        if evenement.places_disponibles():
            kwargs['en_liste_attente'] = False
        else:
            kwargs['en_liste_attente'] = True

        # Appel à la méthode create de BaseModel
        return super().create(**kwargs)
    
    # Méthode pour valider une inscription
    def valider_inscription(self):
        """Valider l'inscription du membre à un événement."""
        evenement = Evenement.query.get(self.envenement_id)

        if evenement.places_disponibles():
            self.en_liste_attente = False
            db.session.commit()
        else:
            raise ValueError("Nombre maximum de participants atteint, inscription en liste d'attente.")

    # Méthode pour ajouter le membre à la liste d'attente
    def ajouter_liste_attente(self):
        """Mettre l'inscription en liste d'attente."""
        self.en_liste_attente = True
        db.session.commit()
        
    # Liste des inscription pour un evenement
    @classmethod
    def get_validated_inscriptions(cls, evenement_id, statut):
        """Récupère toutes les inscriptions validées (non en liste d'attente) pour un événement donné."""
        return cls.query.filter_by(envenement_id=evenement_id, en_liste_attente=statut).all()

        
class Participation(BaseModel):
    __tablename__ = 'participations'

    # membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    # evenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=False)
    
    presence = db.Column(db.Boolean, default=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscriptions.id'), nullable=False)

    # Relation avec l'inscription
    # Permettant d'accéder à toutes les participations associées via l'attribut participations. Cela crée une relation bidirectionnelle depuis un objet de la classe Inscription.
    inscription = db.relationship('Inscription', backref='participations', lazy=True)
    
    def __repr__(self):
        return f'<Participation Membre ID {self.membre_id} à l\'événement ID {self.evenement_id}>'
    
    @classmethod
    def get_participations_by_event(cls, event_id):
        """Récupérer toutes les participations pour un événement spécifique via son inscription."""
        return cls.query.join(Inscription).filter(Inscription.envenement_id == event_id, Inscription.active==True).all()

    @classmethod
    def get_participations_by_member(cls, membre_id):
        """Récupérer toutes les participations d'un membre via ses inscriptions."""
        return cls.query.join(Inscription).filter(Inscription.membre_id == membre_id, Inscription.active==True).all()
    

    @classmethod
    def marquer_presence(cls, inscription_ids):
        """Méthode pour marquer la présence pour plusieurs inscriptions."""
        participations = cls.query.filter(cls.inscription_id.in_(inscription_ids)).all()
        for participation in participations:
            participation.presence = True
        db.session.commit()
        return participations

    """ @classmethod
    def create(cls, inscription_id, presence=True):
        participation = cls(
            inscription_id=inscription_id,
            presence=presence
        )
        db.session.add(participation)
        db.session.commit()
        return participation
    
    # Méthode update
    def update(self, presence=None):
        if presence is not None:
            self.presence = presence
        self.updated_at = datetime.utcnow()
        db.session.commit() """

class Cotisation(Transaction):
    __tablename__ = 'cotisations'

    # montant = db.Column(db.Float, nullable=False)
    # date_paiement = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=False) 

    def __repr__(self):
        return f'<Cotisation {self.montant} FCFA pour l\'événement ID {self.evenement_id}, Membre ID {self.membre_id}>'

    def generer_recu(self) -> str:
        """Générer un reçu pour la cotisation."""
        return f"Reçu de cotisation pour l'événement {self.evenement_id}, membre {self.membre_id}, montant de {self.montant} FCFA."

    # les cotisations par événement 
    @classmethod
    def get_by_event(cls, event_id):
        """Récupérer toutes les cotisations liées à un événement spécifique."""
        return cls.query.filter_by(evenement_id=event_id, active=True).all()
    
    # Calculer le montant total des cotisations pour un événement 
    @classmethod
    def total_by_event(cls, event_id):
        """Calculer le montant total des cotisations pour un événement."""
        total = db.session.query(db.func.sum(cls.montant)).filter_by(evenement_id=event_id, active=True).scalar()
        return total or 0 

        
class Don(BaseModel):
    __tablename__ = 'dons'

    # id = db.Column(db.Integer, primary_key=True)
    # montant = db.Column(db.Float, nullable=False)
    # date_reception = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    donateur_id = db.Column(db.Integer, db.ForeignKey('donateurs.id'), nullable=False)

    def __repr__(self):
        return f'<Don {self.montant}FCFA par Donateur ID {self.donateur_id}>'
    
    def genererRemerciement(self) -> None:
        """Générer un message de remerciement pour le don."""
        print(f"Merci au donateur {self.donateur_id} pour un don de {self.montant} euros.")


class Donateur(BaseModel):
    __tablename__ = 'donateurs'

    # id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))

    dons = db.relationship('Don', backref='donateur', lazy=True)

    def __repr__(self):
        return f'<Donateur {self.nom} {self.prenom}>'


class Tache(BaseModel):
    __tablename__ = 'taches'

    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(50), default="Non commencée")  # Statut initial
    
    # Clef etrangère
    projet_id = db.Column(db.Integer, db.ForeignKey('projets.id'), nullable=False)

    # Relation many-to-many avec Membre via MembreTache
    membres = db.relationship('Membre', secondary='membre_taches', backref=db.backref('taches_assignes', lazy='dynamic'))
    
    def marquer_complete(self):
        self.statut = "Complétée"
        db.session.commit()

    """ def reassigner(self, membre_id):
        self.membre_assigne_id = membre_id
        db.session.commit() """

    def __repr__(self):
        return f'<Tache {self.nom} pour le projet ID {self.projet_id}>'

class MembreTache(BaseModel):
    __tablename__ = 'membre_taches'
    
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), primary_key=True)
    tache_id = db.Column(db.Integer, db.ForeignKey('taches.id'), primary_key=True)
    role = db.Column(db.String(100), nullable=False) 
    date_assignation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations pour les jointures
    membre = db.relationship('Membre', backref=db.backref('taches_associees', lazy=True))
    taches = db.relationship('Tache', backref=db.backref('membres_taches', lazy=True))

    def __repr__(self):
        return f'<MembreTache Membre ID {self.membre_id} associé à Tache ID {self.tache_id}>'


class Projet(BaseModel):
    __tablename__ = 'projets'

    nom = db.Column(db.String(100), nullable=False)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    date_echeance = db.Column(db.Date, nullable=True)
    objectifs = db.Column(db.String(255), nullable=True)
    
    # Relation avec les tâches
    taches = db.relationship('Tache', backref='projet', lazy=True)

    def suivre_avancement(self):
        """Calculer l'avancement basé sur le statut des tâches"""
        taches_total = len(self.taches)
        taches_completees = len([tache for tache in self.taches if tache.statut == "Complétée"])
        
        if taches_total > 0:
            return (taches_completees / taches_total) * 100  # Avancement en pourcentage
        return 0

    def __repr__(self):
        return f'<Projet {self.nom}>'

class Budget(BaseModel):
    __tablename__ = 'budgets'
    
    annee = db.Column(db.Integer, nullable=False)
    montant_prevu = db.Column(db.Float, nullable=False)
    montant_reel = db.Column(db.Float, nullable=True, default=0.0)

    # Relation avec RapportFinancier
    rapports = db.relationship('RapportFinancier', backref='budget', lazy=True)

    def comparer_previsions_avec_reel(self) -> str:
        """Compare le montant prévu avec le montant réel."""
        difference = self.montant_reel - self.montant_prevu
        if difference > 0:
            return f"Le budget réel dépasse les prévisions de {difference} euros."
        elif difference < 0:
            return f"Le budget réel est inférieur aux prévisions de {-difference} euros."
        else:
            return "Le budget réel correspond exactement aux prévisions."

    def __repr__(self):
        return f'<Budget {self.annee} - Prévu: {self.montant_prevu}, Réel: {self.montant_reel}>'

class RapportFinancier(BaseModel):
    __tablename__ = 'rapports_financiers'

    annee = db.Column(db.Integer, nullable=False)
    contenu = db.Column(db.Text, nullable=True)
    
    # Foreign Key vers Budget
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)

    def generer_rapport(self) -> str:
        """Génère un rapport basé sur les données du budget."""
        rapport = f"Rapport financier pour l'année {self.annee}:\n"
        rapport += f"Montant prévu: {self.budget.montant_prevu} euros\n"
        rapport += f"Montant réel: {self.budget.montant_reel} euros\n"
        rapport += self.contenu if self.contenu else "Aucun contenu supplémentaire."
        return rapport

    def exporter(self, format: str):
        """Exporte le rapport dans un format donné (par exemple, PDF, CSV)."""
        if format == "pdf":
            # Logique pour exporter en PDF (à implémenter)
            print(f"Export du rapport en PDF pour {self.annee}")
        elif format == "csv":
            # Logique pour exporter en CSV (à implémenter)
            print(f"Export du rapport en CSV pour {self.annee}")
        else:
            raise ValueError(f"Format {format} non supporté")

    def visualiser_graphiquement(self):
        """Affiche une visualisation graphique des données financières."""
        # Ici, vous pouvez utiliser une bibliothèque comme Matplotlib pour visualiser les données.
        print(f"Affichage des données financières pour l'année {self.annee} sous forme de graphique.")

    def __repr__(self):
        return f'<RapportFinancier {self.annee}>'


class Document(BaseModel):
    __tablename__ = 'documents'

    type = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    chemin_acces = db.Column(db.String(500), nullable=False)

    def sauvegarder_document(self, fichier):
        """Sauvegarder le fichier sur le serveur avec un nom unique"""
        # Générer un nom de fichier unique avec l'extension correcte
        extension = os.path.splitext(fichier.filename)[1]
        nom_fichier_unique = secure_filename(f"{uuid.uuid4()}{extension}")

        # Définir le chemin complet où enregistrer le fichier
        chemin_acces = os.path.join('uploads/', nom_fichier_unique)
        fichier.save(chemin_acces)

        # Mettre à jour le chemin d'accès dans la base de données
        self.chemin_acces = chemin_acces
        db.session.commit()

        return chemin_acces

    def __repr__(self):
        return f'<Document {self.nom} sauvegardé à {self.chemin_acces}>'

class ProcesVerbal(BaseModel):
    __tablename__ = 'proces_verbaux'

    titre = db.Column(db.String(200), nullable=False)
    date_reunion = db.Column(db.Date, nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    chemin_acces_document = db.Column(db.String(200), nullable=True)  # Chemin vers le document téléversé

    def __repr__(self):
        return f'<ProcesVerbal {self.titre} - {self.date_reunion}>'

    @classmethod
    def rechercher_par_date(cls, date):
        return cls.query.filter_by(date_reunion=date).all()

    @classmethod
    def rechercher_par_mot_cle(cls, mot_cle):
        return cls.query.filter(or_(cls.titre.ilike(f'%{mot_cle}%'), cls.contenu.ilike(f'%{mot_cle}%'))).all()
