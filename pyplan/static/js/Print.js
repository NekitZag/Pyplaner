
function printTable(){
    var body = $('body').html(),
        el = $('.print');
        $('body').html(el);
        window.print();
        $('body').html(body);

}