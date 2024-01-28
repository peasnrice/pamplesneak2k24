// push-subscription.js
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.ready.then(function (registration) {
        // Check if the user is already subscribed
        registration.pushManager.getSubscription().then(function (subscription) {
            if (subscription) {
                console.log('User is already subscribed:', subscription);
            } else {
                // Subscribe user here, typically after a user gesture
                // Example: User clicks a "Subscribe to Notifications" button
            }
        });
    });
}

function subscribeUserToPush(registration) {
    const applicationServerKey = urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY');
    return registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey
    })
        .then(function (subscription) {
            // Send the subscription details to the server using the Fetch API or AJAX
            fetch('/save_subscription/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subscription)
            });
        });
}

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

function askPermission() {
    return new Promise(function (resolve, reject) {
        const permissionResult = Notification.requestPermission(function (result) {
            resolve(result);
        });

        if (permissionResult) {
            permissionResult.then(resolve, reject);
        }
    })
        .then(function (permissionResult) {
            if (permissionResult !== 'granted') {
                throw new Error('We weren\'t granted permission.');
            } else {
                subscribeUserToPush(); // Call function to subscribe user
            }
        });
}

document.querySelector('#subscribe').addEventListener('click', function () {
    askPermission();
});