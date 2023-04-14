var group_d;
var clr ;
var gc ;
var desc ;
var group;

$("select[name=Type-group]").change (function(){
    group = $('#group-color').val()[0];
    if (group == 0){
        group = undefined;
    }
    else{
        console.log(group)
        console.log(colors[group-1][0],colors[group-1][1]);
        clr = colors[group-1][1];
        gc = Number(colors[group-1][0]);
        desc = colors[group-1][2];
    }
});

count_group_refresh=$("#Table_5000_simulator, #Table_7000_simulator").find('label:contains("Refresh/Check")').length+1;
tmp_wcrew_id_one=-1;
td_prev=null;
$("td[name=Main-td-select]").on ('click', function() { // Добавление выбранной цветовой группы
    if ($(this).find('div[class*="test-flex"]').length==0) return;
    var wcrew_id = 0;
    var num = 0;
    var td = $(this); // указатель на td чтобы было удобнее читать

    td.children('div').each(function(){
        wcrew_id = this.id;
        num = Number(wcrew_id);
        console.log(num)
        });

    if (group === undefined){
        // Если цветовая группа не выбранна
        console.log('Group not change!')
    }
    else if ( group == 1) { // ----------------------------Сценарий для группы Refresh/Check---------------------------------------

        let cell = event.target.parentNode;
        if (cell.tagName.toLowerCase() != 'td'){
            return;
            }

        let i = cell.parentNode.rowIndex;
        let z = cell.parentNode.rowIndex + 1;
        let j = cell.cellIndex;
        if (!td.find('label:contains("Refresh/Check")').length)
        {
        td.css('background',clr);
        if (td.find('label').length==0)
            td.append('<label id="color-label" name="Refresh/Check">'+desc+ ' № -' + '</label>');
        else
            td.children('label').replaceWith('<label id="color-label" name="Refresh/Check">'+desc+ ' № -' + '</label>')
        td.find("div[class='test-flex']").attr('name',gc);
        if (($("#Table_5000_simulator, #Table_7000_simulator").find('label:contains("Refresh/Check")').length) % 2===0)
          {
          $.ajax({ // Update пары Refresh в базе Аккорд
                    url: 'upd_color_for_refresh_check' +'/'+ tmp_wcrew_id_one +'/'+ num + '/' + ($("#Table_5000_simulator, #Table_7000_simulator").find('label:contains("Refresh/Check")').length)/2
                    +'/'+ index_select_database,
                        success: function(data){
                        number_Ref_Check=(Math.ceil(($("#Table_5000_simulator, #Table_7000_simulator").find('label:contains("Refresh/Check")').length)/2));
                        $('label[id=color-label]:contains("Refresh/Check")').each(function(){
                        current_n=Number($(this).text().replace(/[^0-9]/gi,''))+1;
                        number_Ref_Check= current_n > number_Ref_Check ? current_n : number_Ref_Check;
                        });
                        console.log('Запись Refresh pair успешно! Номер: ' + ($("#Table_5000_simulator, #Table_7000_simulator").find('label:contains("Refresh/Check")').length)/2);

                        $.ajax({ // Апдейт типа тренажера в базе Аккорд
                            url: 'upd_color' +'/'+ gc +'/'+ num +'/'+index_select_database,
                            success: function(data){
                                td_prev.find('label[id="color-label"]').replaceWith('<label id="color-label" name="Refresh/Check">'+desc+ ' № ' + number_Ref_Check  + '</label>')
                                console.log('UPD is Done!' + wcrew_id);
                                set_tcc_id_for_all_people($('td div[class*="test-flex"][id='+num+']'));
                                set_ppls_for_all_people($('td div[class*="test-flex"][id='+num+']'), 'ППЧЛЭ 3.1.1.');
                             },
                            error: function(){ console.log("Error update field Refresh group! ");},
                            async: false,
                        });
                        $.ajax({ // Апдейт типа тренажера в базе Аккорд
                            url: 'upd_color' +'/'+ gc +'/'+ tmp_wcrew_id_one + '/' + index_select_database,
                            success: function(data){
                                td.find('label[id="color-label"]').replaceWith('<label id="color-label" name="Refresh/Check">'+desc+ ' № ' + number_Ref_Check  + '</label>')
                                console.log('UPD is Done!' + tmp_wcrew_id_one);
                                set_tcc_id_for_all_people($('td div[class*="test-flex"][id='+tmp_wcrew_id_one+']'));
                                set_ppls_for_all_people($('td div[class*="test-flex"][id='+tmp_wcrew_id_one+']'), 'ППЧЛЭ 3.1.1.');
                             },
                            error: function(){ console.log("Error update field Refresh group! ");},
                            async: false,
                        });
                        div_first_Refresh=td.closest("tbody").find('label:contains("Refresh/Check")').filter(function () { return $(this).text().replace(/[^0-9]/gi,'')==td.find('label').text().replace(/[^0-9]/gi,'') }).first()
                                                .closest("td").find('div[class*="test-flex"]');
                        set_ppls_for_all_people(div_first_Refresh, 'ППЧЛЭ 3.1.2.');
                    },
                    error: function(){
                        td.css('background','white');
                        td_prev.css('background','white');
                        td.find('label[id="color-label"]').remove();
                        td_prev.find('label[id="color-label"]').remove();
                    console.log("Error update PAIR Refresh group!");
                    alert("Не возможно в данные позиции установить Refresh/Check. \nОбновите страницу, возможно цветовая группа уже установлена.");
                    },
                    async:false,
                });
          }
          tmp_wcrew_id_one=num;
          td_prev=td
        }

    }

    else if(td.children('label').length > 0 && group == 43){ // ----------------------------Для удаления цветовой группы---------------------------------
            td.children('label').each(function(){

                td.css('background',clr);
                td.find("div[class='test-flex']").attr('name',gc);
                set_tcc_id_for_all_people(td); //т.к. при "удалении" gc=43, то views функция при установке в бд ttc_id запишет null
                if (td.find('label:contains("Refresh/Check")').length!=0 && td.children('label').text().replace(/[^0-9]/gi,'')!= '' && group == 43)
                {   //              ---------------------------------сценарий для удаленя пары Refresh/Check-ов---------------------------------
                    console.log("PARSE INT lable: "+ td.children('label').text().replace(/[^0-9]/gi,''));
                    next_find_td=td.closest("tbody").find('label:contains("Refresh/Check")').filter(function () { return $(this).text().replace(/[^0-9]/gi,'')==td.find('label').text().replace(/[^0-9]/gi,'') });
                    next_find_td.closest("td").css('background',clr);
                    num_second_wcrew_id = $(next_find_td).closest("td").children('div[class*="test-flex"][id!="'+num+'"]').attr('id');
                    $.ajax({ //
                    url: 'delete_pair_refresh_group/'+num+'/'+num_second_wcrew_id+'/'+index_select_database,
                    success: function(data){
                        Refresh_pair = td.closest("tbody").find('label:contains("Refresh/Check")').filter(function () { return $(this).text().replace(/[^0-9]/gi,'')==td.find('label').text().replace(/[^0-9]/gi,'') }) ;
                        remove_ppls_for_all_people($(Refresh_pair).first().closest("td").find('div[class*="test-flex"]'), 'ППЧЛЭ 3.1.1.');
                        remove_ppls_for_all_people($(Refresh_pair).first().closest("td").find('div[class*="test-flex"]'), 'ППЧЛЭ 3.1.2.');
                        remove_ppls_for_all_people($(Refresh_pair).last().closest("td").find('div[class*="test-flex"]'), 'ППЧЛЭ 3.1.1.');
                        $(next_find_td).closest("td").children('div[class*="test-flex"][id!="'+num+'"]').attr('name',gc);
                        console.log('id second refresh: ' + num_second_wcrew_id);
                        next_find_td.remove();
                        $.ajax({ //
                        url: 'upd_color' +'/'+ gc +'/'+ num_second_wcrew_id +'/'+index_select_database,
                        success: function(data){
                            console.log('Delete color the second Refresh is Done! id_wcrew:' + num_second_wcrew_id);
                            set_tcc_id_for_all_people($('td div[class*="test-flex"][id='+ num_second_wcrew_id +']'));
                        },
                        error: function(){ console.log("Ошибка удаления (43 группа) второго от выбранного Refresh/Check не произошло.\nwcrew_id: " + num_second_wcrew_id);},
                        async: false,
                        });
                            console.log('Success delete Refresh-pair from table! \nfirst: '+num +' second:' + num_second_wcrew_id);

                    },
                    error: function(){
                        alert("Ошибка удаления пары Refresh/Check");
                        console.log("Ошибка удаления пары Refresh/Check \n wcrew_id1: "+num+"  wcrew_id2:"+num_second_wcrew_id);},
                        async: false,
                    });
                }
                $(this).replaceWith('<label id="color-label">' + desc + '</label>');
            });


            $.ajax({ // Апдейт типа тренажера в базе Аккорд
                url: 'upd_color' +'/'+ gc +'/'+ num + '/'+index_select_database,
                success: function(data){
                    console.log('Delete color is Done!' + wcrew_id);
                },
                error: function(){ console.log("Error");},
            });
           }

    else{
        if (group != 43 && td.find("div[class='test-flex']").attr('name')!="1")   // ------------------------------------------------Установка иных цветовых групп------------------------------------------------------
        {
                $.ajax({ // Апдейт типа тренажера в базе Аккорд
                    url: 'upd_color' +'/'+ gc +'/'+ num +'/'+index_select_database,
                    success: function(data){
                        console.log('UPD is Done!' + wcrew_id);
                        console.log(group, clr, desc);
                        td.css('background',clr);
                        console.log(td.index());

                        if (td.children('label[id="color-label"]').length) {
                        // установка имени цветовой группы и поля 'name' для сессии
                            td.children('label').replaceWith('<label id="color-label">' + desc + '</label>');
                            td.find("div[class='test-flex']").attr('name',gc);
                            set_tcc_id_for_all_people(td);   // Назначение задания каждому из проверяемых (использовать только после присвоения name-цвета сессии)
                        }
                        else{
//                            td.is('#color-label');
                        // установка имени цветовой группы и поля 'name' для сессии
                             td.append('<label id="color-label">' + desc + '</label>');
                            td.find("div[class='test-flex']").attr('name',gc);
                            set_tcc_id_for_all_people(td);
                         }
                        if ( gc == 68 || gc == 75) //Refresh
                        {
                            remove_ppls_for_all_people(td.find("div[class='test-flex']"),'ППЧЛЭ 3.1.2.');
                            set_ppls_for_all_people(td.find("div[class='test-flex']"),'ППЧЛЭ 3.1.1.'); // Для tvs 737 и 777 ППЧЛЭ под Refresh
                            td.children('label[id="color-label"][name!="Refresh"]').replaceWith('<label id="color-label" name="Refresh">Refresh №'+$('tbody div[class="test-flex"][name='+gc+']').length+'</label>');
                        }
                        if ( gc == 69 || gc == 76) //Check
                        {
                            remove_ppls_for_all_people(td.find("div[class='test-flex']"),'ППЧЛЭ 3.1.1.');
                            set_ppls_for_all_people(td.find("div[class='test-flex']"),'ППЧЛЭ 3.1.2.'); // Для tvs 737 и 777 ППЧЛЭ под Check
                            td.children('label[id="color-label"][name!="Check"]').replaceWith('<label id="color-label" name="Check">Check №'+$('tbody div[class="test-flex"][name='+gc+']').length+'</label>');
                        }
                    },
                    error: function(){
                        alert("Цветовая группа не устанавливается. \nОшибка запроса!");
                        console.log("Одиночная цветовая группа не устанавливается. \nОшибка запроса связанная с wcrew_id: "+ num);
                    },
                });

            }
         if (td.find("div[class='test-flex']").attr('name')=="1")
                alert("Сначала необходимо удалить Refresh/Check!");
        }
    $('label[id="color-label"]').css({'font-weight':'bold'});
    find_and_set_marker_of_missing_crew();
  });

function set_tcc_id_for_all_people(object_td)
{
    object_td.find('[class*=people][name!="instructor"]').each(function (){
        //alert($(this).text()+"ttc_id");
        delete_return_task_for_people(this, true); // Функция расположена в Search_people.js
                                                   // (true - установить назначение проверяемого в соотв. с name сессии)
    });
}

function set_ppls_for_all_people(object_div, ppls)
{
    object_div.find('[class*=people][name!="instructor"]').each(function () {
    id_pilot=$(this).attr('id').split('/');
    $.ajax({ //
             url: 'write_ppls_for_pilot/'+ id_pilot[0]+'/'+ 0 + '/' + id_pilot[2]+'/'+ object_div.attr('id')+ '/' +$('#type_at').val()+'/' + ppls +'/'
             +index_select_database,
             success: function(){
             console.log("Запись "+ppls+". на wcrew_main="+ object_div.attr('id'));
                 },
             async:false,
            });
    });
}

function remove_ppls_for_all_people(object_div, ppls)
{
    font=object_div.find('font[id="Label_PPLS"]');
    font.text(font.text().replace(ppls,''));
    font.attr('title', font.text().replace(ppls,''));
    object_div.find('[class*=people][name!="instructor"]').each(function () {
    id_pilot=$(this).attr('id').split('/');
    $.ajax({ //
             url: 'remove_ppls_for_pilot/'+ id_pilot[0]+'/'+ 0 + '/' + id_pilot[2]+'/'+ object_div.attr('id')+ '/' +$('#type_at').val()+'/' + ppls +'/'
             +index_select_database,
             success: function(){
                    console.log("Удален "+ppls+". на wcrew_main="+ object_div.attr('id'));
                 },
                async:false,
            });
    });
}


