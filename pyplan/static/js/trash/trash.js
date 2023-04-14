$(document).ready(function() {
$('.loading').css("display","none");
$("#show_pilots").click(function(){

    var aircraft = $('#flight').val();
    if (aircraft === 'Null'){
        alert("Выберите номер самолета!");
    }
    else{
    $('.loading').css("display","block");
    $.ajax({
        url: aircraft,
        success: function(data){
            console.log("Show pilots");
            $('#pilots_list').replaceWith($(data.html));
        },
     });
    }

});

});


