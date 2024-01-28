// push_subscription.js

// Function to convert VAPID public key from URL safe base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
    // Replace URL-safe base64 characters with standard base64 characters
    base64String = base64String.replace(/-/g, '+').replace(/_/g, '/');

    // Add padding if necessary to make the string length a multiple of 4
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = base64String + padding;

    // Decode base64 string to raw binary data
    console.log(base64);
    console.log(window.atob(base64));
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    // Convert binary data to a Uint8Array
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}


// Function to subscribe user to push notifications
function subscribeUserToPush(registration) {
    const applicationServerKey = urlBase64ToUint8Array(vapid_public_key);
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
            })
                .then(function () {
                    // Send a push notification immediately after subscribing
                    sendPushNotification();
                });
        });
}

// Function to ask for notification permission
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
                navigator.serviceWorker.ready.then(subscribeUserToPush);
            }
        });
}

// Check for support and bind click event to the subscribe button
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.ready.then(function (registration) {
        registration.pushManager.getSubscription().then(function (subscription) {
            if (!subscription) {
                console.log('Subscribe button clicked');

                const subscribeButton = document.querySelector('#subscribe');
                if (subscribeButton) {
                    subscribeButton.addEventListener('click', askPermission);
                }
            } else {
                console.log('User is already subscribed:', subscription);
                sendPushNotification(registration);
            }
        });
    });
} else {
    console.warn("Push messaging is not supported in this browser");
}

// Function to send a push notification
function sendPushNotification(registration) {
    // Customize your notification payload here
    const notificationOptions = {
        body: 'This is a push notification on page load!',
        icon: 'your-icon-url.png', // Add the URL of your notification icon
    };

    // Use the Service Worker's registration to show the notification
    registration.showNotification('Notification Title', notificationOptions);
}

const notification = document.querySelector('#notification');
const sendButton = document.querySelector('#send');
const registration = await navigator.serviceWorker.getRegistration();

const sendNotification = async () => {
    if (Notification.permission === 'granted') {
        showNotification(notification.value);
    }
    else {
        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();

            if (permission === 'granted') {
                showNotification(notification.value);
            }
        }
    }
};

const showNotification = body => {
    const title = 'What PWA Can Do Today';

    const payload = {
        body
    };

    if ('showNotification' in registration) {
        registration.showNotification(title, payload);
    }
    else {
        new Notification(title, payload);
    }
};

document.querySelector('#send-notification').addEventListener('click', function () {
    sendNotification();
});