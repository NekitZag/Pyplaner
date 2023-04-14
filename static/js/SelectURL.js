index_select_database=null;  // 0-static; 1-main_db;
colors=null;
$.ajax({
url: 'create_global_colors/1',
success:function(data)
{colors=data['colors'];},
});
$(document).ready( function() {
    var now=localStorage.getItem("select_date") ? new Date(localStorage.getItem("select_date")) : new Date();
    var month = (now.getMonth() + 1);
    var day = now.getDate();
    if (month < 10)
        month = "0" + month;
    var today = now.getFullYear() + '-' + month;
    var aircraft = $('#type_at').val();


    document.querySelector('input[name$="date_send"]').value = today;
    $('#type_at option[number_menu="'+localStorage.getItem("select_type_aircraft")+'"]').attr("selected", "selected");
     $('#select_data_base_of_project option[value="'+localStorage.getItem("select_data_base")+'"]').attr("selected", "selected");
    index_select_database=$('#select_data_base_of_project').val();
    $('nav div[class="nav-wrapper"]').attr('style',(index_select_database==0?"background-color: #4f6f55":""));
    $('ul[class*="tabs"]').attr('style',(index_select_database==0?"background-color: #8eae94":""));
    $('div[class="layout sticky-layout"]').attr('style',(index_select_database==0?"background-color: #8eae94":""));
    $.ajax({
        url: 'get_info_database/'+index_select_database,
        success: function(data){ $('#info_data_base').text(data["db_info"][0]); },
        async:false,
    });
    Show_table_and_employees();
    });

    $('input[name=date_send]').change(function(){
        Show_table_and_employees();
        localStorage.setItem("select_date",$(this).val());
    });

    $("select[name=Type-AT]").change (function(){
    Show_table_and_employees();
    if ($('#type_at').val()!="320")
        location.href = "#followers";
    localStorage.setItem("select_type_aircraft", $('#type_at option:selected').attr('number_menu'));
    });

    $("#main_display_table a[class*='white-text']").click(function(){
        if(!$(this).hasClass('active'))
            setTimeout(() => {Show_table_and_employees(false); console.log("qwertyTimeoutisnone");}, 100);// sap pilot 96620
    });

    function Show_table_and_employees(update_list_person=true)
    {
       $('#loader').css('display',update_list_person?'block':'none');
       $('#Table_7000_simulator').empty();
       $('#Table_5000_simulator').empty();
       var aircraft = $('#type_at').val();
       if (aircraft=="320" && $('#type_at option:selected').attr('PP')==null)
            load_7000_and_5000_sim();
       else
            load_some_type_sim();
       $('label[id="color-label"]').css({'font-weight':'bold'});
        var group = $('#type_group').val();
        var date = new Date($('input[name=date_send]').val());
        month = date.getMonth()+1;
        year = date.getFullYear();
        //console.log($(this).val())

//        $.ajax({ //Обновление таблицы
//            url: 'show_table_of_schedule/'+aircraft+'/'+$('#tabs .active').text()+'/'+month+'/'+ year+'/'+index_select_database,
//            success: function (data) {
//             $('#Table_'+$('#tabs .active').text()+'_simulator').html($(data.html));
                $.ajax({ // Обновление таблицы цветов
                     url: 'color_group/' + aircraft + '/' + index_select_database,
                     success: function (data) {
                     $('#group-color').replaceWith($(data.html));
                     $("#followers").trigger('DOMSubtreeModified'); // Счетчик цветов в файле "count_simulator.js"
                     $.ajax({ // Обновление номеров Refresh group
                     url: 'show_refresh_number_group/' +month+'/'+ year+'/'+ index_select_database,
                     success:function(data){

                     data['mass_refresh'].forEach(element_refresh=>{
                                  $('#Table_'+$('#tabs .active').text()+'_simulator tbody [id="'+element_refresh[0]+'"]').closest('td').children('label')
                                                                            .append(' № ' + element_refresh[1]);
                                });
                            },
                            async:false,
                     });
                    hide_refr(aircraft);
                     if (update_list_person) // Если функция вызвана с обновлением списка людей
                     {
                        $.ajax({ // Обновление списка людей
                            url: 'display_pilots_and_instructors/' +  aircraft + '/' + group +'/'+$('input[name=date_send]').val() + '/' + month + '/' + year+ '/' + index_select_database,
                        success: function (data) {
                          $('#refresher').replaceWith($(data.html));
                          Listening_change(); //Подключение функции обработчика фильтра поиска людей и Drag&Drop

                        },
                        async: false,
                        });
                       if (group==0)
                        {
                           $.ajax({
                            url: 'display_all_instructors/'+ aircraft + '/' + month + '/' + year+ '/' + index_select_database,
                            success: function(data)
                            {
                             $('#instructors').replaceWith($(data.html).find('#instructors'));
                             Listening_change();

                            },
                            async: false,
                           });
                        }
                     }
                     $('#pilots div[class*="grid_container"]').empty();      // очистка проставленных дней пилотов их для обновления
                     $('#instructors div[class*="grid_container"]').empty();    // очистка проставленных дней инструкторов их для обновления
                     $('#refresher div').each(function(){ //запись дней посещения из таблицы для каждого  пилота и инструктора

                         if ($(this).attr('id')!=null)
                         {
                             pilots_element_day=[];
                             mass_person=$(this).attr('name')!=null ? $('#main_display_table tr [id="'+$(this).attr('id')+'"][name="'+$(this).attr('name')+'"]'):$('#main_display_table tr [id="'+$(this).attr('id')+'"]:not([name])');

                             mass_person.each(function(){
                                                          pilots_element_day.push($(this).closest('tr').prevAll().length+1);
                                                               });
                             for (i=0; i<pilots_element_day.length; i++)
                                $(this).find('.grid_container').append("<div class=box-"+($('.grid_container div').length+1)+">"+pilots_element_day[i]+"</div>");
                                //console.log($(this).find('.grid_container').attr('id'));
                         }
                       });
                     if (aircraft=="330" || aircraft=="350") // Дополнение дней инст. для 330/350
                     $.ajax({
                        url:'find_days_of_instructors_330_350/'+(aircraft=="330"?"350":"330")+'/'+$('input[name=date_send]').val()+'/'+index_select_database,
                        success: function(data){
                            $('#instructors div').each(function(){ //запись дней посещения из таблицы для каждого инструктора
                             if ($(this).attr('id')!=null)
                             {
                                for (i=0;i<data['instructor_days'].length;i++)
                                {
                                    if (data['instructor_days'][i][0]==$(this).attr('id').split('/')[0])
                                    for (j=0;j<data['instructor_days'][i][1].length;j++)
                                        $(this).find('.grid_container').append("<div class=box-"+($(this).find('.grid_container div').length+1)+">"+data['instructor_days'][i][1][j]+"</div>");
                                }
                             }
                            });
                        },
                        async:false,
                      });
                    },
                    error: function () {$("#loader").attr("style","display: none");},
                 });
         find_and_set_marker_of_missing_crew();
//            }
//         });
    };

//-------------------------------------------Выбор группы инструкторов-------------------------------------------------
   $("select[name=Groups]").change (function(){
        var aircraft = $('#type_at').val();
        console.log(aircraft);
        var group = $(this).val();
        console.log(group);
        $('#loader').css('display','block');
        $.ajax({ //Обновление списка людей
            url: 'display_pilots_and_instructors/' + aircraft + '/' +group+'/'+$('input[name=date_send]').val() + '/' + month + '/' + year+ '/' + index_select_database,
        success: function (data) {

          $('#refresher').replaceWith($(data.html));
          if (group==0)
            {
               $.ajax({
                url: 'display_all_instructors/'+ aircraft + '/' + month + '/' + year + '/' + index_select_database,
                success: function(data)
                {

                 $('#instructors').replaceWith($(data.html).find('#instructors'));

                },
                async: false,
               });
            }
          Listening_change(); //Подключение функции обработчика фильтра поиска людей и Drag&Drop
          $('#refresher div').each(function(){ //запись дней посещения из таблицы для каждого ???пилота???      .parentNode.parentNode.rowIndex
             if ($(this).attr('id')!=null)
             {
                 pilots_element_day=[];
                 mass_person=$(this).attr('name')!=null ? $('#main_display_table tr [id="'+$(this).attr('id')+'"][name="'+$(this).attr('name')+'"]'):$('#main_display_table tr [id="'+$(this).attr('id')+'"]:not([name]');

                 mass_person.each(function(){
                                              pilots_element_day.push($(this).closest('tr').prevAll().length+1);
                                                   });
                 for (i=0; i<pilots_element_day.length; i++)
                    $(this).find('.grid_container').append("<div class=box-"+($('.grid_container div').length+1)+">"+pilots_element_day[i]+"</div>");
                    //console.log($(this).find('.grid_container').attr('id'));
             }
            });
            if (aircraft=="330" || aircraft=="350") // Дополнение дней инструкторам для 330/350
                     $.ajax({
                        url:'find_days_of_instructors_330_350/'+(aircraft=="330"?"350":"330")+'/'+$('input[name=date_send]').val()+'/'+index_select_database,
                        success: function(data){
                            $('#instructors div').each(function(){ //запись дней посещения из таблицы для каждого инструктора
                             if ($(this).attr('id')!=null)
                             {
                                for (i=0;i<data['instructor_days'].length;i++)
                                {
                                    if (data['instructor_days'][i][0]==$(this).attr('id').split('/')[0])
                                    for (j=0;j<data['instructor_days'][i][1].length;j++)
                                        $(this).find('.grid_container').append("<div class=box-"+($(this).find('.grid_container div').length+1)+">"+data['instructor_days'][i][1][j]+"</div>");
                                }
                             }
                            });
                        },
                        async:false,
                      });
        }
      });
    });

//-------------------------------Переход на сформированную страницу добавления пилотов---------------------------------------
    $("#redirect_people_adding").click( function(){
        $.ajax({ // Апдейт типа тренажера в базе Аккорд
          url: 'add_people/' + $('#type_at').val() +'/'+ $('input[name=date_send]').val()+'/'+index_select_database,
          success: function(data){
          date_choice=$('input[name=date_send]').val();
          value_choice_tvs=$('#type_at').val()
          $('body').replaceWith($(data.html));
          console.log(date_choice);
          document.querySelector('input[name$="date_send_add_people"]').value=date_choice;
          document.querySelector('#type_at').value=value_choice_tvs;
          },
      });

    });

//-------------------------Таблицы для 320 типа самолета-----------------------------
 function load_7000_and_5000_sim (){
    var aircraft = $('#type_at').val();
    var date = new Date($('input[name=date_send]').val());
        month = date.getMonth()+1;
        year = date.getFullYear();
     $.ajax({ //Обновление таблицы
            url: 'show_table_of_schedule/'+aircraft+'/7000/'+month+'/'+ year+'/'+index_select_database,
            success: function (data) {
             $('#Table_7000_simulator').html($(data.html));
             $('#info_data_base').text(data["db_info"][0]);

             $.ajax({ //Обновление таблицы
                    url: 'show_table_of_schedule/'+aircraft+'/5000/'+month+'/'+ year+'/'+index_select_database,
                    success: function (data) {
                     $('#Table_5000_simulator').html($(data.html));
                     //hide_refr(aircraft);

                     },
                     async:false,
                     error: function(data) { alert(data.responseJSON.error);},
                });
             },
             async:false,
             error: function(data) { alert(data.responseJSON.error);},
             });
    };

//------------------------Таблица расписания для иных типов самолета------------------------------
    function load_some_type_sim(){
    var aircraft = $('#type_at').val();
    var date = new Date($('input[name=date_send]').val());
        month = date.getMonth()+1;
        year = date.getFullYear();
    PP_TRJ=$('#type_at option:selected').attr('PP');
    $.ajax({ //Обновление таблицы
        url: 'show_table_of_schedule/'+aircraft+'/'+(PP_TRJ!=null?PP_TRJ: 'null')+'/'+month+'/'+ year+'/'+index_select_database + (PP_TRJ!=null?'/ZA':''),
        success: function (data) {
             $('#Table_7000_simulator').html($(data.html));
             $('#info_data_base').text(data["db_info"][0]);
             //счетчик для Refresh и Check
             Check_count=1;
             Refresh_count=1;
             $('#Table_7000_simulator label[id="color-label"]').filter(function() {return $(this).text() === "Check";}).each(function () {
                $(this).text('Check №'+Check_count);
                Check_count+=1;
             });
             $('#Table_7000_simulator label[id="color-label"]').filter(function() {return $(this).text() === "Refresh";}).each(function () {
                $(this).text('Refresh №' + Refresh_count);
                Refresh_count+=1;
             });
             //hide_refr(aircraft);
         },
         async:false,
         error: function(data) { alert(data.responseJSON.error);},
         });
    };

//---------------------------Выбор БД со сменой интерфейса-------------------------------------------
$('#select_data_base_of_project').change(function(){ // Переключение баз данных
    select_db_val=$(this).val();
    //alert('Вы подключены к: '+ data['db_info'][0]);
    index_select_database=select_db_val; // Изменение индекса базы данных
    $('nav div[class="nav-wrapper"]').attr('style',(index_select_database==0?"background-color: #4f6f55":""));
    $('ul[class*="tabs"]').attr('style',(index_select_database==0?"background-color: #8eae94":""));
    $('div[class="layout sticky-layout"]').attr('style',(index_select_database==0?"background-color: #8eae94":""));
    localStorage.setItem("select_data_base", index_select_database);
    Show_table_and_employees();
    console.log(localStorage.getItem("select_data_base") );
});

//------------------Функция скрытия ненужных элементов для других самолетов--------------------------
function hide_refr(aircraft){
    if (aircraft == '737' || aircraft == '777' ){
        $('#group_refresh_check').css("display", "none");
        $('.preliminary').css("display","grid");
    }
    else{
        $('.preliminary').css("display","none");
    }
}

//---------------Динамическое выставление маркеров недостающего летного состава-----------------------
function find_and_set_marker_of_missing_crew(){
    $('#main_display_table td div[class="test-flex"][name="1"]').each(function(){
        if ($(this).find('div[class*="people"][name="instructor"]').length==0)
            {
                if ($(this).find("div[name='No_pilot'][post='INSTR']").length == 0)
                    {
                        var newdiv = document.createElement("div");
                        $(newdiv).attr('id','None/None/None');
                        $(newdiv).attr('name','No_pilot');
                        $(newdiv).attr('post','INSTR');
                        $(newdiv).html("ИНСТРУКТОР");
                        $(newdiv).attr('style',"background:red; color: white; font-weight: bolder; font-size: 15px; width: 100%; border-radius: 5px");
                        $(this).append(newdiv);
                    }
        }
        else
            $(this).find("div[name='No_pilot'][post='INSTR']").remove();
        if ($(this).find('div[class*="people"][name!="instructor"]').length<2)
        {
            if ($(this).find('div[class*="people"][id*="/10"][name!="instructor"]').length == 0)
                {
                    if ($(this).find("div[name='No_pilot'][post='KVS']").length == 0)
                    {
                        var newdiv = document.createElement("div");
                        $(newdiv).attr('id','None/None/None');
                        $(newdiv).attr('name','No_pilot');
                        $(newdiv).attr('post','KVS');
                        $(newdiv).html("KВС");
                        $(newdiv).attr('style',"background:red; color: white; font-weight: bolder; font-size: 15px; width: 100%; border-radius: 5px");
                        $(this).append(newdiv);
                    }
                }
                else
                    $(this).find("div[name='No_pilot'][post='KVS']").remove();

            if ($(this).find('div[class*="people"][id*="/20"][name!="instructor"]').length == 0)
                {
                    if ($(this).find("div[name='No_pilot'][post='2nd_pilot']").length == 0)
                    {
                        var newdiv = document.createElement("div");
                        $(newdiv).attr('id','None/None/None');
                        $(newdiv).attr('name','No_pilot');
                        $(newdiv).attr('post','2nd_pilot');
                        $(newdiv).html("2-й пилот");
                        $(newdiv).attr('style',"background:red; color: white; font-weight: bolder; font-size: 15px; width: 100%; border-radius: 5px");
                        $(this).append(newdiv);
                    }
                }
                else
                    $(this).find("div[name='No_pilot'][post='2nd_pilot']").remove();
        }
        else
            $(this).find("div[name='No_pilot'][post!='INSTR']").remove();
    });
    $('#main_display_table td div[class="test-flex"][name!="1"]').each(function(){
        $(this).find("div[name='No_pilot']").remove();
    });
}

