const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
let detailWindow; // Variable pour stocker la fenêtre des détails

function createWindow() {
    const win = new BrowserWindow({
        width: 900,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: false, // Active le contexte isolé
            nodeIntegration: true, // Désactive nodeIntegration pour la sécurité
        },
    });

    win.loadFile('src/index.html');
}

// Fonction pour créer la fenêtre de détails
function createDetailWindow(eventId) {
    if (detailWindow) {
        detailWindow.focus();
    } else {
        detailWindow = new BrowserWindow({
            width: 800,
            height: 600,
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