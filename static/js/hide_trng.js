$(window).on('load', function(){
    var aircraft = $('#type_at').val();
    hide_trng(aircraft);
});

$("select[name=Type-AT]").change (function(){
    var aircraft = $('#type_at').val();
    hide_trng(aircraft);
});

function hide_prep(aircraft){
    if (aircraft == '320' || aircraft == '330' || aircraft == '350'){
        $('.preliminary').css("display","none");
    }
    else {
        $('.preliminary').css("display","grid");
    }
};
function hide_trng(aircraft){
    if (aircraft == '777' || aircraft == '737'){
        $('#print_seven').css("display","none");
        $('#print_five').css("display","none");
    } else if (aircraft == '330' || aircraft == '350') {
        $('#print_seven').css("display","none");
        $('#print_five').css("display","none");
    } else {
        $('#print_seven').css("display","block");
        $('#print_five').css("display","block");
    }
};