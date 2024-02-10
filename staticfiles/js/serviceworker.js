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
    const eventData = event.data.json(); // Assuming the incoming data is a JSON string.
    const notificationTitle = eventData.notification.title;
    const notificationOptions = {
        body: eventData.notification.body,
        icon: eventData.notification.icon,
        data: {
            url: eventData.notification.click_action
        }
    };

    event.waitUntil(
        self.registration.showNotification(notificationTitle, notificationOptions)
    );
});
