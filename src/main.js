const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');
let detailWindow; // Variable pour stocker la fenêtre des détails
let detailProjetWindow;

function createWindow() {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;
    const win = new BrowserWindow({
        width: width,
        height: height,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: false, // Active le contexte isolé
            nodeIntegration: true, // Désactive nodeIntegration pour la sécurité
        },
    });

    win.loadFile('src/index.html');
}

// Fonction pour créer la fenêtre de détails evenement
function createDetailWindow(eventId) {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;
    if (detailWindow) {
        // detailWindow.focus();
        detailWindow.on('closed', () => {
            // Une fois la fenêtre fermée, créez une nouvelle fenêtre
            detailWindow = new BrowserWindow({
                width: width,
                height: height,
                webPreferences: {
                    preload: path.join(__dirname, 'preload.js'),
                    contextIsolation: true, // Assurez-vous que c'est activé
                    nodeIntegration: false, // Toujours désactiver pour la sécurité
                },
            });
            detailWindow.loadFile('src/evenement_details.html'); // Assurez-vous que ce fichier existe
            detailWindow.on('closed', () => {
                detailWindow = null;
            });

            // Passer l'ID de l'événement à la nouvelle fenêtre des détails evenement
            detailWindow.webContents.on('did-finish-load', () => {
                detailWindow.webContents.send('load-event-details', eventId);
            });
        });

        // Fermer la fenêtre existante
        detailWindow.close();
    } else {
        detailWindow = new BrowserWindow({
            width: width,
            height: height,
            webPreferences: {
                preload: path.join(__dirname, 'preload.js'),
                contextIsolation: true, // Assurez-vous que c'est activé
                nodeIntegration: false, // Toujours désactiver pour la sécurité
            },
        });
        detailWindow.loadFile('src/evenement_details.html'); // Assurez-vous que ce fichier existe
        detailWindow.on('closed', () => {
            detailWindow = null;
        });

        // Passer l'ID de l'événement à la fenêtre des détails
        detailWindow.webContents.on('did-finish-load', () => {
            detailWindow.webContents.send('load-event-details', eventId);
        });
    }
}

let currentEventId = null;

// Écouter l'événement envoyé depuis renderer.js
ipcMain.on('open-event-details', (event, eventId) => {
    // console.log(`ID de evenement reçu dans le processus principal : ${eventId}`);
    currentEventId = eventId; // Stocker l'ID de l'événement
    createDetailWindow(eventId);
});

// Gérer la demande pour récupérer l'ID de l'événement
ipcMain.handle('get-event-id', () => {
    // console.log(`ID de evenenement renvoye : ${currentEventId}`);
    return currentEventId; // Retourner l'ID stocké
});

// Fonction pour créer la fenêtre de détails projet
function createDetailProjetWindow(projetId) {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;
    if (detailProjetWindow) {
        detailProjetWindow.on('closed', () => {
            // Une fois la fenêtre fermée, créez une nouvelle fenêtre
            detailProjetWindow = new BrowserWindow({
                width: width, // Largeur de l'écran
                height: height,
                webPreferences: {
                    preload: path.join(__dirname, 'preload.js'),
                    contextIsolation: true, // Assurez-vous que c'est activé
                    nodeIntegration: false, // Toujours désactiver pour la sécurité
                },
            });
            detailProjetWindow.loadFile('src/taches.html'); // Assurez-vous que ce fichier existe
            detailProjetWindow.on('closed', () => {
                detailProjetWindow = null;
            });

            // Passer l'ID du projet à la nouvelle fenêtre des détails
            detailProjetWindow.webContents.on('did-finish-load', () => {
                detailProjetWindow.webContents.send('load-projet-details', projetId);
            });
        });

        // Fermer la fenêtre existante
        detailProjetWindow.close();
    } else {
        detailProjetWindow = new BrowserWindow({
            width: width, // Largeur de l'écran
            height: height,
            webPreferences: {
                preload: path.join(__dirname, 'preload.js'),
                contextIsolation: true, // Assurez-vous que c'est activé
                nodeIntegration: false, // Toujours désactiver pour la sécurité
            },
        });
        detailProjetWindow.loadFile('src/taches.html'); // Assurez-vous que ce fichier existe
        detailProjetWindow.on('closed', () => {
            detailProjetWindow = null;
        });

        // Passer l'ID du projet à la fenêtre des détails
        detailProjetWindow.webContents.on('did-finish-load', () => {
            detailProjetWindow.webContents.send('load-projet-details',projetId);
        });
    }
}

let currentProjetId = null;

// Écouter le projet envoyé depuis renderer.js
ipcMain.on('open-projet-details', (event, projetId) => {
    // console.log(`ID du projet reçu dans le processus principal : ${projetId}`);
    currentProjetId = projetId; // Stocker l'ID du projet
    createDetailProjetWindow(projetId);
});

// Gérer la demande pour récupérer l'ID du projet
ipcMain.handle('get-projet-id', () => {
    // console.log(`ID du projet  renvoye : ${currentProjetId}`);
    return currentProjetId; // Retourner l'ID stocké
});

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});