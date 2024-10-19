const { contextBridge, ipcRenderer } = require('electron');
// const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('versions', {
    node: () => process.versions.node,
    chrome: () => process.versions.chrome,
    electron: () => process.versions.electron,
});

// Exposer une API pour charger les détails de l'événement
/* contextBridge.exposeInMainWorld('api', {
    loadEventDetails: (callback) => ipcRenderer.on('load-event-details', (event, eventId) => {
        callback(eventId);
    })
}); */
// const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
    send: (channel, data) => {
        const validChannels = ['open-event-details'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data); // Envoi de l'ID de l'événement
        }
    },
    loadEventDetails: (callback) => {
        ipcRenderer.invoke('get-event-id').then(callback);
    },
    getEventId: () => ipcRenderer.invoke('get-event-id')
    /* // Autres fonctions que vous avez définies
    showAddEvenementModal,
    deleteEvenement,
    loadEvenementForUpdate,
    recurrenceEvenement */
});
