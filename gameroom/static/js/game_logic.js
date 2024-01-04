var refreshIntervalId = null;

$(document).ready(function () {

    var currentCardIndex = parseInt(localStorage.getItem('lastShownCardIndex'), 10) || 0;
    var cards = $('.carousel-container .carousel-card');
    var cards_length = cards.length;

    if (cards_length <= currentCardIndex) {
        currentCardIndex = cards_length - 1;
    }

    if (currentCardIndex < 0) {
        currentCardIndex = 0;
        localStorage.setItem('lastShownCardIndex', 0);
    }

    $('#show_all_button').hide();
    $('#hide_all_button').show();

    attachButtonHandlers();


    $('#player_word').on('click', '.succeeded_button', function () {
        const wordId = $(this).data('word-id');
        const gameId = $(this).data('game-id');
        const playerId = $(this).data('player-id');
        word_success(wordId, gameId, playerId);
    });

    $('#player_word').on('click', '.failed_button', function () {
        const wordId = $(this).data('word-id');
        const gameId = $(this).data('game-id');
        const playerId = $(this).data('player-id');
        word_fail(wordId, gameId, playerId);
    });

    $('#player_word').on('click', '.skipped_button', function () {
        const wordId = $(this).data('word-id');
        const gameId = $(this).data('game-id');
        const playerId = $(this).data('player-id');
        word_fail(wordId, gameId, playerId);
    });

    // Character count for the 'word' field
    $('#id_word').on('input', function () {
        const currentLength = $(this).val().length;
        $('#word_count').text(`${currentLength}/128`);
    });

    // Delegated event handling for dynamic content
    $('#player_word').on('click', '#next_button', function () {
        cards = $('.carousel-container .carousel-card');
        cards_length = cards.length;

        if (cards_length <= currentCardIndex) {
            currentCardIndex = cards_length - 1;
        }

        if (currentCardIndex < 0) {
            currentCardIndex = 0;
            localStorage.setItem('lastShownCardIndex', 0);
        }

        if (currentCardIndex < cards.length - 1) {
            currentCardIndex += 1;
            showCard(currentCardIndex);
        } else {
            currentCardIndex = 0;
            showCard(currentCardIndex);
        }
    });

    $('#player_word').on('click', '#prev_button', function () {
        cards = $('.carousel-container .carousel-card');
        cards_length = cards.length;

        if (cards_length <= currentCardIndex) {
            currentCardIndex = cards_length - 1;
        }

        if (currentCardIndex < 0) {
            currentCardIndex = 0;
            localStorage.setItem('lastShownCardIndex', 0);
        }

        if (currentCardIndex > 0) {
            currentCardIndex -= 1;
            showCard(currentCardIndex);
        } else {
            currentCardIndex = cards.length - 1;
            showCard(currentCardIndex);
        }
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
            attachButtonHandlers();
            initializeCards();
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
            attachButtonHandlers();
            initializeCards();
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
            attachButtonHandlers();
            initializeCards();
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }

    } catch (error) {
        console.error('Error in word_success:', error);
    }
}

async function refresh_word(gameId, playerId) {
    var currentCardIndex = parseInt(localStorage.getItem('lastShownCardIndex'), 10) || 0;
    var cards = $('.carousel-container .carousel-card');
    var cards_length = cards.length;

    if (cards_length <= currentCardIndex) {
        currentCardIndex = cards_length - 1;
    }

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
            attachButtonHandlers();
            initializeCards();

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

            $('#id_word').val(data.response_text);
            $('#id_word').trigger('input');


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

function initializeCards() {
    var cards = $('.carousel-container .carousel-card');
    var cards_length = cards.length;

    // Hide all cards initially
    // $('.carousel-card').hide();

    var lastShownCardIndex = parseInt(localStorage.getItem('lastShownCardIndex'), 10) || 0;

    if (lastShownCardIndex >= cards_length) {
        lastShownCardIndex = cards_length - 1;
    }

    if (lastShownCardIndex < 0) {
        lastShownCardIndex = 0;
    }

    var lastShowCardContents = localStorage.getItem('lastShowCardContents') || "false";

    if (lastShowCardContents == "true") {
        // $('.carousel-card .toggle-content').show();
        $('.carousel-card .game_word').removeClass('blur-sm pointer-events-none');
        $('#show_all_button').hide();
        $('#hide_all_button').show();
    } else {
        // $('.carousel-card .toggle-content').hide();
        $('.carousel-card .game_word').addClass('blur-sm pointer-events-none');
        $('#show_all_button').show();
        $('#hide_all_button').hide();
    }

    if (lastShownCardIndex >= cards_length) {
        lastShownCardIndex = cards_length - 1;
    }



    showCard(lastShownCardIndex);
}

function showCard(index) {
    var cards = $('.carousel-container .carousel-card');

    // Hide all cards
    cards.hide();
    console.log(index);
    // Show the selected card
    var selectedCard = $(cards[index]);
    selectedCard.show();

    // Store the current index in local storage
    localStorage.setItem('lastShownCardIndex', index.toString());
}

function attachButtonHandlers() {
    $('#show_all_button').off('click').on('click', function () {
        $('.carousel-card .game_word').removeClass('blur-sm pointer-events-none');
        $('#show_all_button').hide();
        $('#hide_all_button').show();
        localStorage.setItem('lastShowCardContents', 'true');
    });

    $('#hide_all_button').off('click').on('click', function () {
        $('.carousel-card .game_word').addClass('blur-sm pointer-events-none');
        $('#show_all_button').show();
        $('#hide_all_button').hide();
        localStorage.setItem('lastShowCardContents', 'false');
    });
}