// serviceworker.js
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
});

self.addEventListener('push', function (event) {
    const options = {
        body: event.data.text(),
        // You can add more options here, like icons, images, vibrate, etc.
    };
    event.waitUntil(
        self.registration.showNotification('Notification Title', options)
    );
});

navigator.serviceWorker.register('/path/to/serviceworker.js')
    .then(function (swReg) {
        console.log('Service Worker is registered', swReg);
    })
    .catch(function (error) {
        console.error('Service Worker Error', error);
    });