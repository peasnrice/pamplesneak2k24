$(document).ready(function () {

    $('.game_word').hide();

    $('#player_word').on('click', '#reveal_button', function () {
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

    setInterval(refresh_word.bind(null, gameId, playerId), 10000);  // Refresh every 10 seconds
    refresh_word(gameId, playerId);  // Initial call to refresh word

    // Message pop-up logic
    var messageContainer = $('#message-container');
    if (messageContainer.length) {
        // Show the message container for 5 seconds
        messageContainer.fadeIn().delay(5000).fadeOut();
    }

    $('#random_word_button').click(randomize_word); // Bind the function to the button click
    $('#random_player_button').click(randomize_player); // Bind the function to the button click


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
            $('#player_word').html(data.html);
            $('.game_word').hide();
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
            $('#player_word').html(data.html);
            $('.game_word').hide();
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in word_success:', error);
    }
}

async function refresh_word(gameId, playerId) {

    const wordCurrentlyNotPresent = $('#player_word').find('#word_not_present').length > 0;
    const gameWordDisplayStyle = $('.game_word').css('display');


    try {
        const response = await fetch(`/gameroom/ajax/refresh_word/${gameId}/${playerId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
        });

        if (response.ok) {
            const data = await response.json();
            $('#player_word').html(data.html);
            $('.game_word').css('display', gameWordDisplayStyle);

            const wordNowPresent = $('#player_word').find('#word_present').length > 0;
            if (wordCurrentlyNotPresent && wordNowPresent) {
                $('.game_word').hide();
            }

        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in word_success:', error);
    }
}

async function randomize_word() {

    var obscurity = $('#obscurity_level').val();
    var silliness = $('#silliness_level').val();

    try {
        const response = await fetch('/gameroom/ajax/openai_request/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'obscurity': obscurity,
                'silliness': silliness,
                'max_tokens': 64
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data.response_text);

            $('#id_word').val(data.response_text);

        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Error in randomize_word:', error);
    }
}

async function randomize_player() {
    // Get the dropdown element
    var playerSelect = document.getElementById('id_target');

    // Calculate a random index
    var randomIndex = Math.floor(Math.random() * playerSelect.options.length);
    console.log(randomIndex);

    // Set the selected index
    playerSelect.selectedIndex = randomIndex;
}
