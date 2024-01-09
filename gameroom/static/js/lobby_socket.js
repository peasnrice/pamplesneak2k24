var lobbySocket = new WebSocket('ws://' + window.location.host + '/ws/gameroom/' + gameId + '/');
let countdownTimer;


lobbySocket.onmessage = function (e) {
    var data = JSON.parse(e.data);

    if (data['players']) {
        updatePlayerList(data['players']);
    }

    if (data.type === 'game.start') {
        // Redirect or refresh the page
        console.log("message received");
        window.location.reload();
    }

    if (data.type === 'round.transition' || data.type === 'round.create' || data.type === 'round.play') {
        document.getElementById('currentRound').textContent = `Round ${data.round_number}`;
        document.getElementById('gameState').textContent = `State: ${data.round_state}`;
        startCountdown(data.countdown_time);
    }

    if (data.type === 'game.end') {
        document.getElementById('game_info').style.display = 'none'; // Hide game_info
        document.getElementById('end_game').style.display = 'block';  // Show end_game
    }

};

function updatePlayerList(players) {
    var playerList = document.querySelector('.player-list');
    playerList.innerHTML = ''; // Clear existing player list

    players.forEach(function (player) {
        var li = document.createElement('li');
        li.textContent = player;
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
    clearInterval(countdownTimer);
    let totalMilliseconds = durationInSeconds * 1000;  // Convert seconds to milliseconds
    let milliseconds = totalMilliseconds;

    countdownTimer = setInterval(function () {
        if (milliseconds <= 0) {
            clearInterval(countdownTimer);
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

        milliseconds -= 100; // Decrement milliseconds by 100

    }, 100); // Update every 100 milliseconds
}