
$(document).ready(function() {
var kvs;
var sec_pil;
var int_pil;
var tetstt;
var second_pil;

$('#pilots').each(function() {
//    tetstt = $(this).find('.people').length;  // тестовый вывод всех
    $kvs = $(this).find('.people[id$="1/10"]').length;
    $int_pil = $(this).find('.people[id$="3/10"]').length;
    sec_pil = $(this).find('.people[id$="/20"]').length;
    scec_pil = $(this).find('.people[id$="2/10"]').length;
    $second_pil = sec_pil + scec_pil;

    $('#count_kvs').text('КВС: ' + $kvs);
    $('#count_secpil').text('Вторые: ' + $second_pil);
    $('#count_instr').text('Пил-инстр: ' + $int_pil);

});
});