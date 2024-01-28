$(document).ready(function () {
    const roundsSelect = $('#id_number_of_rounds');
    const durationSelect = $('#id_round_duration');
    const durationDescription = $('#round-duration-description');
    const gameTimeCalculator = $('#game-time-calculator');
    const additionalSneaksSection = $('#id_allow_additional_sneaks').parent();
    const timeBetweenRoundsSection = $('#id_time_between_rounds').parent();

    function format12HourClock(date) {
        let hours = date.getHours();
        let minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        minutes = minutes < 10 ? '0' + minutes : minutes;
        return hours + ':' + minutes + ' ' + ampm;
    }

    function updateEndTime(totalMinutes) {
        const now = new Date();
        // Round up to the nearest 5 minutes
        const roundedMinutes = Math.ceil((now.getMinutes() + totalMinutes) / 5) * 5;
        now.setMinutes(roundedMinutes);

        // Adjust hours if minutes have overflowed 60
        if (roundedMinutes >= 60) {
            const extraHours = Math.floor(roundedMinutes / 60);
            now.setHours(now.getHours() + extraHours);
            now.setMinutes(roundedMinutes % 60);
        }

        $('#game-end-time').text(format12HourClock(now));
    }

    function formatTime(totalMinutes) {
        if (totalMinutes >= 60) {
            const hours = Math.floor(totalMinutes / 60);
            const minutes = totalMinutes % 60;
            let timeString = `${hours} hour${hours > 1 ? 's' : ''}`;
            if (minutes > 0) {
                timeString += ` and ${minutes} minute${minutes > 1 ? 's' : ''}`;
            }
            return timeString;
        } else if (totalMinutes > 0) {
            return `${totalMinutes} minute${totalMinutes > 1 ? 's' : ''}`;
        } else {
            return '0'; // Return just '0' when totalMinutes is 0
        }
    }

    function calculateTotalGameTime() {
        const numberOfRounds = roundsSelect.val() !== 'open' ? parseInt(roundsSelect.val()) : 0;
        const roundDuration = durationSelect.val() ? parseInt(durationSelect.val()) : 0;
        const totalMinutes = numberOfRounds * roundDuration;
        $('#total-game-time').text(formatTime(totalMinutes));
        updateEndTime(totalMinutes); // Update end time
    }

    function toggleDurationVisibility() {
        if (roundsSelect.val() === 'open') {
            durationSelect.hide();
            durationDescription.text("There is no round duration, the game will end when the host ends the game.");
            gameTimeCalculator.hide();
        } else {
            durationSelect.show();
            durationDescription.text("Round duration");
            gameTimeCalculator.show();
            calculateTotalGameTime();
        }
    }

    function toggleAdditionalFieldsVisibility() {
        if (roundsSelect.val() === 'open') {
            durationSelect.hide();
            durationDescription.text("There is no round duration, the game will end when the host ends the game.");
            gameTimeCalculator.hide();
            additionalSneaksSection.hide();
            timeBetweenRoundsSection.hide();
        } else {
            durationSelect.show();
            durationDescription.text("Round duration");
            gameTimeCalculator.show();
            additionalSneaksSection.show();
            timeBetweenRoundsSection.show();
            calculateTotalGameTime(); // Recalculate total time when not open-ended
        }
    }

    roundsSelect.change(function () {
        toggleAdditionalFieldsVisibility();
        calculateTotalGameTime();
    });
    durationSelect.change(calculateTotalGameTime);
    toggleAdditionalFieldsVisibility(); // Call on initial load
    calculateTotalGameTime(); // Calculate initial total game time
});