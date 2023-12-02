$(document).ready(function () {
    $('.game_word').hide();

    $('#reveal_button').click(function () {
        $('.game_word').toggle();
    });

    $('#player_word').on('click', '#succeeded_button', function () {
        const wordId = $(this).data('word-id');
        const gameId = $(this).data('game-id');
        const playerId = $(this).data('player-id');
        word_success(wordId, gameId, playerId);
    });

    $('#player_word').on('click', '#failed_button', function () {
        const wordId = $(this).data('word-id');
        const gameId = $(this).data('game-id');
        const playerId = $(this).data('player-id');
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
        const response = await fetch(`/gameroom/ajax/word_success/${wordId}/${gameId}/${playerId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('player_word').innerHTML = data.html;
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in word_success:', error);
    }
}

async function word_fail(wordId, gameId, playerId) {
    try {
        const response = await fetch(`/gameroom/ajax/word_fail/${wordId}/${gameId}/${playerId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('player_word').innerHTML = data.html;
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in word_success:', error);
    }
}