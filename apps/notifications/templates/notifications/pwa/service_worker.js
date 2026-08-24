// SIGHU service worker — v2 (postMessage a clientes al recibir push)
// Mantiene la app instalable, cachea shell mínimo y maneja push notifications.

const CACHE_NAME = 'sighu-shell-v2';
const OFFLINE_URL = '/pwa/offline/';
const SHELL = [
    OFFLINE_URL,
    '/static/pwa/icon-192.png',
    '/static/pwa/icon-512.png',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL)).catch(() => {})
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((names) =>
            Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
        )
    );
    self.clients.claim();
});

// Solo interceptamos navegación (documentos HTML) para servir la página offline
// cuando no hay red. El resto pasa directo al navegador — no queremos cachear
// respuestas dinámicas de Django ni interferir con CSRF/sesiones.
self.addEventListener('fetch', (event) => {
    if (event.request.mode !== 'navigate') return;
    event.respondWith(
        fetch(event.request).catch(() => caches.match(OFFLINE_URL))
    );
});

// Push handler — payload esperado:
//   {title, body, url, icon, tag, tagGroup, actions, vibrate}
// tagGroup permite que varias notif del mismo tipo (ej. recordatorios de
// sesión) se agrupen bajo un solo tag → solo la última visible en la barra.
self.addEventListener('push', (event) => {
    let data = {};
    try {
        data = event.data ? event.data.json() : {};
    } catch (e) {
        data = { title: 'SIGHU', body: event.data ? event.data.text() : '' };
    }
    const title = data.title || 'SIGHU';
    const tag = data.tagGroup || data.tag || 'sighu';
    const options = {
        body: data.body || '',
        icon: data.icon || '/static/pwa/icon-192.png',
        badge: '/static/pwa/icon-192.png',
        tag,
        renotify: true,
        // Vibración corta (Android): dos pulsos de 200ms con 100ms de pausa.
        // iOS ignora este campo y usa su propio patrón por defecto.
        vibrate: data.vibrate || [200, 100, 200],
        // actions: array de {action, title, icon}. Android desktop las muestra
        // como botones; iOS los ignora (solo tap principal funciona).
        actions: Array.isArray(data.actions) ? data.actions : [],
        // Guardamos url + urls por acción para el click handler
        data: {
            url: data.url || '/',
            actionUrls: data.actionUrls || {},
        },
    };
    event.waitUntil(Promise.all([
        self.registration.showNotification(title, options),
        // Avisa a los clientes abiertos para que reproduzcan un beep in-app.
        // El sistema operativo suena por su cuenta si la pestaña está en
        // segundo plano; este ping solo suena cuando SIGHU está abierto.
        self.clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(function (clients) {
                clients.forEach(function (c) {
                    c.postMessage({ type: 'sighu-push', title: title, tag: tag });
                });
            })
            .catch(function () { /* silencioso */ }),
    ]));
});

// Click en la notificación (o en un botón de acción) — enfoca ventana o abre nueva
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const dataUrl = (event.notification.data && event.notification.data.url) || '/';
    const actionUrls = (event.notification.data && event.notification.data.actionUrls) || {};
    // Si tocó un botón de acción con URL propia, gana esa; si no, la general.
    const targetUrl = (event.action && actionUrls[event.action]) || dataUrl;
    event.waitUntil(
        self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            for (const client of clientList) {
                if ('focus' in client) {
                    client.navigate(targetUrl);
                    return client.focus();
                }
            }
            if (self.clients.openWindow) return self.clients.openWindow(targetUrl);
        })
    );
});
