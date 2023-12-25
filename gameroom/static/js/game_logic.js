var refreshIntervalId = null;

$(document).ready(function () {

    $('.game_word').hide();
    $('#show_button').hide();
    $('#hide_button').show();

    $('#player_word').on('click', '#show_button', function () {
        $('.game_word').show();
        $('#show_button').hide();
        $('#hide_button').show();
    });

    $('#player_word').on('click', '#hide_button', function () {
        $('.game_word').hide();
        $('#show_button').show();
        $('#hide_button').hide();
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

    $('#player_word').on('click', '#skipped_button', function () {
        const wordId = $(this).data('word-id');
        const gameId = $(this).data('game-id');
        const playerId = $(this).data('player-id');
        word_fail(wordId, gameId, playerId);
    });

    // Character count for the 'word' field
    $('#id_word').on('input', function () {
        const currentLength = $(this).val().length;
        $('#word_count').text(`${currentLength}/64`);
    });


    if (!refreshIntervalId) {
        refreshIntervalId = setInterval(refresh_word.bind(null, gameId, playerId), 10000);
    }
    refresh_word(gameId, playerId);  // Initial call to refresh word


    // Message pop-up logic
    var messageContainer = $('#message-container');
    if (messageContainer.length) {
        // Show the message container for 5 seconds
        messageContainer.fadeIn().delay(5000).fadeOut();
    }

    // $('#random_word_button').click(randomize_word); // Bind the function to the button click
    // $('#random_player_button').click(randomize_player); // Bind the function to the button click

    $(document).on('click', '.validate_sneak', function () {
        var sneakId = $(this).closest('div[id]').attr('id');
        validate_sneak(sneakId);
    });

    $(document).on('click', '.reject_sneak', function () {
        var sneakId = $(this).closest('div[id]').attr('id');
        reject_sneak(sneakId);
    });

    $(document).on('click', '#show_button', function () {
        $('.game_word').show();
        $('#show_button').hide();
        $('#hide_button').show();
    });

    $(document).on('click', '#hide_button', function () {
        $('.game_word').hide();
        $('#show_button').show();
        $('#hide_button').hide();
    });

    // Show QR Code
    $(document).on('click', '#show_qr_code_button', function () {
        $('#qrCodeImage').show();
        $('#show_qr_code_button').hide();
        $('#hide_qr_code_button').show();
    });

    // Hide QR Code
    $(document).on('click', '#hide_qr_code_button', function () {
        $('#qrCodeImage').hide();
        $('#show_qr_code_button').show();
        $('#hide_qr_code_button').hide();
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

async function word_skip(wordId, gameId, playerId) {
    try {
        const response = await fetch(`/gameroom/ajax/word_skip/${wordId}/${gameId}/${playerId}/`, {
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
    console.log(gameWordDisplayStyle)


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
            if (gameWordDisplayStyle == 'none') {
                $('#show_button').show();
                $('#hide_button').hide();
            } else {
                $('#show_button').hide();
                $('#hide_button').show();
            }

            const wordNowPresent = $('#player_word').find('#word_present').length > 0;
            if (wordCurrentlyNotPresent && wordNowPresent) {
                $('.game_word').hide();
                $('#show_button').show();
                $('#hide_button').hide();
            }

        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in word_success:', error);
    }
}

async function get_inspiration() {
    try {
        const response = await fetch('/gameroom/ajax/inspiration/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data.response_text);

            $('#id_word').val(data.response_text);

        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Error in retrieving inspiration:', error);
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

async function validate_sneak(sneakId) {
    try {
        const response = await fetch(`/gameroom/ajax/validate_sneak/${gameId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'sneak_id': sneakId })
        });

        if (response.ok) {
            const data = await response.json();
            updateVoteCounts(sneakId, data.validations_count, data.rejections_count);
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in validate_sneak:', error);
    }
}

async function reject_sneak(sneakId) {
    try {
        const response = await fetch(`/gameroom/ajax/reject_sneak/${gameId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'sneak_id': sneakId })
        });

        if (response.ok) {
            const data = await response.json();
            updateVoteCounts(sneakId, data.validations_count, data.rejections_count);
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in reject_sneak:', error);
    }
}


function updateVoteCounts(sneakId, validationsCount, rejectionsCount) {
    var container = $('#' + sneakId);
    container.find('.votes').html('Validations: <strong>' + validationsCount + ' 🌟</strong>, Rejections: <strong>' + rejectionsCount + ' 💔</strong>');
}