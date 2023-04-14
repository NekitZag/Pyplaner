// --------------------------------------Событие изменения таблицы----------------------------------------------------------
$("#followers, #posts").on("DOMSubtreeModified",function(){
   //...............динамический подсчет групп цветов..................
    $('#group-color[name="Type-group"] option').each(function(){
        var attr=$(this).attr('name');
        if (typeof attr !== 'undefined' && attr !== false)
        {
            count_sim=$("#main_display_table").find('label:contains('+$(this).attr('name')+')').length;
            $(this).text($(this).attr('name')+' '+ ($(this).attr('name')=="Refresh/Check"? Math.floor(count_sim/2) :count_sim));
        }
    });
});