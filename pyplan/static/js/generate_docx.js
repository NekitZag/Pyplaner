
//$(document).ready( function() {
//
//    });
$("#docx_but").click(function(){
        var aircraft = $('#type_at').val();
        $.ajax({
                            url: 'generate_docx/'+ aircraft+ '/' + index_select_database,
                            success: function(data)
                            {
                             console.log(aircraft)
                            },
                            async: false,
                           });
    });
