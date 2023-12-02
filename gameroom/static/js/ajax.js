// async function refreshWords(wordBankSize) {
//     const response = await fetch(`/ajax/refresh_words/${wordBankSize}/`);
//     const data = await response.json();

//     document.querySelector('#words_box').innerHTML = data.html;
// }

// async function word_success(wordId, gameId, playerId) {
//     const response = await fetch(`/ajax/word_success/${wordId}/${gameId}/${playerId}`);
//     const data = await response.json();

//     $('#player_word').html(data.html);

//     $('#player_word script').each(function () {
//         eval($(this).text());
//     });
// }

// async function word_fail(wordId, gameId, playerId) {
//     const response = await fetch(`/ajax/word_fail/${wordId}/${gameId}/${playerId}`);
//     const data = await response.json();

//     $('#player_word').html(data.html);

//     $('#player_word script').each(function () {
//         eval($(this).text());
//     });
// }