// push_subscription.js

// Check for support and manage subscription status
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.ready.then(registration => {
        registration.pushManager.getSubscription().then(subscription => {
            const subscribeButton = document.getElementById('subscribe');
            if (!subscription) {
                console.log('User is not subscribed.');
                if (subscribeButton) {
                    subscribeButton.addEventListener('click', () => askPermission().then(() => subscribeUserToPush(registration)));
                }
            } else {
                console.log('User is already subscribed:', subscription);
                updateSubscriptionOnServer(subscription);
            }
        });
    });
} else {
    console.warn("Push messaging is not supported in this browser");
}

// Request notification permission from the user
function askPermission() {
    return new Promise((resolve, reject) => {
        const permissionResult = Notification.requestPermission(result => resolve(result));
        if (permissionResult) {
            permissionResult.then(resolve, reject);
        }
    }).then(permissionResult => {
        if (permissionResult !== 'granted') {
            throw new Error('We weren\'t granted permission.');
        }
    });
}

// Convert VAPID public key from URL safe base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
    base64String = base64String.replace(/-/g, '+').replace(/_/g, '/');
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = base64String + padding;
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Subscribe the user to push notifications
function subscribeUserToPush(registration) {
    if (typeof vapid_public_key === 'undefined') {
        console.error('VAPID public key is not defined');
        return Promise.reject(new Error('VAPID public key is not defined'));
    }
    
    const applicationServerKey = urlBase64ToUint8Array(vapid_public_key);
    return registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey
    }).then(subscription => {
        console.log('User is subscribed.');
        return fetch('/save_subscription/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            body: JSON.stringify(subscription)
        });
    }).catch(error => {
        console.error('Failed to subscribe user:', error);
        throw error;
    });
}

// Update or save the subscription on the server
function updateSubscriptionOnServer(subscription) {
    fetch('/update_or_save_subscription/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify(subscription)
    }).then(response => {
        if (response.ok) {
            console.log('Subscription record updated or saved on the server.');
        } else {
            console.error('Failed to update or save the subscription.');
        }
    });
}

// document.addEventListener('DOMContentLoaded', () => {
//     // Check subscription status on load
//     if ('serviceWorker' in navigator && 'PushManager' in window) {
//         navigator.serviceWorker.ready.then(checkSubscription);
//     }
// });
