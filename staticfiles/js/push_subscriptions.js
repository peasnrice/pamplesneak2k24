// push_subscription.js

// Check for support and bind click event to the subscribe button
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.ready.then(function (registration) {
        registration.pushManager.getSubscription().then(function (subscription) {
            if (!subscription) {
                console.log('Subscribe button clicked');

                const subscribeButton = $('#subscribe');
                if (subscribeButton) {
                    subscribeButton.addEventListener('click', askPermission);
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

function initializePushNotifications() {
    // Check for Push API support
    if ('PushManager' in window) {
        navigator.serviceWorker.ready.then(function (registration) {
            registration.pushManager.getSubscription().then(function (subscription) {
                if (!subscription) {
                    askPermission().then(subscribeUserToPush(registration));
                } else {
                    console.log('User is already subscribed.');
                }
            });
        });
    } else {
        console.warn("Push messaging is not supported in this browser");
    }
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
            }
        });
}

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

function checkSubscription() {
    navigator.serviceWorker.ready.then(function (registration) {
        registration.pushManager.getSubscription().then(function (subscription) {
            if (subscription) {
                console.log('User is already subscribed:', subscription);
                // Send the existing subscription to the server to ensure it's recorded
                updateSubscriptionOnServer(subscription);
            } else {
                console.log('User is not subscribed.');
                // Optionally, prompt the user to subscribe here
            }
        });
    });
}

// Update or save the subscription on the server
function updateSubscriptionOnServer(subscription) {
    fetch('/update_or_save_subscription/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token // Ensure you're passing the CSRF token correctly
        },
        body: JSON.stringify(subscription)
    })
        .then(function (response) {
            if (response.ok) {
                console.log('Subscription record updated or saved on the server.');
            } else {
                console.error('Failed to update or save the subscription.');
            }
        });
}

document.addEventListener('DOMContentLoaded', function () {
    // Existing code for the hamburger menu
    var hamburger = document.getElementById('hamburger-button');
    var mobileMenu = document.getElementById('mobile-menu');

    checkSubscription();


    hamburger.addEventListener('click', function () {
        mobileMenu.classList.toggle('hidden');
    });

    // Additional code for subscription button
    var subscribeButton = document.getElementById('subscribe');
    if (subscribeButton) {
        subscribeButton.addEventListener('click', function () {
            console.log('Subscribe button was clicked.');
            askPermission();
        });
    } else {
        console.log('Subscribe button not found');
    }
});
