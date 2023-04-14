var blind = false;
$('#blind').click(function(){
        if (blind == false){
            $("html").css({
                'filter': 'grayscale(1)',
            });
            blind = true;
        }
        else {
               $("html").css({
                'filter': 'grayscale(0)',
            });
            blind = false;
        }

});