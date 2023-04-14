$(document).ready(function($) {
check_comment=null;
currentElement=null;
	$('.popup-open').click(function() {
	    $('#context-menu').removeClass( ['visible' ] )
		currentElement = document.elementFromPoint(parseInt($('#context-menu').css('left'))-1,
                        parseInt($('#context-menu').css('top'))-1);
        $('.popup-fade').fadeIn();
		$.ajax({ // Обновление таблицы цветов
                     url: 'read_comment_person/' + $(currentElement).closest('div.test-flex').attr('id')+'/'+$(currentElement).attr('id').split('/')[0]+'/'+index_select_database,
                     success: function (data) {
                            $('#textComment').val(data["comment"]);
                            check_comment=data["comment"];
                      },
                      async:false,
        });
		return false;
	});

	$('.popup-close').click(function() {
		$(this).parents('.popup-fade').fadeOut();
		write_db_comment();
		return false;
	});

//	$(document).keydown(function(e) {
//		if (e.keyCode === 27) {
//			e.stopPropagation();
//			$('.popup-fade').fadeOut();
//		}
//	});

	$('.popup-fade').click(function(e) {
		if ($(e.target).closest('.popup').length == 0) {
			$(this).fadeOut();
			write_db_comment();
		}
	});

	function write_db_comment(){
	    if (check_comment!=$('#textComment').val())
	    $.ajax({
	    url: 'write_comment_person/'+ ($('#textComment').val()==''? '`' : $('#textComment').val())+'/'+ $(currentElement).closest('div.test-flex').attr('id')+'/'+$(currentElement).attr('id').split('/')[0]+'/'+index_select_database,
	    success: function (data) {
             console.log("Коментарий для id_pers: "+$(currentElement).attr('id').split('/')[0]+" на сессии id_wcrew:"+ $(currentElement).closest('div.test-flex').attr('id')+ " записан.");
             if ($('#textComment').val()!='')
                {
                 if (!$(currentElement).find("svg[id='Icons']").length)
                    $(currentElement).append('<svg class="i-peters" id="Icons" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><defs><style>.cls-1{fill:#45413c;opacity:0.15;}.cls-2{fill:#ff6242;}.cls-3{fill:#ff866e;}.cls-4{fill:none;stroke:#45413c;stroke-linecap:round;stroke-linejoin:round;}</style></defs><title></title><ellipse id="_Ellipse_" data-name="&lt;Ellipse&gt;" class="cls-1" cx="24" cy="44.18" rx="8.48" ry="1.82"/><path class="cls-2" d="M25.4,2.5H22.6c-1.86,0-3.34,1.18-3.23,2.57L21,26.32c.09,1.18,1.4,2.11,3,2.11s2.88-.93,3-2.11L28.63,5.07C28.74,3.68,27.26,2.5,25.4,2.5Z"/><path id="_Path_" data-name="&lt;Path&gt;" class="cls-3" d="M19.56,7.48a3.31,3.31,0,0,1,3-1.6h2.8a3.31,3.31,0,0,1,3,1.6l.19-2.41c.11-1.39-1.37-2.57-3.23-2.57H22.6c-1.86,0-3.34,1.18-3.23,2.57Z"/><path class="cls-4" d="M25.4,2.5H22.6c-1.86,0-3.34,1.18-3.23,2.57L21,26.32c.09,1.18,1.4,2.11,3,2.11s2.88-.93,3-2.11L28.63,5.07C28.74,3.68,27.26,2.5,25.4,2.5Z"/><circle id="_Path_2" data-name="&lt;Path&gt;" class="cls-2" cx="24" cy="35.24" r="3.65"/><path id="_Path_3" data-name="&lt;Path&gt;" class="cls-3" d="M24,33.93A3.58,3.58,0,0,1,27.57,36a3.94,3.94,0,0,0,.08-.77,3.65,3.65,0,1,0-7.3,0,3.94,3.94,0,0,0,.08.77A3.58,3.58,0,0,1,24,33.93Z"/><circle id="_Path_4" data-name="&lt;Path&gt;" class="cls-4" cx="24" cy="35.24" r="3.65"/></svg>')
                    $(currentElement).attr("title",$('#textComment').val());
                    $(currentElement).find("svg[id='Icons'] title").text($('#textComment').val());
                }
              else
              $(currentElement).find("svg[id='Icons']").remove();
              $(currentElement).attr("title",$('#textComment').val());
              $(currentElement).find("svg[id='Icons'] title").text($('#textComment').val());
             },
             async:false,
	    });
	};
});