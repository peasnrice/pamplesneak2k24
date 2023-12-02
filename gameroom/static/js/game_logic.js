$(document).ready(function () {
    $('.game_word').hide();

    $('#reveal_button').click(function () {
        $('.game_word').toggle();
    });

    // Attach event handlers for succeeded and failed buttons
    $('#succeeded_button').click(function () {
        const wordId = $('#succeeded_button').data('word-id');
        const gameId = $('#succeeded_button').data('game-id');
        const playerId = $('#succeeded_button').data('player-id');
        word_success(wordId, gameId, playerId);
    });

    $('#failed_button').click(function () {
        const wordId = $('#failed_button').data('word-id');
        const gameId = $('#succeeded_button').data('game-id');
        const playerId = $('#succeeded_button').data('player-id');
        word_fail(wordId, gameId, playerId);
    });

});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function word_success(wordId, gameId, playerId) {
    try {
        // Perform an AJAX request to a Django view
        const response = await fetch(`/gameroom/ajax/word_success/${wordId}/${gameId}/${playerId}/`, {
            method: 'POST', // or 'GET', depending on your server setup
            headers: {
                'X-CSRFToken': getCookie('csrftoken'), // CSRF token, required for POST requests
                'Content-Type': 'application/json'
            },
            // Additional data can be sent in the body, if necessary
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        document.getElementById('player_word').innerHTML = data["response"];

    } catch (error) {
        console.error('Error in word_success:', error);
    }
}

async function word_fail(wordId, gameId, playerId) {
    try {
        const response = await fetch(`/gameroom/ajax/word_fail/${wordId}/${gameId}/${playerId}/`, {
            method: 'POST', // or 'GET'
            headers: {
                'X-CSRFToken': getCookie('csrftoken'), // CSRF token
                'Content-Type': 'application/json'
            },
            // Additional data can be sent in the body, if necessary
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        document.getElementById('player_word').innerHTML = data["response"];

    } catch (error) {
        console.error('Error in word_fail:', error);
    }
}