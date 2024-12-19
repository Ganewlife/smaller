document.addEventListener('DOMContentLoaded', () => {
    // const $ = require('jquery');

    
    // Définir l'URL de l'API
    const API_URL = 'http://localhost:5000/api';


    // Fonction pour afficher une notification Bootstrap
    function showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        notification.classList.remove('d-none');
        setTimeout(() => notification.classList.add('d-none'), 3000);
    }


    const regex = /^(?:(5|6|9)\d{7}|4[0-7]\d{6})$/;
    function validatePhoneNumber(phoneNumber) {
        return regex.test(phoneNumber);
    }

    /* toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": false,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    } */

    // Fonction pour afficher les notifications
    /* function showNotification(message, duration = 3000, type = 'success') {
        if (type === 'success') {
            toastr.success(message);
        } else if (type === 'error') {
            toastr.error(message);
        }

        setTimeout(() => {
            toastr.clear();
        }, duration);
    } */
    // Gestion administrateur
    const loginForm = document.getElementById('login-form');
    const createAdminForm = document.getElementById('create-admin-form');
    const changePasswordForm = document.getElementById('change-password-form');
    
    // Gestion des catégories
    const categorieForm = document.getElementById('categorie-form');
    const categorieList = document.getElementById('categorie-list');
    const categorieNom = document.getElementById('categorie-nom');
    const categorieDescription = document.getElementById('categorie-description');
    const categorieId = document.getElementById('categorie-id');
    
    // Gestion des statuts
    const statutForm = document.getElementById('statut-form');
    const statutList = document.getElementById('statut-list');
    const statutNom = document.getElementById('statut-nom');
    const statutId = document.getElementById('statut-id');

    // Gestion des membres
    const membreForm = document.getElementById('membre-form');
    const membreList = document.getElementById('membre-list');
    const membreNom = document.getElementById('membre-nom');
    const membrePrenom = document.getElementById('membre-prenom');
    const membreEmail = document.getElementById('membre-email');
    const membreTelephone = document.getElementById('membre-telephone');
    const membreDateNaissance = document.getElementById('membre-date-naissance');
    const membreCategorie = document.getElementById('membre-categorie');
    const membreStatut = document.getElementById('membre-statut');
    const membreId = document.getElementById('membre-id');

    // Connexion Admin
    loginForm.onsubmit = function(event) {
        event.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        fetch(`${API_URL}/admin/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })
        .then(response => {
            if (!response.ok) throw new Error('Identifiants invalides');
            return response.json();
        })
        .then(data => {
            showNotification('Connexion réussie !', 'success');
            loadAdminList();
        })
        .catch(error => {
            showNotification(error.message, 'danger');
        });
    };

    // Création d'un nouvel Admin
    createAdminForm.onsubmit = function(event) {
        event.preventDefault();
        const username = document.getElementById('admin-username').value;
        const password = document.getElementById('admin-password').value;

        fetch(`${API_URL}/admins`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })
        .then(response => {
            if (!response.ok) throw new Error('Erreur lors de la création');
            return response.json();
        })
        .then(() => {
            showNotification('Admin créé avec succès !', 'success');
            createAdminForm.reset();
            loadAdminList();
        })
        .catch(error => {
            showNotification(error.message, 'danger');
        });
    };

    // Modifier le mot de passe d'un Admin
    changePasswordForm.onsubmit = function(event) {
        event.preventDefault();
        const newPassword = document.getElementById('new-password').value;

        fetch(`${API_URL}/admin/change_password`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: newPassword })
        })
        .then(response => {
            if (!response.ok) throw new Error('Erreur lors du changement de mot de passe');
            return response.json();
        })
        .then(() => {
            showNotification('Mot de passe modifié avec succès !', 'success');
            changePasswordForm.reset();
        })
        .catch(error => {
            showNotification(error.message, 'danger');
        });
    };

    // Charger la liste des administrateurs
    function loadAdminList() {
        return fetch(`${API_URL}/admin/list`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const adminList = document.getElementById('admin-list');
            adminList.innerHTML = '';  // Vider la liste avant de la recharger

            data.forEach(admin => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = `${admin.username} (ID: ${admin.id})`;
                adminList.appendChild(li);
            });
        })
        .catch(error => {
            showNotification('Erreur lors du chargement de la liste des admins', 'danger');
        });
    }


    // Charger les catégories dans la liste
    function loadCategoriesList() {
        return fetch(`${API_URL}/allcategories`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Données reçues:', data);  // Ajoutez cette ligne pour inspecter la réponse
                categorieList.innerHTML = '';
    
                // Vérification de la structure des données
                const categories = data.categories || data;  // Si 'data.categories' est indéfini, utiliser 'data' directement
    
                if (Array.isArray(categories)) {
                    categories.forEach(categorie => {
                        let li = document.createElement('li');
                        li.textContent = `${categorie.nom} (${categorie.description})`;
                        let updateBtn = document.createElement('button');
                        updateBtn.textContent = 'Modifier';
                        updateBtn.onclick = () => loadCategorieForUpdate(categorie.id);
                        let deleteBtn = document.createElement('button');
                        deleteBtn.textContent = 'Désactiver';
                        deleteBtn.onclick = () => deactivateCategorie(categorie.id);
                        li.appendChild(updateBtn);
                        li.appendChild(deleteBtn);
                        categorieList.appendChild(li);
                    });
                } else {
                    console.error('Les données des catégories ne sont pas valides.');
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement des catégories:', error);
            });
    }

    // Charger les catégories pour la liste déroulante
    function loadCategories() {
        return fetch(`${API_URL}/allcategories`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                membreCategorie.innerHTML = '';
                const categories = data.categories || data;
                if (Array.isArray(categories)) {
                    categories.forEach(categorie => {
                        let option = document.createElement('option');
                        option.value = categorie.id;
                        option.textContent = categorie.nom;
                        membreCategorie.appendChild(option);
                    });
                } else {
                    throw new Error('Les données des catégories ne sont pas valides.');
                }
            })
            .catch(error => {
                showNotification(`Erreur lors du chargement des catégories : ${error.message}`, 'error');
                console.error(error);
            });
    }
    
    // Charger les statut dans la liste
    function loadStatutsList() {
        return fetch(`${API_URL}/allstatuts`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Données reçues:', data);  // Ajoutez cette ligne pour inspecter la réponse
                statutList.innerHTML = '';
                
                // Vérification de la structure des données
                const statuts = data.statuts || data;  // Si 'data.statuts' est indéfini, utiliser 'data' directement
    
                if (Array.isArray(statuts)) {
                    statuts.forEach(statut => {
                        let li = document.createElement('li');
                        li.textContent = `${statut.nom}`;
                        let updateBtn = document.createElement('button');
                        updateBtn.textContent = 'Modifier';
                        updateBtn.onclick = () => loadStatutForUpdate(statut.id);
                        let deleteBtn = document.createElement('button');
                        deleteBtn.textContent = 'Désactiver';
                        deleteBtn.onclick = () => deactivateStatut(statut.id);
                        li.appendChild(updateBtn);
                        li.appendChild(deleteBtn);
                        statutList.appendChild(li);
                    });
                } else {
                    console.error('Les données des statut ne sont pas valides.');
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement des catégories:', error);
            });
    }
    
    // Charger les statuts pour la liste déroulante
    function loadStatuts() {
        return fetch(`${API_URL}/allstatuts`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                membreStatut.innerHTML = '';
                const statuts = data.statuts || data;
                if (Array.isArray(statuts)) {
                    statuts.forEach(statut => {
                        let option = document.createElement('option');
                        option.value = statut.id;
                        option.textContent = statut.nom;
                        membreStatut.appendChild(option);
                    });
                } else {
                    throw new Error('Les données des statuts ne sont pas valides.');
                }
            })
            .catch(error => {
                showNotification(`Erreur lors du chargement des statuts : ${error.message}`, 'error');
                console.error(error);
            });
    }

    // Charger les membres
    function loadMembres() {
        fetch(`${API_URL}/all_membres`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                membreList.innerHTML = '';
                const membres = data.membres || data;
                
                if (Array.isArray(membres)) {
                    membres.forEach(membre => {
                        let li = document.createElement('li');
                        li.textContent = `${membre.nom} ${membre.prenom} (${membre.email}) ${membre.telephone}`;
                        let updateBtn = document.createElement('button');
                        updateBtn.textContent = 'Modifier';
                        updateBtn.onclick = () => loadMembreForUpdate(membre.id);
                        let deleteBtn = document.createElement('button');
                        deleteBtn.textContent = 'Désactiver';
                        deleteBtn.onclick = () => deactivateMembre(membre.id);
                        li.appendChild(updateBtn);
                        li.appendChild(deleteBtn);
                        membreList.appendChild(li);
                    });
                } else {
                    showNotification('Les données des membres ne sont pas valides.', 'error');
                }
            })
            .catch(error => {
                showNotification(`Erreur lors du chargement des membres : ${error.message}`, 'error');
                console.error(error);
            });
    }

    // Ajouter ou mettre à jour une catégorie
    categorieForm.onsubmit = function (event) {
        event.preventDefault();
        const method = categorieId.value ? 'PUT' : 'POST';
        const url = categorieId.value ? `${API_URL}/categories/${categorieId.value}` : `${API_URL}/categories`;
        const data = {
            nom: categorieNom.value,
            description: categorieDescription.value
        };
        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => response.json())
            .then(() => {
                categorieForm.reset();
                categorieId.value = '';
                loadCategoriesList();
                showNotification("Catégorie ajoutée avec succès !");
            })
            .catch(error => {
                showNotification(`Erreur lors de l'enregistrement de la catégorie : ${error.message}`, 'error');
                console.error(error);
            });
    };
    
    // Ajouter ou mettre à jour un statut
    statutForm.onsubmit = function (event) {
        event.preventDefault();
        const method = statutId.value ? 'PUT' : 'POST';
        const url = statutId.value ? `${API_URL}/statuts/${statutId.value}` : `${API_URL}/statuts`;
        const data = {
            nom: statutNom.value,
        };
        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => response.json())
            .then(() => {
                statutForm.reset();
                statutId.value = '';
                loadStatutsList();
                showNotification("Statut ajouté avec succès !");
            })
            .catch(error => {
                showNotification(`Erreur lors de l'enregistrement du statut : ${error.message}`, 'error');
                console.error(error);
            });
    };

    // Charger les informations de la catégorie à modifier
    function loadCategorieForUpdate(id) {
        fetch(`${API_URL}/categories/${id}`)
            .then(response => response.json())
            .then(categorie => {
                categorieId.value = categorie.id;
                categorieNom.value = categorie.nom;
                categorieDescription.value = categorie.description;
            });
    }

    // Désactiver une catégorie
    function deactivateCategorie(id) {
        fetch(`${API_URL}/categories/${id}`, { method: 'DELETE' })
            .then(() => loadCategoriesList())
            .catch(error => {
                showNotification(`Erreur lors de la désactivation de la catégorie : ${error.message}`, 'error');
                console.error(error);
            });
    }
    
    // Charger les informations de statut à modifier
    function loadStatutForUpdate(id) {
        fetch(`${API_URL}/statuts/${id}`)
            .then(response => response.json())
            .then(statut => {
                statutId.value = statut.id;
                statutNom.value = statut.nom;
            });
    }

    // Désactiver un statut
    function deactivateStatut(id) {
        fetch(`${API_URL}/statuts/${id}`, { method: 'DELETE' })
            .then(() => loadStatutsList())
            .catch(error => {
                showNotification(`Erreur lors de la désactivation du statut : ${error.message}`, 'error');
                console.error(error);
            });
    }

    // Ajouter ou mettre à jour un membre
    membreForm.onsubmit = function (event) {
        event.preventDefault();

        // Validation des champs obligatoires
        if (!membreNom.value || !membrePrenom.value || !membreDateNaissance.value || !membreTelephone.value || !membreEmail.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/) || !membreCategorie.value || !membreStatut.value) {
            showNotification("Veuillez remplir tous les champs obligatoires avec des informations valides !", 'error');
            return;
        }
    
        if (!validatePhoneNumber(membreTelephone)) {
            showNotification("Veuillez fournir un numéro de téléphone valide !", 'error');
            return;
        }


        const method = membreId.value ? 'PUT' : 'POST';
        const url = membreId.value ? `${API_URL}/membres/${membreId.value}` : `${API_URL}/membres`;

        const data = {
            nom: membreNom.value,
            prenom: membrePrenom.value,
            email: membreEmail.value,
            date_naissance: membreDateNaissance.value,
            telephone: membreTelephone.value || null,
            categorie_id: membreCategorie.value,
            statut_id: membreStatut.value || null
        };

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur lors de l'enregistrement du membre. Statut : ${response.status}`);
            }
            return response.json();
        })
        .then(() => {
            membreForm.reset();
            membreId.value = '';
            loadMembres();
            showNotification("Membre enregistré avec succès !");
        })
        .catch(error => {
            showNotification(`Erreur lors de l'enregistrement du membre : ${error.message}`, 'error');
            console.error(error);
        });
    };

    // Charger les informations du membre à modifier
    function loadMembreForUpdate(id) {
        fetch(`${API_URL}/membres/${id}`)
            .then(response => response.json())
            .then(membre => {
                console.log('id categorie ; ',membre.date_naissance);
                Promise.all([loadCategories(), loadStatuts()]).then(() => {
                    membreId.value = membre.id;
                    membreNom.value = membre.nom;
                    membrePrenom.value = membre.prenom;
                    membreEmail.value = membre.email;
                    membreTelephone.value = membre.telephone;
                    membreCategorie.value = membre.categorie_id;
                    membreStatut.value = membre.statut_id;
                    // membreDateNaissance.value = membre.date_naissance.toLocaleDateString();
                    if (membre.date_naissance) {
                        const parsedDate = new Date(Date.parse(membre.date_naissance));
                        const formattedDate = parsedDate.toISOString().split('T')[0]; // Formater en YYYY-MM-DD
                        membreDateNaissance.value = formattedDate;
                    } else {
                        membreDateNaissance.value = ''; // Si la date est vide
                    }
                });
            })
            .catch(error => {
                showNotification(`Erreur lors du chargement du membre : ${error.message}`, 'error');
                console.error(error);
            });
    }

    // Désactiver un membre
    function deactivateMembre(id) {
        fetch(`${API_URL}/membres/${id}`, { method: 'DELETE' })
            .then(() => loadMembres())
            .catch(error => {
                showNotification(`Erreur lors de la désactivation du membre : ${error.message}`, 'error');
                console.error(error);
            });
    }


    
    // Charger les admins, catégories, statuts et membres au démarrage
    // loadAdminList();
    // loadCategories();
    // loadStatuts();
    // loadCategoriesList();
    // loadStatutsList();
    // loadMembres();
    // loadProcesVerbaux();
});
