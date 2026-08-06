// SIGHU service worker — v1
// Mantiene la app instalable, cachea shell mínimo y maneja push notifications.

const CACHE_NAME = 'sighu-shell-v1';
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

// Push handler — el payload viene como JSON con {title, body, url, icon, tag}
self.addEventListener('push', (event) => {
    let data = {};
    try {
        data = event.data ? event.data.json() : {};
    } catch (e) {
        data = { title: 'SIGHU', body: event.data ? event.data.text() : '' };
    }
    const title = data.title || 'SIGHU';
    const options = {
        body: data.body || '',
        icon: data.icon || '/static/pwa/icon-192.png',
        badge: '/static/pwa/icon-192.png',
        tag: data.tag || 'sighu',
        data: { url: data.url || '/' },
        renotify: true,
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

// Click en la notificación — enfoca la ventana existente o abre una nueva
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const targetUrl = (event.notification.data && event.notification.data.url) || '/';
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
