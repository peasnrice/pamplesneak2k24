// push-subscription.js
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.ready.then(function (registration) {
        registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array('PUBLIC_VAPID_KEY')
        }).then(function (subscription) {
            console.log('Push subscription:', subscription);
            // TODO: Send subscription to the backend for saving to send push messages later
        }).catch(function (error) {
            console.error('Push subscription error:', error);
        });
    });
} else {
    console.warn("Push messaging is not supported");
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