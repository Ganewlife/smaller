from flask import Flask, Blueprint, current_app, request, jsonify, make_response
from models import Membre, CategorieMembre, Statut, Admin, Donateur, Don, Cotisation, Evenement, Inscription, Participation, Projet, Tache, MembreTache, Budget, RapportFinancier, Document, ProcesVerbal
# from datetime import datetime
import os
import jwt
import datetime
from functools import wraps
from flask import send_from_directory, abort
from werkzeug.utils import secure_filename


# Chemin de base où les documents sont sauvegardés
UPLOAD_DIRECTORY = os.path.join(os.getcwd(), 'uploads')

main = Blueprint('main', __name__)

# Conversion de la chaîne date_naissance en objet Python date
def convertir_date(date_brut):
    date_str = date_brut
    if date_str:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()  # Conversion de la chaîne en objet date
    else:
        date = None
    return date
    
@main.route('/admins', methods=['POST'])
def create_admin():
    data = request.json
    
    username = data.get('username')
    if not username:
        return jsonify({"error": "Le nom d'utilisateur est requis"}), 400

    password = data.get('password')
    if not password:
        return jsonify({"error": "Le mot de passe est requis"}), 400
    
    admin = Admin.create(username=username, password=password)
    
    return jsonify({"message": "Admin créé", "admin_id": admin.id}), 201


# Fonction pour protéger les routes (décorateur)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt')  # Récupérer le token depuis le cookie

        if not token:
            return jsonify({'message': 'Token manquant!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_admin = Admin.query.get(data['admin_id'])
        except:
            return jsonify({'message': 'Token invalide!'}), 401

        return f(current_admin, *args, **kwargs)
    
    return decorated

# Route de connexion (login)
@main.route('/admin/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    # print(f"Login tenté par : {username}")  # Debugging

    # Rechercher l'admin
    admin = Admin.query.filter_by(username=username).first()
    # print(f"Admin trouvé : {admin}")  # Debugging   

    # Vérification des informations d'identification
    if not admin or not admin.check_password(password):
        # print(f"Mot de passe incorrect pour {username}")  # Debugging
        return jsonify({'message': 'Identifiants invalides!'}), 401

    # Générer un token JWT
    token = jwt.encode({
        'admin_id': admin.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    # Réponse avec le cookie sécurisé
    response = make_response(jsonify({'message': 'Connexion réussie!'}))
    response.set_cookie('jwt', token, httponly=True, secure=True, samesite='Lax', max_age=60*30)
    
    return response


@main.route('/admin/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'Déconnexion réussie!'}))
    response.delete_cookie('jwt')  # Supprimer le cookie JWT
    return response

# Lire les admins
@main.route('/admin/list', methods=['GET'])
def get_all_admins():
    admins = Admin.get_all()
    return jsonify([{
        "id": admin.id,
        "username": admin.username,
        "active": admin.active
    } for admin in admins])

# Route pour vérifier le dashboard (protégée)
@main.route('/admin/dashboard', methods=['GET'])
@token_required  # Utiliser le décorateur pour protéger cette route
def dashboard(current_admin):
    return jsonify({
        'message': f'Bienvenue sur le dashboard, Admin {current_admin.username}!',
        'admin_id': current_admin.id
    })


# Créer un membre
@main.route('/membres', methods=['POST'])
def create_membre():
    data = request.json
    
    categorie_id = data.get('categorie_id')
    if not categorie_id:
        return jsonify({"error": "categorie du membre est requis"}), 400
    
    statut_id = data.get('statut_id') or 1
    if not statut_id:
        return jsonify({"error": "statut du memebre est requis"}), 400
    
    # Conversion de la chaîne date_naissance en objet Python date
    date_naissance_str = data.get('date_naissance')
    # print(date_naissance_str);
    if date_naissance_str:
        date_naissance = datetime.datetime.strptime(date_naissance_str, '%Y-%m-%d').date()  # Conversion de la chaîne en objet date
    else:
        date_naissance = None  # Si aucune date n'est fournie
    
    membre = Membre.create(
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        telephone=data.get('telephone'),
        date_naissance=date_naissance,
        profil_photo=data.get('profil_photo'),
        categorie_id=categorie_id,
        statut_id=statut_id
    )
    return jsonify({"message": "Membre créé", "membre": membre.id}), 201

# Lire les membres
@main.route('/all_membres', methods=['GET'])
def get_all_membres():
    membres = Membre.get_all()
    return jsonify([{
        "id": membre.id,
        "nom": membre.nom,
        "prenom": membre.prenom,
        "email": membre.email,
        "telephone": membre.telephone,
        "categorie": membre.categorie_membre.nom if membre.categorie_membre else None,
        "statut": membre.statut_membre.nom if membre.statut_membre else None,
        "active": membre.active
    } for membre in membres])
    
# Lire un membre
@main.route('/membres/<int:membre_id>', methods=['GET'])
def get_membre(membre_id):
    membre = Membre.get_by_id(membre_id)
    if not membre:
        return jsonify({"message": "Membre non trouvé"}), 404
    return jsonify({
        "id": membre.id,
        "nom": membre.nom,
        "prenom": membre.prenom,
        "email": membre.email,
        "date_naissance": membre.date_naissance,
        "telephone": membre.telephone,
        "categorie_id": membre.categorie_id,
        "statut_id": membre.statut_id,
        "active": membre.active
    })

# Mettre à jour un membre
@main.route('/membres/<int:membre_id>', methods=['PUT'])
def update_membre(membre_id):
    membre = Membre.get_by_id(membre_id)
    if not membre:
        return jsonify({"message": "Membre non trouvé"}), 404

    data = request.json
    date_naissance_str = data.get('date_naissance')
    
    # Convertir la chaîne en objet date
    date_naissance = None
    if date_naissance_str:
        try:
            date_naissance = datetime.datetime.strptime(date_naissance_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Le format de la date est incorrect. Utilisez YYYY-MM-DD."}), 400
        
    categorie_id = data.get('categorie_id')
    if not categorie_id:
        return jsonify({"error": "categorie du membre est requis"}), 400
    
    statut_id = data.get('statut_id') or 1
    if not statut_id:
        return jsonify({"error": "statut du memebre est requis"}), 400
    
    membre.update(
        nom=data.get('nom'),
        prenom=data.get('prenom'),
        email=data.get('email'),
        telephone=data.get('telephone'),
        date_naissance=date_naissance,
        profil_photo=data.get('profil_photo'),
        categorie_id=categorie_id,
        statut_id=statut_id
    )
    return jsonify({"message": "Membre mis à jour"})

# Désactiver un membre
@main.route('/membres/<int:membre_id>', methods=['DELETE'])
def deactivate_membre(membre_id):
    membre = Membre.get_by_id(membre_id)
    if not membre:
        return jsonify({"message": "Membre non trouvé"}), 404

    membre.delete()
    return jsonify({"message": "Membre désactivé"})

# Réactiver un membre
@main.route('/membres/<int:membre_id>/reactivate', methods=['PUT'])
def reactivate_membre(membre_id):
    membre = Membre.get_by_id(membre_id)
    if not membre:
        return jsonify({"message": "Membre non trouvé"}), 404

    membre.reactivate()
    return jsonify({"message": "Membre réactivé"})


# Créer une catégorie de membre
@main.route('/categories', methods=['POST'])
def create_categorie():
    data = request.json
    categorie = CategorieMembre.create(
        nom=data['nom'],
        description=data.get('description')
    )
    return jsonify({"message": "Catégorie créée", "categorie": categorie.id})

# Lire les catégories de membre
@main.route('/allcategories', methods=['GET'])
def get_all_categories():
    categories = CategorieMembre.get_all()
    
    return jsonify([{
        "id": categorie.id,
        "nom": categorie.nom,
        "description": categorie.description,
        "active": categorie.active
    } for categorie in categories])
    
# Lire une catégorie de membre
@main.route('/categories/<int:categorie_id>', methods=['GET'])
def get_categorie(categorie_id):
    categorie = CategorieMembre.get_by_id(categorie_id)
    if not categorie:
        return jsonify({"message": "Catégorie non trouvée"}), 404
    return jsonify({
        "id": categorie.id,
        "nom": categorie.nom,
        "description": categorie.description,
        "active": categorie.active
    })

# Mettre à jour une catégorie de membre
@main.route('/categories/<int:categorie_id>', methods=['PUT'])
def update_categorie(categorie_id):
    categorie = CategorieMembre.get_by_id(categorie_id)
    if not categorie:
        return jsonify({"message": "Catégorie non trouvée"}), 404

    data = request.json
    categorie.update(
        nom=data.get('nom'),
        description=data.get('description')
    )
    return jsonify({"message": "Catégorie mise à jour"})

# Désactiver une catégorie de membre
@main.route('/categories/<int:categorie_id>', methods=['DELETE'])
def deactivate_categorie(categorie_id):
    categorie = CategorieMembre.get_by_id(categorie_id)
    if not categorie:
        return jsonify({"message": "Catégorie non trouvée"}), 404

    categorie.delete()
    return jsonify({"message": "Catégorie désactivée"})

# Réactiver une catégorie de membre
@main.route('/categories/<int:categorie_id>/reactivate', methods=['PUT'])
def reactivate_categorie(categorie_id):
    categorie = CategorieMembre.get_by_id(categorie_id)
    if not categorie:
        return jsonify({"message": "Catégorie non trouvée"}), 404

    categorie.reactivate()
    return jsonify({"message": "Catégorie réactivée"})

@main.route('/membres/<int:membre_id>/participations', methods=['GET'])
def get_participations(membre_id):
    try:
        participations = Membre.get_participations(membre_id)
        return jsonify(participations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Créer un statut
@main.route('/statuts', methods=['POST'])
def create_statut():
    data = request.json
    statut = Statut.create(
        nom=data['nom'],
    )
    return jsonify({"message": "Statut créée", "statut": statut.id})

# Lire les statuts de membre
@main.route('/allstatuts', methods=['GET'])
def get_all_statuts():
    statuts = Statut.get_all()
    
    return jsonify([{
        "id": statut.id,
        "nom": statut.nom,
        "active": statut.active
    } for statut in statuts])
    
# Lire un statut de membre
@main.route('/statuts/<int:statut_id>', methods=['GET'])
def get_statut(statut_id):
    statut = Statut.get_by_id(statut_id)
    if not statut:
        return jsonify({"message": "Statut non trouvée"}), 404
    return jsonify({
        "id": statut.id,
        "nom": statut.nom,
        "active": statut.active
    })

# Mettre à jour un statut de membre
@main.route('/statuts/<int:statut_id>', methods=['PUT'])
def update_statut(statut_id):
    statut = Statut.get_by_id(statut_id)
    if not statut:
        return jsonify({"message": "Statut non trouvée"}), 404

    data = request.json
    statut.update(
        nom=data.get('nom'),
    )
    return jsonify({"message": "Statut mise à jour"})

# Désactiver un statut de membre
@main.route('/statuts/<int:statut_id>', methods=['DELETE'])
def deactivate_statut(statut_id):
    statut = Statut.get_by_id(statut_id)
    if not statut:
        return jsonify({"message": "Statut non trouvée"}), 404

    statut.delete()
    return jsonify({"message": "Statut désactivée"})

# Réactiver une catégorie de membre
@main.route('/statuts/<int:statut_id>/statut', methods=['PUT'])
def reactivate_statut(statut_id):
    statut = Statut.get_by_id(statut_id)
    if not statut:
        return jsonify({"message": "Statut non trouvée"}), 404

    statut.reactivate()
    return jsonify({"message": "Statut réactivée"})

# Route pour créer un donateur
@main.route('donateurs', methods=['POST'])
def create_donateur():
    data = request.get_json()
    try:
        donateur = Donateur.create(
            nom=data.get('nom'),
            prenom=data.get('prenom'),
            email=data.get('email'),
            telephone=data.get('telephone')
        )
        return jsonify({"id": donateur.id, "message": "Donateur créé avec succès"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour récupérer tous les donateurs actifs
@main.route('donateurs', methods=['GET'])
def get_all_donateurs():
    donateurs = Donateur.get_all()
    return jsonify([{
        "id": donateur.id,
        "nom": donateur.nom,
        "prenom": donateur.prenom,
        "email": donateur.email,
        "telephone": donateur.telephone
    } for donateur in donateurs]), 200

# Route pour récupérer un donateur par ID
@main.route('donateurs/<int:donateur_id>', methods=['GET'])
def get_donateur(donateur_id):
    try:
        donateur = Donateur.get_by_id(donateur_id)
        return jsonify({
            "id": donateur.id,
            "nom": donateur.nom,
            "prenom": donateur.prenom,
            "email": donateur.email,
            "telephone": donateur.telephone
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

# Route pour mettre à jour un donateur
@main.route('donateurs/<int:donateur_id>', methods=['PUT'])
def update_donateur(donateur_id):
    data = request.get_json()
    try:
        donateur = Donateur.get_by_id(donateur_id)
        donateur.update(
            nom=data.get('nom'),
            prenom=data.get('prenom'),
            email=data.get('email'),
            telephone=data.get('telephone')
        )
        return jsonify({"message": "Donateur mis à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour désactiver un donateur
@main.route('donateurs/<int:donateur_id>', methods=['DELETE'])
def delete_donateur(donateur_id):
    try:
        donateur = Donateur.get_by_id(donateur_id)
        donateur.delete()
        return jsonify({"message": "Donateur désactivé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour réactiver un donateur
@main.route('donateurs/<int:donateur_id>/reactivate', methods=['PUT'])
def reactivate_donateur(donateur_id):
    try:
        donateur = Donateur.get_by_id(donateur_id)
        donateur.reactivate()
        return jsonify({"message": "Donateur réactivé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# Enregistré un don
@main.route('/dons', methods=['POST'])
def create_don():
    data = request.json
    don = Don.create(
        montant=data['montant'],
        date_transaction=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        donateur_id=data['donateur_id']
    )
    return jsonify({"message": "Don créé", "don": don.id}), 201

# MAJ don
@main.route('/dons/<int:don_id>', methods=['PUT'])
def update_don(don_id):
    don = Don.get_by_id(don_id)
    if not don:
        return jsonify({"message": "Don non trouvé"}), 404
    
    data = request.json
    don.update(
        montant=data['montant'],
        date_transaction=datetime.strptime(data['date'], '%Y-%m-%d').date()
    )
    return jsonify({"message": "Don mis à jour"})


# Permet de supprimer un don spécifique.
@main.route('/dons/<int:don_id>', methods=['DELETE'])
def delete_don(don_id):
    don = Don.get_by_id(don_id)
    if not don:
        return jsonify({"message": "Don non trouvée"}), 404
    
    don.delete()
    return jsonify({"message": "Don supprimé avec succès"}), 200


@main.route('/cotisations', methods=['POST'])
def create_cotisation():
    data = request.json
    date_cotisation = datetime.strptime(data['date'], '%Y-%m-%d').date()
    cotisation = Cotisation.create(
        montant=data['montant'],
        date_transaction=date_cotisation,
        membre_id=data['membre_id'],
        evenement_id=data['evenement_id'],
    )
    return jsonify({"message": "Cotisation créée", "cotisation_id": cotisation.id}), 201

# MAJ  d'une cotisation
@main.route('/cotisations/<int:cotisation_id>', methods=['PUT'])
def update_cotisation(cotisation_id):
    cotisation = Cotisation.get_by_id(cotisation_id)
    if not cotisation:
        return jsonify({"message": "Cotisation non trouvée"}), 404
    
    data = request.json
    date_cotisation = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    cotisation.update(
        montant=data['montant'],
        date_transaction=date_cotisation
    )
    return jsonify({"message": "Cotisation mise à jour"})

# Récupérer les détails d'une cotisation donnée par son ID
@main.route('/cotisations/<int:cotisation_id>', methods=['GET'])
def get_cotisation(cotisation_id):
    cotisation = Cotisation.get_by_id(cotisation_id)
    if not cotisation:
        return jsonify({"message": "Cotisation non trouvée"}), 404
    return jsonify({
        'id': cotisation.id,
        'montant': cotisation.montant,
        'date_paiement': cotisation.date_transaction.strftime('%Y-%m-%d'),
        'membre_id': cotisation.membre_id,
        'evenement_id': cotisation.evenement_id
    }), 200
    
# Lister toutes les cotisations
@main.route('/cotisations', methods=['GET'])
def list_cotisations():
    cotisations = Cotisation.get_all()
    return jsonify([{
        'id': cotisation.id,
        'montant': cotisation.montant,
        'date_paiement': cotisation.date_transaction.strftime('%Y-%m-%d'),
        'membre_id': cotisation.membre_id,
        'evenement_id': cotisation.evenement_id
    } for cotisation in cotisations]), 200

# Lister les cotisations d’un membre spécifique
@main.route('/cotisations/membre/<int:membre_id>', methods=['GET'])
def get_cotisations_by_membre(membre_id):
    cotisations = Cotisation.query.filter_by(membre_id=membre_id, active=True).all()
    if not cotisations:
        return jsonify({"message": "Aucune cotisation trouvée pour ce membre"}), 404

    return jsonify([{
        'id': cotisation.id,
        'montant': cotisation.montant,
        'date_paiement': cotisation.date_transaction.strftime('%Y-%m-%d'),
        'membre_id': cotisation.membre_id,
        'evenement_id': cotisation.evenement_id,
        'created_at': cotisation.created_at,
        'updated_at': cotisation.updated_at
    } for cotisation in cotisations]), 200
    
    
# Récupérer les cotisations d'un événement spécifique
@main.route('/evenements/<int:event_id>/cotisations', methods=['GET'])
def get_event_cotisations(event_id):
    cotisations = Cotisation.get_by_event(event_id)
    total = Cotisation.total_by_event(event_id)
    result = [
        {
            "id": cotisation.id,
            "membre": cotisation.membre_id,
            "montant": cotisation.montant,
            "date_paiement": cotisation.date_transaction,
            'updated_at': cotisation.updated_at
        } for cotisation in cotisations
    ]
    return jsonify({"total": total, "cotisations": result})


# Permet de supprimer une cotisation spécifique.
@main.route('/cotisations/<int:cotisation_id>', methods=['DELETE'])
def delete_cotisation(cotisation_id):
    cotisation = Cotisation.get_by_id(cotisation_id)
    if not cotisation:
        return jsonify({"message": "Cotisation non trouvée"}), 404
    
    cotisation.delete()
    return jsonify({"message": "Cotisation supprimée avec succès"}), 200


# Générer un reçu pour une cotisation
@main.route('/cotisations/<int:cotisation_id>/recu', methods=['GET'])
def generer_recu(cotisation_id):
    cotisation = Cotisation.get_by_id(cotisation_id)
    if not cotisation:
        return jsonify({"message": "Cotisation non trouvée"}), 404

    recu = cotisation.genererRecus()
    return jsonify({"recu": recu}), 200


# Route pour envoyer de notification de planififcation de de l'enevement 
@main.route('/evenements/<int:evenement_id>/notifications', methods=['POST'])
def envoyer_notifications(evenement_id):
    evenement = Evenement.query.get(evenement_id)

    if not evenement:
        return jsonify({'error': 'Événement non trouvé.'}), 404

    try:
        evenement.envoyer_notifications()
        return jsonify({'message': 'Notifications envoyées avec succès.'}), 200
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'envoi des notifications: {str(e)}'}), 500


# Route pour planifier un événement
@main.route('/evenements', methods=['POST'])
def planifier_evenement():
    data = request.json

    # Validation des données
    if not data.get('nom') or not data.get('date') or not data.get('lieu'):
        return jsonify({'error': 'Les champs nom, date et lieu sont obligatoires.'}), 400
    
    # Conversion de la chaîne date en objet Python date
    date = convertir_date(data['date'])
    print(data.get('est_recurrent'))
    # Création de l'événement
    evenement = Evenement.create(
        nom=data['nom'],
        date=date,
        lieu=data['lieu'],
        nb_participants_max=data.get('nb_participants_max', 100),
        est_recurrent=data.get('est_recurrent', False),
        recurrence_details=data.get('recurrence_details', None)
    )

    evenement.envoyer_notifications()  # Appel de la fonction pour envoyer les notifications

    return jsonify({'message': 'Événement planifié avec succès', 'evenement_id': evenement.id}), 201


# Route pour récupérer tous les evenements actifs
@main.route('evenements', methods=['GET'])
def get_all_evenements():
    evenements = Evenement.get_all()
    return jsonify([{
        "id": evenement.id,
        "nom": evenement.nom,
        "lieu": evenement.lieu,
        "nb_participants_max": evenement.nb_participants_max,
        "date": evenement.date,
        "recurrence_details": evenement.recurrence_details,
        "est_recurrent": evenement.est_recurrent
    } for evenement in evenements]), 200
    
    
# Routes pour recuperer un evenement specifique
@main.route('/evenements/<int:evenement_id>', methods=['GET'])
def get_evenement(evenement_id):
    """Route pour récupérer un événement par son ID."""
    evenement = Evenement.get_by_id(evenement_id)
    
    if not evenement:
        return jsonify({"message": "Événement non trouvé."}), 404

    # Préparer les données à retourner
    evenement_data = {
        "id": evenement.id,
        "nom": evenement.nom,
        "date": evenement.date.strftime('%Y-%m-%d'),
        "lieu": evenement.lieu,
        "nb_participants_max": evenement.nb_participants_max,
        "est_recurrent": evenement.est_recurrent,
        "recurrence_details": evenement.recurrence_details
    }

    return jsonify(evenement_data), 200


# Route pour mettre à jour un evenement
@main.route('/evenements/<int:evenement_id>', methods=['PUT'])
def update_evenement(evenement_id):
    """Route pour mettre à jour un événement existant."""
    evenement = Evenement.get_by_id(evenement_id)

    if not evenement:
        return jsonify({"message": "Événement non trouvé."}), 404

    data = request.json

    # Validation des champs obligatoires
    if not data.get('nom') or not data.get('date') or not data.get('lieu'):
        return jsonify({"error": "Les champs nom, date et lieu sont obligatoires."}), 400

    # Conversion de la chaîne date en objet Python Date
    date = convertir_date(data['date'])
    
    # Mise à jour des champs de l'événement
    evenement.update(
        nom=data['nom'],
        date=date,
        lieu=data['lieu'],
        nb_participants_max=data.get('nb_participants_max'),
        est_recurrent=data.get('est_recurrent', False),
        recurrence_details=data.get('recurrence_details')
    )

    return jsonify({"message": "Événement mis à jour avec succès."}), 200


# Permet de supprimer un evenement spécifique.
@main.route('/evenements/<int:evenement_id>', methods=['DELETE'])
def delete_evenement(evenement_id):
    evenement = Evenement.get_by_id(evenement_id)
    if not evenement:
        return jsonify({"message": "Evenement non trouvé"}), 404
    
    evenement.delete()
    return jsonify({"message": "Evenement supprimé avec succès"}), 200
    
    
@main.route('/evenements/<int:evenement_id>/recurrence', methods=['PUT'])
def definir_recurrence(evenement_id):
    data = request.json

    # Vérification de l'existence de l'événement
    evenement = Evenement.query.get(evenement_id)
    if not evenement:
        return jsonify({'error': 'Événement non trouvé.'}), 404

    # Validation des données
    type_recurrence = data.get('type_recurrence')
    jour_semaine = data.get('jour_semaine')
    jour_mois = data.get('jour_mois')
    
    if not type_recurrence:
        return jsonify({'error': 'Le type de récurrence est obligatoire.'}), 400
    
    try:
        evenement.definir_recurrence(type_recurrence, jour_semaine=jour_semaine, jour_mois=jour_mois)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Récurrence définie avec succès pour l\'événement.', 'evenement_id': evenement.id}), 200



@main.route('/evenements/<int:evenement_id>/augmenter_places', methods=['POST'])
def augmenter_places(evenement_id):
    """Route pour augmenter le nombre de places d'un événement."""
    data = request.json
    nombre_places = data.get('nombre_places')

    if not nombre_places or nombre_places <= 0:
        return jsonify({"message": "Nombre de places invalide."}), 400

    evenement = Evenement.get_by_id(evenement_id)

    if not evenement:
        return jsonify({"message": "Événement non trouvé."}), 404

    evenement.augmenter_places(nombre_places)
    return jsonify({"message": f"{nombre_places} places ajoutées à l'événement {evenement.nom}."}), 200


@main.route('/evenement/<int:evenement_id>/details', methods=['GET'])
def evenement_details(evenement_id):
    # Exemple d'une fonction pour obtenir les détails de l'événement
    evenement = Evenement.get_by_id(evenement_id)

    if not evenement:
        return jsonify({"error": "Événement non trouvé"}), 404

    # Convertir l'événement en dictionnaire ou en JSON
    evenement_data = {
        "id": evenement.id,
        "nom": evenement.nom,
        "description": evenement.description,
        # Ajoutez d'autres champs nécessaires ici
    }

    return jsonify(evenement_data), 200

# Recuperer les membres non sincrits à un evenemets
@main.route('/membres_non_inscrits', methods=['GET'])
def get_membres_non_inscrits():
    evenement_id = request.args.get('evenement_id')
    if not evenement_id:
        return jsonify({"error": "L'événement n'est pas spécifié."}), 400

    evenement = Evenement.get_by_id(evenement_id)
    if not evenement:
        return jsonify({"error": "L'événement spécifié n'existe pas."}), 404

    # Récupérer les membres qui ne sont pas inscrits à cet événement
    membres_inscrits_ids = [i.membre_id for i in Inscription.query.filter_by(active=True, envenement_id=evenement_id).all()]
    membres_disponibles = Membre.query.filter(~Membre.id.in_(membres_inscrits_ids)).all()

    return jsonify([{"id": membre.id, "nom": membre.nom, "fullname":membre.nom+" "+membre.prenom} for membre in membres_disponibles]), 200


# Recuperer lees inscriptions
@main.route('/inscriptions', methods=['GET'])
def get_inscriptions():
    evenement_id = request.args.get('evenement_id')
    if not evenement_id:
        return jsonify({"error": "L'ID de l'événement est requis"}), 400
    
    try:
        # Rechercher les inscriptions en fonction de l'ID de l'événement
        inscriptions = Inscription.query.filter_by(envenement_id=evenement_id,active=True).all()
        inscriptions_data = [{
            "id": inscription.id,
            "membre_id": inscription.membre_id,
            # "inscription_membre": inscription.inscription_membre,
            "en_liste_attente": inscription.en_liste_attente,
            "membre": {
                "id": inscription.membre.id,
                "fullname": inscription.membre.nom+" "+inscription.membre.prenom
            }
        } for inscription in inscriptions]

        return jsonify(inscriptions_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Route pour inscrire plusieurs membres à la fois
@main.route('/inscriptions/multiple', methods=['POST'])
def inscrire_multiple_membres():
    data = request.json
    evenement_id = data.get('evenement_id')
    membre_ids = data.get('membre_ids')

    if not evenement_id or not membre_ids:
        return jsonify({"error": "Les champs evenement_id et membre_ids sont requis."}), 400

    evenement = Evenement.get_by_id(evenement_id)
    print('evenement: ', evenement.id)
    if not evenement:
        # print('Événement non trouvé pour l\'ID:', evenement_id)
        return jsonify({"error": "L'événement spécifié n'existe pas."}), 404
    print('Événement trouvé:', evenement.id)
    try:
        for membre_id in membre_ids:
            Inscription.create(membre_id=membre_id, envenement_id=evenement_id)
        return jsonify({"message": "Membres inscrits avec succès."}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Route pour inscrire un seul membres à un evenement
@main.route('/inscriptions', methods=['POST'])
def create_inscription():
    data = request.json
    membre_id = data.get('membre_id')
    evenement_id = data.get('evenement_id')

    if not membre_id or not evenement_id:
        return jsonify({"error": "Les champs membre_id et evenement_id sont requis."}), 400

    try:
        # Utilisation de la méthode create de la classe Inscription
        inscription = Inscription.create(membre_id=membre_id, envenement_id=evenement_id)
        message = "Inscription réussie" if not inscription.en_liste_attente else "Inscription en liste d'attente"
        return jsonify({"message": message, "inscription_id": inscription.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    

@main.route('/inscriptions/<int:inscription_id>/valider', methods=['POST'])
def valider_inscription(inscription_id):
    """Route pour valider une inscription."""
    inscription = Inscription.query.get(inscription_id)

    if not inscription:
        return jsonify({"message": "Inscription non trouvée."}), 404

    try:
        inscription.valider_inscription()
        return jsonify({"message": "Inscription validée avec succès."}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    
    
@main.route('/inscriptions/<int:inscription_id>/ajouter_liste_attente', methods=['POST'])
def ajouter_liste_attente(inscription_id):
    """Route pour ajouter un membre à la liste d'attente."""
    inscription = Inscription.query.get(inscription_id)

    if not inscription:
        return jsonify({"message": "Inscription non trouvée."}), 404

    inscription.ajouter_liste_attente()
    return jsonify({"message": "Inscription ajoutée à la liste d'attente avec succès."}), 200


# Permet de supprimer un incription spécifique.
@main.route('/inscriptions/<int:inscription_id>', methods=['DELETE'])
def delete_inscription(inscription_id):
    inscription = Inscription.get_by_id(inscription_id)
    if not inscription:
        return jsonify({"message": "Inscription non trouvée"}), 404
    
    inscription.delete()
    return jsonify({"message": "Inscription supprimée avec succès"}), 200


@main.route('/participations', methods=['POST'])
def create_participation():
    data = request.json
    inscription_id = data.get('inscription_id')
    presence = data.get('presence', True)  # Par défaut, on considère la personne présente

    if not inscription_id:
        return jsonify({"error": "inscription_id est requis."}), 400

    participation = Participation.create(inscription_id=inscription_id, presence=presence)
    return jsonify({"message": "Participation créée", "participation_id": participation.id}), 201

@main.route('/participations/event/<int:event_id>', methods=['GET'])
def get_participations_by_event(event_id):
    participations = Participation.get_participations_by_event(event_id)
    return jsonify([{
        "id": p.id,
        "inscription_id": p.inscription_id,
        "inscription_membre": p.inscription_membre,
        "inscription_evenement": p.inscription_evenement,
        "presence": p.presence
    } for p in participations]), 200


@main.route('/evenements/<int:event_id>/participants', methods=['GET'])
def get_participants(event_id):
    # Utiliser la méthode du modèle pour récupérer les inscriptions validées
    participants = Inscription.get_validated_inscriptions(event_id, False)
    
    result = []
    for participant in participants:
        result.append({
            'id': participant.id,
            'nom': participant.membre.nom,
            'prenom': participant.membre.prenom,
            'email': participant.membre.email,
            'presence': participant.participations[0].presence if participant.participations else False
        })
    
    return jsonify(result)

@main.route('/evenements/<int:event_id>/participants/attente', methods=['GET'])
def get_participants_en_attente(event_id):
    # Utiliser la méthode du modèle pour récupérer les inscriptions en attente
    participants = Inscription.get_validated_inscriptions(event_id, True)
    
    result = []
    for participant in participants:
        result.append({
            'id': participant.id,
            'nom': participant.membre.nom,
            'prenom': participant.membre.prenom,
            'email': participant.membre.email,
            'presence': participant.participations[0].presence if participant.participations else False
        })
    
    return jsonify(result)

# Fais la présence de membre pour un evenement
@main.route('/evenements/<int:event_id>/participants/presence', methods=['POST'])
def marquer_presence(event_id):
    data = request.json
    inscription_ids = data.get('inscription_ids', [])

    if not inscription_ids:
        return jsonify({'error': 'Aucun participant sélectionné'}), 400

    # Appeler la méthode pour marquer la présence
    Participation.marquer_presence(inscription_ids)

    return jsonify({'message': 'Présence enregistrée avec succès'}), 200

# Liste des memebres présent à un evenement
@main.route('/evenements/<int:event_id>/membres-presents', methods=['GET'])
def get_membres_presents(event_id):
    # Appel de la méthode pour récupérer les membres présents à cet événement
    membres_presents = Evenement.get_membres_presents(event_id)
    
    return jsonify(membres_presents)

# creer un projet
@main.route('/projets', methods=['POST'])
def create_projet():
    data = request.json
    projet = Projet.create(
        nom=data['nom'],
        date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
        date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
        date_echeance=datetime.strptime(data.get('date_echeance'), '%Y-%m-%d').date() if data.get('date_echeance') else None,
        objectifs=data.get('objectifs')
    )
    return jsonify({"message": "Projet créé", "projet_id": projet.id}), 201


# créer une taches
@main.route('/taches', methods=['POST'])
def create_tache():
    data = request.json
    tache = Tache.create(
        nom=data['nom'],
        description=data.get('description'),
        date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
        date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
        projet_id=data['projet_id'],
        membre_assigne_id=data.get('membre_assigne_id')
    )
    return jsonify({"message": "Tâche créée", "tache_id": tache.id}), 201

# MAJ Tache
@main.route('/taches/<int:tache_id>', methods=['PUT'])
def update_tache(tache_id):
    tache = Tache.get_by_id(tache_id)
    if not tache:
        return jsonify({"message": "Tâche non trouvée"}), 404
    
    data = request.json
    tache.update(
        nom=data['nom'],
        description=data.get('description'),
        date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
        date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
        statut=data.get('statut', tache.statut),  # Si le statut est passé, sinon conserver l'actuel
    )
    return jsonify({"message": "Tâche mise à jour"})

# Assigner une tache à un memebre
@main.route('/taches/<int:tache_id>/assigner_membre', methods=['POST'])
def assigner_membre(tache_id):
    data = request.json
    membre_id = data['membre_id']
    
    # Assigner le membre à la tâche
    tache_membre = MembreTache.create(tache_id=tache_id, membre_id=membre_id)
    
    return jsonify({"message": "Membre assigné à la tâche"})


@main.route('/taches/<int:tache_id>', methods=['DELETE'])
def delete_tache(tache_id):
    tache = Tache.get_by_id(tache_id)
    if not tache:
        return jsonify({"message": "Tâche non trouvée"}), 404
    
    tache.delete() 
    return jsonify({"message": "Tâche supprimée"})


# Marquer une tâche comme complétée
@main.route('/taches/<int:tache_id>/complete', methods=['PUT'])
def complete_tache(tache_id):
    tache = Tache.get_by_id(tache_id)
    if not tache:
        return jsonify({"message": "Tâche non trouvée"}), 404
    
    tache.marquer_complete()
    return jsonify({"message": "Tâche marquée comme complétée"})


# Les tâches associées à un projet
@main.route('/projets/<int:projet_id>/taches', methods=['GET'])
def get_taches_projet(projet_id):
    projet = Projet.get_by_id(projet_id)
    result = []
    
    for tache in projet.taches:
        membres = [{'id': membre.id, 'nom': membre.nom, 'prenom': membre.prenom} for membre in tache.membres]
        result.append({
            'tache_id': tache.id,
            'nom': tache.nom,
            'description': tache.description,
            'date_debut': tache.date_debut.strftime('%Y-%m-%d'),
            'date_fin': tache.date_fin.strftime('%Y-%m-%d'),
            'statut': tache.statut,
            'updated_at': tache.updated_at.strftime('%Y-%m-%d'),
            'membres': membres
        })
    
    return jsonify(result)


# les tâches assignées à un membre
@main.route('/membres/<int:membre_id>/taches', methods=['GET'])
def get_taches_for_membre(membre_id):
    # Rechercher le membre par ID
    membre = Membre.query.get(membre_id)
    if not membre:
        return jsonify({"message": "Membre non trouvé"}), 404
    
    # Récupérer les tâches assignées à ce membre
    taches = []
    # for tache_membre in membre.membre_taches:
    for tache in membre.taches:
        # tache = tache_membre.tache
        taches.append({
            'id': tache.id,
            'nom': tache.nom,
            'description': tache.description,
            'date_debut': tache.date_debut.strftime('%Y-%m-%d'),
            'date_fin': tache.date_fin.strftime('%Y-%m-%d'),
            'projet': tache.projet_id,
            'statut': tache.statut,
            'updated_at': tache.updated_at.strftime('%Y-%m-%d')
        })
    
    return jsonify(taches), 200


# Suivre l’avancement d’un projet
@main.route('/projets/<int:projet_id>/avancement', methods=['GET'])
def suivre_avancement_projet(projet_id):
    projet = Projet.get_by_id(projet_id)
    if not projet:
        return jsonify({"message": "Projet non trouvé"}), 404
    
    avancement = projet.suivre_avancement()
    return jsonify({"avancement": avancement})

# MAJ projet
@main.route('/projets/<int:projet_id>', methods=['PUT'])
def update_projet(projet_id):
    projet = Projet.query.get(projet_id)
    if not projet:
        return jsonify({"message": "Projet non trouvé"}), 404
    
    data = request.json
    projet.update(
        nom=data['nom'],
        date_debut=datetime.strptime(data['date_debut'], '%Y-%m-%d').date(),
        date_fin=datetime.strptime(data['date_fin'], '%Y-%m-%d').date(),
        date_echeance=datetime.strptime(data.get('date_echeance'), '%Y-%m-%d').date() if data.get('date_echeance') else None,
        objectifs=data.get('objectifs')
    )
    return jsonify({"message": "Projet mis à jour"})

# Suppression d'un projet
@main.route('/projets/<int:projet_id>', methods=['DELETE'])
def delete_projet(projet_id):
    projet = Projet.get_by_id(projet_id)
    if not projet:
        return jsonify({"message": "Projet non trouvé"}), 404
    
    projet.delete()  # Assuming `BaseModel` has a delete method
    return jsonify({"message": "Projet supprimé"})


# créer un Budget
@main.route('/budgets', methods=['POST'])
def create_budget():
    data = request.json
    budget = Budget.create(
        annee=data['annee'],
        montant_prevu=data['montant_prevu'],
        montant_reel=data.get('montant_reel', 0.0)
    )
    return jsonify({"message": "Budget créé", "budget_id": budget.id}), 201


# comparer le montant prévu et le montant réel
@main.route('/budgets/<int:budget_id>/comparer', methods=['GET'])
def comparer_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    comparaison = budget.comparer_previsions_avec_reel()
    return jsonify({"comparaison": comparaison})


# créer un RapportFinancier
@main.route('/rapports', methods=['POST'])
def create_rapport():
    data = request.json
    rapport = RapportFinancier.create(
        annee=data['annee'],
        contenu=data.get('contenu', ''),
        budget_id=data['budget_id']
    )
    return jsonify({"message": "Rapport financier créé", "rapport_id": rapport.id}), 201


# générer un rapport financier
@main.route('/rapports/<int:rapport_id>/generer', methods=['GET'])
def generer_rapport(rapport_id):
    rapport = RapportFinancier.query.get_or_404(rapport_id)
    contenu_rapport = rapport.generer_rapport()
    return jsonify({"rapport": contenu_rapport})

# exporter un rapport financier
@main.route('/rapports/<int:rapport_id>/export', methods=['POST'])
def exporter_rapport(rapport_id):
    rapport = RapportFinancier.query.get_or_404(rapport_id)
    data = request.json
    format = data.get('format', 'pdf')
    try:
        rapport.exporter(format)
        return jsonify({"message": f"Rapport exporté en {format}"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# visualiser graphiquement les données d'un rapport financier
@main.route('/rapports/<int:rapport_id>/visualiser', methods=['GET'])
def visualiser_rapport(rapport_id):
    rapport = RapportFinancier.query.get_or_404(rapport_id)
    rapport.visualiser_graphiquement()
    return jsonify({"message": "Visualisation graphique générée."})


ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

def est_extension_autorisee(fichier):
    return '.' in fichier.filename and \
        fichier.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def taille_autorisee(fichier):
    # Vérification de la taille du fichier
    fichier.seek(0, os.SEEK_END)  # Aller à la fin du fichier pour vérifier la taille
    taille_fichier = fichier.tell()
    fichier.seek(0)  # Revenir au début
    return taille_fichier <= MAX_FILE_SIZE


# Téléverser et Sauvegarder un Document
@main.route('/upload', methods=['POST'])
def upload_document():
    if 'fichier' not in request.files:
        return jsonify({"message": "Aucun fichier fourni"}), 400
    
    fichier = request.files['fichier']
    
    if fichier.filename == '':
        return jsonify({"message": "Aucun fichier sélectionné"}), 400
    
    # Vérifier l'extension et la taille du fichier
    if not est_extension_autorisee(fichier):
        return jsonify({"message": "Extension de fichier non autorisée"}), 400
    
    if not taille_autorisee(fichier):
        return jsonify({"message": "Fichier trop volumineux"}), 400
    
    # Sauvegarder le document
    document = Document(
        type=request.form['type'],
        nom=fichier.filename
    )
    chemin_acces = document.sauvegarder_document(fichier)

    return jsonify({"message": "Document sauvegardé", "chemin_acces": chemin_acces}), 201


@main.route('/download/<int:document_id>', methods=['GET'])
def download_document(document_id):
    # Récupérer le document dans la base de données par son ID
    document = Document.query.get(document_id)
    if not document:
        return jsonify({"message": "Document non trouvé"}), 404

    # Vérifier que le fichier existe dans le répertoire
    if not os.path.exists(document.chemin_acces):
        return jsonify({"message": "Fichier introuvable sur le serveur"}), 404

    # Renvoie le fichier à partir du répertoire des uploads
    return send_from_directory(directory=UPLOAD_DIRECTORY, 
                               path=os.path.basename(document.chemin_acces),
                               as_attachment=True,
                               download_name=document.nom)
    
from flask import render_template, jsonify

@main.route('/documents', methods=['GET'])
def list_documents():
    # Récupérer tous les documents depuis la base de données
    documents = Document.query.all()

    # Générer la liste des documents sous forme d'une structure Python (dictionnaire)
    result = [
        {
            'id': doc.id,
            'nom': doc.nom,
            'type': doc.type,
            'date_creation': doc.date_creation,
            'chemin_acces': doc.chemin_acces
        } for doc in documents
    ]
    
    # Retourner une vue HTML avec les documents
    return render_template('documents_list.html', documents=result)

UPLOAD_FOLDER = 'uploads/documents'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}  # Extensions de fichier autorisées

# Fonction pour vérifier l'extension du fichier
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/proces_verbaux', methods=['POST'])
def create_proces_verbal():
    data = request.form  # On récupère les champs texte du formulaire
    fichier = request.files['document']  # On récupère le fichier téléversé

    if 'document' not in request.files or fichier.filename == '':
        return jsonify({'message': 'Aucun fichier sélectionné'}), 400

    if fichier and allowed_file(fichier.filename):
        # Sauvegarder le fichier avec un nom unique
        filename = secure_filename(fichier.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        fichier.save(filepath)

        # Créer le procès-verbal avec le chemin d'accès au document
        proces_verbal = ProcesVerbal.create(
            titre=data['titre'],
            date_reunion=datetime.strptime(data['date_reunion'], '%Y-%m-%d').date(),
            contenu=data['contenu'],
            chemin_acces_document=filepath  # Chemin vers le document téléversé
        )
        return jsonify({"message": "Procès-verbal créé", "proces_verbal_id": proces_verbal.id}), 201
    else:
        return jsonify({"message": "Format de fichier non autorisé"}), 400
    

# Télécharger un Document
@main.route('/proces_verbaux/<int:id>/telecharger', methods=['GET'])
def telecharger_document(id):
    proces_verbal = ProcesVerbal.query.get(id)
    if not proces_verbal or not proces_verbal.chemin_acces_document:
        return jsonify({"message": "Document non trouvé"}), 404

    # Envoyer le fichier depuis le dossier des téléversements
    directory = os.path.dirname(proces_verbal.chemin_acces_document)
    filename = os.path.basename(proces_verbal.chemin_acces_document)
    return send_from_directory(directory, filename, as_attachment=True)
