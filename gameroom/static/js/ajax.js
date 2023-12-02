async function refreshWords(wordBankSize) {
    const response = await fetch(`/ajax/refresh_words/${wordBankSize}/`);
    const data = await response.json();

    document.querySelector('#words_box').innerHTML = data.html;
}

async function refreshWord(gameId, playerId) {
    const response = await fetch(`/ajax/refresh_word/${gameId}/${playerId}/`);
    const data = await response.json();

    // Update the HTML content
    $('#player_word').html(data.html);

    // Execute any script tags in the response
    $('#player_word script').each(function () {
        eval($(this).text());
    });
}