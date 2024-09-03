from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Membre(db.Model):
    __tablename__ = 'membres'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    date_naissance = db.Column(db.Date)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    statut_id = db.Column(db.Integer, db.ForeignKey('statuts.id'))
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)

    cotisations = db.relationship('Cotisation', backref='membre', lazy=True)
    participations = db.relationship('Participation', backref='membre', lazy=True)

    def __repr__(self):
        return f'<Membre {self.nom} {self.prenom}>'


class CategorieMembre(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    membres = db.relationship('Membre', backref='categorie', lazy=True)

    def __repr__(self):
        return f'<CategorieMembre {self.nom}>'


class Statut(db.Model):
    __tablename__ = 'statuts'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)

    membres = db.relationship('Membre', backref='statut', lazy=True)

    def __repr__(self):
        return f'<Statut {self.nom}>'


class Cotisation(db.Model):
    __tablename__ = 'cotisations'

    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    date_paiement = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)

    def __repr__(self):
        return f'<Cotisation {self.montant}€ pour Membre ID {self.membre_id}>'


class Evenement(db.Model):
    __tablename__ = 'evenements'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    lieu = db.Column(db.String(200), nullable=False)
    nb_participants_max = db.Column(db.Integer)
    est_recurrent = db.Column(db.Boolean, default=False)
    recurrence_details = db.Column(db.String(100))

    participations = db.relationship('Participation', backref='evenement', lazy=True)

    def __repr__(self):
        return f'<Evenement {self.nom} à {self.lieu}>'


class Participation(db.Model):
    __tablename__ = 'participations'

    id = db.Column(db.Integer, primary_key=True)
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=False)
    presence = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Participation Membre ID {self.membre_id} à l\'événement ID {self.evenement_id}>'


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    chemin_acces = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Document {self.nom} ({self.type})>'


class Don(db.Model):
    __tablename__ = 'dons'

    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    date_reception = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    donateur_id = db.Column(db.Integer, db.ForeignKey('donateurs.id'), nullable=False)

    def __repr__(self):
        return f'<Don {self.montant}€ par Donateur ID {self.donateur_id}>'


class Donateur(db.Model):
    __tablename__ = 'donateurs'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))

    dons = db.relationship('Don', backref='donateur', lazy=True)

    def __repr__(self):
        return f'<Donateur {self.nom} {self.prenom}>'
