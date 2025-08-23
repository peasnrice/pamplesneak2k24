// Check if gameId is defined
if (typeof gameId === 'undefined') {
    console.error('gameId is not defined. Cannot establish WebSocket connection.');
    throw new Error('gameId is required but not defined');
}

var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
var lobbySocket;
var timerInterval; // Declare this at the top level

try {
    lobbySocket = new WebSocket(protocol + '//' + window.location.host + '/ws/gameroom/' + gameId + '/');
} catch (error) {
    console.error('Failed to create WebSocket connection:', error);
    throw error;
}

$(document).ready(function () {
    updateRoundStateDisplay(roundState);
    startCountdown(countdownTimer);
})

lobbySocket.onmessage = function (e) {
    var data;
    try {
        data = JSON.parse(e.data);
    } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        return;
    }

    if (data['players']) {
        updatePlayerList(data['players']);
    }

    if (data.type === 'game.start') {
        // Redirect or refresh the page
        window.location.reload();
    }

    if (data.type === 'round.transition') {
        window.location.reload();
    }

    if (data.type === 'round.transition' || data.type === 'round.create' || data.type === 'round.play') {
        document.getElementById('currentRound').textContent = `Round ${data.round_number} of ${number_of_rounds}`;
        document.getElementById('gameState').textContent = `State: ${data.round_state}`;
        startCountdown(data.countdown_time);

        // Handling round states
        updateRoundStateDisplay(data.round_state);
    }

    if (data.type === 'game.end') {
        document.getElementById('game_info').style.display = 'none'; // Hide game_info
        document.getElementById('end_game').style.display = 'block';  // Show end_game
        window.location.reload();
    }

};

function updatePlayerList(players) {
    var playerList = document.querySelector('.player-list');
    if (!playerList) {
        console.error('Player list element not found');
        return;
    }
    
    playerList.innerHTML = ''; // Clear existing player list

    if (!Array.isArray(players)) {
        console.error('Players data is not an array');
        return;
    }

    players.forEach(function (player) {
        if (!player || typeof player.name !== 'string') {
            console.warn('Invalid player data:', player);
            return;
        }
        
        var li = document.createElement('li');
        var text = player.name;
        if (player.is_host) {
            text += " (host)";
        }
        li.textContent = text; // Using textContent prevents XSS
        playerList.appendChild(li);
    });
}

lobbySocket.onclose = function (e) {
    console.error('Lobby socket closed unexpectedly: Code', e.code, 'Reason', e.reason);
};

lobbySocket.onerror = function (error) {
    console.error('WebSocket Error: ', error);
};

function startCountdown(durationInSeconds) {
    clearInterval(timerInterval); // Clear any existing interval to prevent multiple timers

    let totalMilliseconds = durationInSeconds * 1000; // Convert seconds to milliseconds
    let milliseconds = totalMilliseconds;

    timerInterval = setInterval(function () {
        if (milliseconds <= 0) {
            clearInterval(timerInterval); // Stop the timer when it reaches zero
            document.getElementById('countdown').textContent = "00:00:00";
            return;
        }

        let minutes = Math.floor(milliseconds / (60 * 1000));
        let seconds = Math.floor((milliseconds % (60 * 1000)) / 1000);
        let millisecondsDisplay = milliseconds % 1000; // Remaining milliseconds

        // Format the time and update the countdown display
        let formattedMilliseconds = millisecondsDisplay > 0 ? "." + millisecondsDisplay.toString().replace(/0+$/, '') : "";

        document.getElementById('countdown').textContent =
            minutes.toString().padStart(2, '0') + ":" +
            seconds.toString().padStart(2, '0') +
            formattedMilliseconds;

        milliseconds -= 100; // Decrement milliseconds by 100 for each interval

    }, 100); // Update every 100 milliseconds
}

function updateRoundStateDisplay(roundState) {

    document.getElementById('currentRound').textContent = 'Round ' + current_round + ' of ' + number_of_rounds;
    document.getElementById('gameState').textContent = 'State: ' + roundState;
    // Hide all states initially
    $('#transitionState').hide();
    $('#playState').hide();
    $('#createState').hide();
    // Show the relevant state
    if (roundState === 'transition') {
        $('#transitionState').show();
    } else if (roundState === 'play') {
        $('#playState').show();
    } else if (roundState === 'create') {
        $('#createState').show();
    }
}


