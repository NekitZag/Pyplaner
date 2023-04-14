// var divElement = document.getElementById('Lisening_change')
// alert('Прогрузился');
// function HideInstructors(){
//    $('#instructors').hide();
//    $('#pilots').show();
// };
// function HidePilots(){
//    $('#instructors').show();
//    $('#pilots').hide();
// };
name_month=["Янв", "Фев","Мар","Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"];
 //alert('Прогрузился');
$('#main_display_table').on('click','#myPlot', function(){$(this).empty(); });

//Наряд по клику на человека
$(document).on('click','.people', function(){
    $('#context-menu').removeClass( ['visible' ] );
    $('#myPlot').removeClass(['hidden']);
    const point_position = $("#display_table_context_menu").position();
    const point_position_global = $("#display_table_context_menu").offset();
    const currentElement = document.elementFromPoint(parseInt($('#context-menu').css('left'))-1,
    parseInt($('#context-menu').css('top'))-1);
    select_person=$(this);
    id_select_person=$(this).attr('id').split('/')[0];
    if (!parseInt(id_select_person)) return;

    name_select_person=$(this).clone().children().remove().end().text();
    var date = new Date($('input[name=date_send]').val())
    month = date.getMonth()+1;
    year = date.getFullYear();
    var name_person=$(this).text();
    $.ajax({ // Отображение наряда на месяц
          url: 'info_otpusklist/'+id_select_person+'/'+month+'/'+year+'/' + index_select_database,
          success: function(date){
            $('#myPlot').empty();
            var style = document.createElement('style');
            var p_name = document.createElement('p');
            var bool_select_day = true;
            p_name.innerHTML= name_select_person;
            p_name.style="font-weight:bold";
            //$(p_name).append($(select_person).find("img"));
            $('#myPlot').append(p_name);
            style.type = 'text/css';
            style.innerHTML = '.width_cell_otpusk { width:45px; border: 1px solid black; text-align: center; }';
            document.getElementsByTagName('head')[0].appendChild(style);
            let thead  = document.createElement('thead');
             $('#myPlot').append(thead);
             $('#myPlot').append(document.createElement('tr'));
             $('#myPlot').append(document.createElement('tr'));
             $('#myPlot').append(document.createElement('tr'));
            for (i=0;i<date["mass_display_otpusk"].length;i++)
            {
                let new_tr = document.createElement('th');
                new_tr.innerHTML = date["mass_display_otpusk"][i][1];
                new_tr.classList='width_cell_otpusk';
                $('#myPlot thead').append(new_tr);
                new_td= document.createElement('td');
                new_td.className='width_cell_otpusk';
                $('#myPlot tr').eq(0).append(new_td);
                new_td= document.createElement('td');
                new_td.className='width_cell_otpusk';
                $('#myPlot tr').eq(1).append(new_td);
                new_td= document.createElement('td');
                new_td.className='width_cell_otpusk';
                $('#myPlot tr').eq(2).append(new_td);
            }
            for (i=0;i<date["mass_display_otpusk"].length;i++)
            { 
              for (x = 0; x < date["mass_display_otpusk"][i][0].length;x++){
                if ( date["mass_display_otpusk"][i][0][x] == 'ТВ')
                {
                  $('#myPlot tr').eq(0).find('td').eq(i).append("<br><svg xmlns='http://www.w3.org/2000/svg' width='24' height='32'><path fill='#3CAED6' d='M12 0s12 13.373 12 20-5.372 12-12 12c-6.627 0-12-5.373-12-12l12-20z'/><path fill='#63BFDE' d='M16.994 16c-1.108 0-2.006.898-2.006 2.007 0 1.107.897 2.005 2.006 2.005 1.107 0 2.006-.897 2.006-2.005 0-1.109-.898-2.007-2.006-2.007z'/><path fill='#369DC0' d='M13 31c-6.627 0-12-5.373-12-12 0-5.497 8.25-15.627 11.066-18.926l-.066-.074s-12 13.373-12 20 5.373 12 12 12c3.568 0 6.764-1.566 8.961-4.039-2.119 1.885-4.901 3.039-7.961 3.039z'/></svg></br>");
                }
                  if (date["mass_display_otpusk"][i][0][x] == 'ТС')
                {
                  $('#myPlot tr').eq(0).find('td').eq(i).append("<br><svg version='1.1' id='Layer_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' viewBox='0 0 495 495' style='enable-background:new 0 0 495 495;' xml:space='preserve'><g><path style='fill:#FFA733;' d='M379.942,243.25c25.956-6.124,55.431-10.323,90.093-11.689L327.52,65.275v116.812L379.942,243.25z'/><polygon style='fill:#FFC477;' points='327.52,65.275 277.462,123.681 327.52,182.086 	'/><path style='fill:#CC7400;' d='M247.5,298.705c38.989-21.303,77.98-42.606,132.442-55.455l-52.422-61.164l-50.058-58.405L197.44,30.315v242.271C214.881,280.879,231.191,289.792,247.5,298.705z'/><path style='fill:#EE8700;' d='M197.44,30.315L24.957,231.561c76.973,3.03,128.357,20.042,172.483,41.025V30.315z'/><path style='fill:#FFDE55;' d='M247.5,298.705c-16.309-8.914-32.619-17.826-50.06-26.119c-44.126-20.983-95.51-37.995-172.483-41.025c-8.037-0.316-16.342-0.486-24.957-0.486v233.61h495v-98.36C371.25,366.325,309.38,332.515,247.5,298.705z'/><path style='fill:#FFCD00;' d='M470.035,231.562c-34.662,1.365-64.137,5.565-90.093,11.689c-54.462,12.849-93.453,34.152-132.442,55.455c61.88,33.81,123.75,67.62,247.5,67.62v-135.25C486.382,231.075,478.074,231.245,470.035,231.562z'/></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g></svg></br>");
                }
              }
                  if (date["mass_display_otpusk"][i][5]==true)
                {
                    $('#myPlot tr').eq(0).find('td').eq(i).append("<br><svg width='44px' height='44px' viewBox='0 0 64 64' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' aria-hidden='true' role='img' class='iconify iconify--emojione' preserveAspectRatio='xMidYMid meet'><circle cx='32' cy='32' r='30' fill='#ffe8a6'></circle><g fill='#f4dc9f'><circle cx='50' cy='35.2' r='7'></circle><circle cx='18.1' cy='39' r='6'></circle><circle cx='24.2' cy='50' r='9'></circle><circle cx='24' cy='17.2' r='4'></circle><circle cx='37' cy='18.2' r='4'></circle><circle cx='12.1' cy='25.9' r='4'></circle><circle cx='39' cy='9.2' r='2'></circle><circle cx='8.1' cy='39' r='2'></circle><circle cx='52' cy='50' r='2'></circle><circle cx='25' cy='29.9' r='3'></circle><circle cx='15' cy='15.7' r='2'></circle><circle cx='46' cy='52.6' r='4'></circle><path d='M24.2 10.8c0 2.8 2.2 5 5 5s5-2.2 5-5s-2.2-5-5-5c-2.8-.1-5 2.2-5 5'></path></g></svg></br>");
                }
                for (j=0;j<date["mass_display_otpusk"][i][0].length;j++)
                {
                    $('#myPlot tr').eq(0).find('td').eq(i).append(date["mass_display_otpusk"][i][0][j]+ " <br> ");
                }

                if (date["mass_display_otpusk"][i][2]!=null)
                    $('#myPlot tr').eq(1).find('td').eq(i).append( date["mass_display_otpusk"][i][2]);
                if (date["mass_display_otpusk"][i][3]!=null)
                    $('#myPlot tr').eq(1).find('td').eq(i).append("-"+ date["mass_display_otpusk"][i][3]);
                if (date["mass_display_otpusk"][i][4]!=null)
                   $('#myPlot tr').eq(2).find('td').eq(i).append("<font color=Red>" + date["mass_display_otpusk"][i][4]);

                if ($('#posts[class*="active"],#followers[class*="active"]').find('tbody tr').eq(date["mass_display_otpusk"][i][1]-1).find('td').eq(0).attr('class')=='holiday' && i>6 && i<date["mass_display_otpusk"].length-7)
                    {//выходные
                        $('#myPlot th').eq(i).attr('style', "background-color: #ff6666");
                    }

                if ($(select_person).closest('tr').prevAll().length+1 == date["mass_display_otpusk"][i][1] && $(select_person).closest('table').length > 0 && bool_select_day && i>6)
                   {
                       $('#myPlot tr').eq(0).find('td').eq(i).attr('style', "background-color: LightSalmon");
                       $('#myPlot tr').eq(1).find('td').eq(i).attr('style', "background-color: LightSalmon");
                       $('#myPlot tr').eq(2).find('td').eq(i).attr('style', "background-color: LightSalmon");
                       bool_select_day=false;
                   }
                if ((i<=6 && date["days_off_pre_month"][date["days_off_pre_month"].length-7+i]!=0) || (i>=date["mass_display_otpusk"].length-7 && date["days_off_next_month"][i-(date["mass_display_otpusk"].length-7)]!=0))
                    {
                        $('#myPlot th').eq(i).attr('style', "background-color: #ff6666");
                    }


    //            if (date["mass_display_otpusk"][i][4]!=null)
    //            new_e.innerHTML+="<br>" + date["mass_display_otpusk"][i][4];
            }
//            new_e.className='width_cell_otpusk';
//            if (date["mass_display_otpusk"][i][5]==true)
//            {
//                new_e.innerHTML+= "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1920 1920'><style> .st0{fill:#fff}.st1{fill:none;stroke:#231f20;stroke-width:50;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10} </style> <path class='st0' d='M1294.4 1447.1c132.3 0 255.2-40.3 357.1-109.2-129.3 218.6-367.5 365.2-640 365.2-410.4 0-743-332.7-743-743.1s332.7-743 743-743c14.2 0 28.3.4 42.2 1.2-233 95-397.3 323.8-397.3 591 .1 352.2 285.7 637.9 638 637.9z' id='Layer_5'/>  <path class='st1' d='M1294.4 1447.1c-352.3 0-637.9-285.6-637.9-637.9 0-267.2 164.2-496 397.3-591-14-.8-28.1-1.2-42.2-1.2-410.4 0-743 332.7-743 743s332.7 743.1 743 743.1c272.4 0 510.6-146.6 640-365.2-102 68.9-224.9 109.2-357.2 109.2z' id='STROKES'/>  </svg>";
//            }
//            for (j=0;j<date["mass_display_otpusk"][i][0].length;j++)
//            {
//                new_e.innerHTML+=date["mass_display_otpusk"][i][0][j]+ " <br> ";
//            }
//
//            if (date["mass_display_otpusk"][i][2]!=null)
//            new_e.innerHTML+="<font color=Red>" + date["mass_display_otpusk"][i][2];
//            if (date["mass_display_otpusk"][i][3]!=null)
//            new_e.innerHTML+="<font color=Red>" +"-"+ date["mass_display_otpusk"][i][3];
////            if (date["mass_display_otpusk"][i][4]!=null)
////            new_e.innerHTML+="<br>" + date["mass_display_otpusk"][i][4];
//            $('#myPlot').append(new_e);

         }

});
});

//Отслеживание отпуска клавиши для вводимого текста-фильтра в элемент <input> для вкладки пилоты
$(document).on('keyup', "#filter_pilots" , function() {

            // Retrieve the input field text and reset the count to zero
            var filter = $(this).val(),

              count = 0;
            // Loop through the comment list,
            console.log(filter.toLowerCase()== "квс");
            $('#pilots div.people').each(function() {
              // If the list item does not contain the text phrase fade it out
              if ($(this).text().search(new RegExp(filter, "i")) < 0 && !(filter.toLowerCase()== "квс" && $(this).attr('id').split('/')[1]==3 && $(this).attr('id').split('/')[2]==10)) {
                $(this).hide();  // MY CHANGE

                // Show the list item if the phrase matches and increase the count by 1
              } else {
                $(this).show(); // MY CHANGE
                count++;
              }
              //if
           });
       });

// Отслеживание отпуска клавиши для вводимого текста-фильтра в элемент <input> для вкладки инструкторы
 $(document).on('keyup', "#filter_instructors", function() {

            // Retrieve the input field text and reset the count to zero
            var filter = $(this).val(),

              count = 0;
            // Loop through the comment list
            $('#instructors div.people').each(function() {
              // If the list item does not contain the text phrase fade it out
              if ($(this).text().search(new RegExp(filter, "i")) < 0) {
                $(this).hide();  // MY CHANGE

                // Show the list item if the phrase matches and increase the count by 1
              } else {
                $(this).show(); // MY CHANGE
                count++;
              }

           });
       });

//---------------------------------Удаление человека из таблицы----------------------------------------------
$("#delete_person_from_table").click(
    function(){
    $('#context-menu').removeClass(['visible' ]);
    const point_position = $("#delete_person_from_table").position();
    const point_position_global = $("#delete_person_from_table").offset();
    const currentElement = document.elementFromPoint(parseInt($('#context-menu').css('left'))-1,
    parseInt($('#context-menu').css('top'))-1);
    if (!currentElement.parentNode.classList.contains(`test-flex`) || !parseInt(currentElement.parentNode.id)) {return;}
    id_mass_pars = currentElement.id.split('/');
    if (!parseInt(id_mass_pars[0])) return;
    if (confirm('Удалить '+currentElement.textContent+' ?') )
       $.ajax({ // Удаление из сессии человека
          url: 'delete_person_from_table/'+currentElement.parentNode.id+'/'+id_mass_pars[0]+'/'+index_select_database,
          success: function(){
          find_del_obj= $('#refresher div[id="'+currentElement.id+'"]');
          if ($(currentElement).attr('name')!= null) find_del_obj.filter('[name="'+$(currentElement).attr('name')+'"]');
         find_del_obj.each(function(){    //Удаление ячейки информирующего дня из списка пилотов и инструкторов
                    $(this).find('.grid_container div').each(function(){
                        if ($(this).text() == $(currentElement).closest('tr').prevAll().length+1)
                        {
                            $(this).remove();
                            return false;
                        }
                    });
            });
          if ($(currentElement).closest('td').find('label:contains("Refresh/Check")').length!=0 && $(currentElement).attr('Name')!= 'instructor')  // Если удаление пилота происходит на Refresh/Check
             {
                Refresh_parent_element=$(currentElement).closest("tbody").find('label:contains("Refresh/Check")').filter(function () { return $(this).text().replace(/[^0-9]/gi,'')==$(currentElement).closest('td').find('label').text().replace(/[^0-9]/gi,'') })
                   .closest("td").find('div[class*="test-flex"][id!="'+$(currentElement).closest('div[class*="test-flex"]').attr('id')+'"]');
                $.ajax({ // Удаление из сессии человека
                          url: 'delete_person_from_table/'+Refresh_parent_element.attr('id')+'/'+id_mass_pars[0]+'/'+index_select_database,
                          success: function(){
                                find_del_obj= $('#refresher div[id="'+currentElement.id+'"]');
                                if ($(currentElement).attr('name')!= null) find_del_obj.filter('[name="'+$(currentElement).attr('name')+'"]');
                                find_del_obj.each(function(){    // Удаление ячейки информирующего дня из списка пилотов и инструкторов
                                $(this).find('.grid_container div').each(function(){
                                    if ($(this).text() == $(Refresh_parent_element).closest('tr').prevAll().length+1)
                                    {
                                        $(this).remove();
                                        return false;
                                    }
                                    });
                                });
                                Ref_el=Refresh_parent_element.find('div[id="'+currentElement.id+'"]');
                                if (Refresh_parent_element.find('div[class*="people"]').length==1)
                                {
                                    $(Ref_el).attr('id','None/None/None');
                                    $(Ref_el).text("None");
                                    $(Ref_el).attr("style","");
                                }
                                else
                                    Ref_el.remove();
                          },
                          error: function(){ alert("Ошибка при удалении персонала со второго Refresh/Check-a!");},
                          async:false
                     });
             }
             count_element=currentElement.parentNode.querySelectorAll('div .people').length;
              console.log(count_element)
              if (count_element==1)
              {
                  currentElement.id='None/None/None';
                  currentElement.innerHTML="None";
                  currentElement.style="";
              }
                  else
                  currentElement.remove();
              find_and_set_marker_of_missing_crew();
            },
            error: function(){ alert("Ошибка при удалении записи!");},
            async:false
          });

    }

);

// Удаление задания человека из сессии
$("#delete_task_for_people").click( function(){
    $('#context-menu').removeClass(['visible' ]);
    const currentElement = document.elementFromPoint(parseInt($('#context-menu').css('left'))-1,
                                                        parseInt($('#context-menu').css('top'))-1);
    delete_return_task_for_people(currentElement);
});

function delete_return_task_for_people (object, set_ttc_id=false){ //Функция исп. так же в Select_Group.js
    if (!object.parentNode.classList.contains(`test-flex`) || !parseInt(object.parentNode.id)) {return;}
    ttc_id=($(object.parentNode).attr('name')=="None")?0:$(object.parentNode).attr('name');
    if (ttc_id==0) return;
    if ($(object).find('label:contains("Не назначен!")').length==0 && !set_ttc_id) ttc_id=0;
    $.ajax({
    url: 'delete_return_task_for_people/'+ object.parentNode.id+'/'+ object.id.split('/')[0]+
    '/'+ ttc_id+'/'+index_select_database,
    success:function(){
        if (ttc_id==0)
        $(object).append("<label style='color:red;'>Не назначен!</label>");
        else
         $(object).find('label:contains("Не назначен!")').remove();
    },
    async:false,
    });
};

//Замена надписи checkbox
$('#pilots_tabs a').click(function () {
    $('#checkbox-hidden-active-pilots span').text($(this).attr('name'));
});

// Скрытие-раскрытие пилотов поставленных на сессии
$(document).on('click','#checkbox_hide_pilots_in_session',function(){
   if (this.checked)
        {
        $('#pilots div').each(function(){
            if ($(this).attr('id')!=null && $(this).find('.grid_container div').length != 0)
                $(this).hide();
        });
        $('#instructors div').each(function(){
            if ($(this).attr('id')!=null && $(this).find('.grid_container div').length != 0)
                $(this).hide();
        });
        }
    else
     {
     $('#pilots div').each(function(){
        $(this).show();
     })
     $('#instructors div').each(function(){
        $(this).show();
     })
     }
});


function Listening_change(){
      //Инициализация родительских классов элементов пилотов и инструкторов
      InstructorsListElement = document.querySelector('.instructors');
      PilotsListElement = document.querySelector('.pilots');

      //Инициализация списка всех элементов пилотов и инструкторов
      const instructorElements = InstructorsListElement.querySelectorAll('.people');
      const pilotsElements= PilotsListElement.querySelectorAll('.people');

      // Перебираем все элементы списка и открываем им свойства перемещения
      for (const inst of instructorElements) {
        inst.draggable = true;
      }

      for (const pilo of pilotsElements) {
        pilo.draggable = true;
      }

      //Начало действия перемещения инструкторов
      InstructorsListElement.addEventListener(`dragstart`, (evt) => {
        evt.target.classList.add(`selected`);
      });

      //Начало действия перемещения пилотов
      PilotsListElement.addEventListener(`dragstart`, (evt) => {
          evt.target.classList.add(`selected`);
      });

      //Конец действия перемещения инструкторов
      InstructorsListElement.addEventListener(`dragend`, (evt) => {
          const activeElement = InstructorsListElement.querySelector(`.selected`);
          currentElement = document.elementFromPoint(event.clientX, event.clientY);
          evt.target.classList.remove(`selected`);
          console.log(currentElement.parentNode.classList);
           if (!(currentElement.parentNode.classList.contains(`test-flex`) || currentElement.classList.contains(`test-flex`) ||
          $(currentElement).attr('Name')=="No_pilot")) {return;}
          if (!currentElement.classList.contains('people'))
            {
                currentElement=$(currentElement).attr('Name')=="No_pilot"?$(currentElement).siblings('[class*="people"]')[0]:currentElement.getElementsByClassName('people')[0];
            }
          //currentElement.parentNode.replaceChild(activeElement,currentElement);
           let cell = currentElement.parentNode.parentNode;
          if (cell.tagName.toLowerCase() != 'td')
            return;
          let j = cell.cellIndex;
          let date = new Date($('input[name=date_send]').val());
           month = date.getMonth()+1;
           year = date.getFullYear();
            id_pilot=activeElement.id.split('/');
        $.ajax({ // проверка "пересечений"
          url: '/wcrew_add_check/'+ id_pilot[0]+'/'+ currentElement.parentNode.id+'/' + index_select_database,
          success: function(data){
          console.log(data['message_add_check'][0][0])
          if (data['message_add_check'][0][0]!=null)
            if (!confirm('У инструктора '+activeElement.textContent+'  '+ data['message_add_check'][0][0]+
             ' c '+data['message_add_check'][0][1]+' по '+data['message_add_check'][0][2]+' все равно добавить?'))
                return false;
            $.ajax({ // Запись людей в таблицу аккорд
              url: '/'+'write_db' +'/'+id_pilot[0]+'/'+ 3 + '/'+ (parseInt(id_pilot[2])?id_pilot[2]:'10') +'/'+ currentElement.parentNode.id + '/'+$('#type_at').val()+'/'+ $('#tabs .active').text()+'/'+ 0+'/'+index_select_database,
              success: function(data){  //alert("Успешно");
              var newdiv = document.createElement("div");
              $(newdiv).attr('name',"instructor") ;
              console.log(activeElement.name);
              newdiv.id = activeElement.id;

              newdiv.className = activeElement.className;
              newdiv.innerHTML = activeElement.innerHTML;
              $(newdiv).find('font').empty();
              $(newdiv).find('div').empty();
              $(newdiv).attr('editor',$('#user_of_project').attr('editor'));
              newdiv.style['background']=activeElement.style['background']
              newdiv.style['color']=activeElement.style['color']
              if (currentElement.id != 'None/None/None')
              {
                find_elem_append=$(currentElement.parentNode).find("[class*='people'][name!='instructor']").first();
                if ($(find_elem_append).length!=0)
                    $(find_elem_append).before(newdiv);
                else
                    currentElement.parentNode.append(newdiv);
              }
              else
                currentElement.replaceWith(newdiv);
              console.log(newdiv.parentNode.classList);
              $(activeElement).find('.grid_container').append("<div class=box-"+($(activeElement).find('.grid_container div').length+1)+">"+($(newdiv).closest('tr').prevAll().length+1)+"</div>");
              console.log(newdiv.parentNode.id);
              find_and_set_marker_of_missing_crew();
              },
              error: function(){ alert("Ошибка добавления инструктора!");},
             });
        }
      });
    });



      //Конец действия перемещения пилотов
      PilotsListElement.addEventListener(`dragend`, (evt) => {
          const activeElement = PilotsListElement.querySelector(`.selected`);
          currentElement = document.elementFromPoint(event.clientX, event.clientY);
          evt.target.classList.remove(`selected`);
           if (!(currentElement.parentNode.classList.contains(`test-flex`) ||
          currentElement.classList.contains(`test-flex`) ||
          $(currentElement).attr('Name')=="No_pilot")) {return;}
          if (!currentElement.classList.contains('people'))
            {
                currentElement=$(currentElement).attr('Name')=="No_pilot"?$(currentElement).siblings('[class*="people"]')[0]:currentElement.getElementsByClassName('people')[0];
            }
          //currentElement.parentNode.replaceChild(activeElement,currentElement);
          let cell = currentElement.parentNode.parentNode;
          if (cell.tagName.toLowerCase() != 'td')
            return;
          let date = new Date($('input[name=date_send]').val());
           month = date.getMonth()+1;
           year = date.getFullYear();
           if ($(activeElement).attr('id')==null) return;
           id_pilot=activeElement.id.split('/');
       $.ajax({ // проверка "пересечений"
          url: '/wcrew_add_check/'+ id_pilot[0]+'/'+ currentElement.parentNode.id+'/' + index_select_database,
          success: function(data){
          console.log(data['message_add_check'][0][0])
          if (data['message_add_check'][0][0]!=null)
            if (!confirm('У пилота '+activeElement.textContent+'  '+ data['message_add_check'][0][0]+
             ' c '+data['message_add_check'][0][1]+' по '+data['message_add_check'][0][2]+' все равно добавить?'))
                return false;
                //alert($(currentElement.parentNode).attr('name'));
           $.ajax({ // Запись пилотов в таблицу аккорд
          url: '/'+'write_db' +'/'+id_pilot[0]+'/'+ 0 + '/'+ id_pilot[2] +'/' + currentElement.parentNode.id  + '/'+$('#type_at').val()+'/'+$('#tabs .active').text()
          +'/'+ (($(currentElement.parentNode).attr('name')=="None")?0:$(currentElement.parentNode).attr('name')) +'/'+ index_select_database,
          success: function(data){  //alert("Успешно");
              var newdiv = document.createElement("div");
              newdiv.id = activeElement.id;
              newdiv.className = activeElement.className;
              newdiv.className += " people_block";
              newdiv.innerHTML = activeElement.innerHTML;
              $(newdiv).find('font').remove();
              $(newdiv).find('div').remove();
              $(newdiv).attr('editor',$('#user_of_project').attr('editor'));
              now=new Date;
              $(newdiv).attr('date_edit',(now.getDate()<10?"0"+now.getDate():now.getDate())+ ' ' + name_month[now.getMonth()] +' '+now.getFullYear()+' '+now.getHours()+':'+now.getMinutes());
              newdiv.innerHTML = newdiv.innerHTML.split(" ").slice(1,-1).join(" ");
              if (currentElement.id != 'None/None/None')
                {
                find_elem_append=$(currentElement.parentNode).find("[class*='people'][name!='instructor']").filter(function () { return $(this).attr('id').split('/')[2] == id_pilot[2]}).last();
                  if ($(find_elem_append).length!=0)
                        $(find_elem_append).after(newdiv);
                    else
                        currentElement.parentNode.append(newdiv);
                 }
              else
                currentElement.replaceWith(newdiv);
              $(activeElement).find('.grid_container').append("<div class=box-"+($(activeElement).find('.grid_container div').length+1)+">"+($(newdiv).closest('tr').prevAll().length+1)+"</div>");
          // Если добавление пилота происходит на Refresh/Check
              if ($(newdiv).closest('td').find('label:contains("Refresh/Check")').length!=0)
              {
                 div_first_Refresh=$(newdiv).closest("tbody").find('label:contains("Refresh/Check")').filter(function () { return $(this).text().replace(/[^0-9]/gi,'')==$(newdiv).closest('td').find('label').text().replace(/[^0-9]/gi,'') }).first()
                    .closest("td").find('div[class*="test-flex"]');
                 div_second_Refresh=$(newdiv).closest("tbody").find('label:contains("Refresh/Check")').filter(function () { return $(this).text().replace(/[^0-9]/gi,'')==$(newdiv).closest('td').find('label').text().replace(/[^0-9]/gi,'') })//:contains("'+$(newdiv).closest('td').find('label').text().replace(/[^0-9]/gi,'')+'")
                   .closest("td").find('div[class*="test-flex"][id!="'+$(newdiv).closest('div[class*="test-flex"]').attr('id')+'"]');

                $.ajax({ // Запись людей в таблицу аккорд второй Refresh
                      url: '/'+'write_db' +'/'+id_pilot[0]+'/'+ 0 + '/'+ id_pilot[2] +'/' + div_second_Refresh.attr('id')  + '/'+$('#type_at').val()+'/'+$('#tabs .active').text()
                      +'/'+ (($(div_second_Refresh).attr('name')=="None")?0:$(div_second_Refresh).attr('name'))+'/'+index_select_database,
                      success: function(data){
                      if (div_second_Refresh.children('div[id="None/None/None"][class*="people"]').length == 0)
                            {
                            find_elem_append = div_second_Refresh.find("[class*='people'][name!='instructor']").filter(function () { return $(this).attr('id').split('/')[2] == id_pilot[2]}).last();
                            if ($(find_elem_append).length!=0)
                                $(find_elem_append).after(newdiv.cloneNode(true));
                            else
                                div_second_Refresh.append(newdiv.cloneNode(true));
                             }
                      else
                            div_second_Refresh.children('div[id="None/None/None"][class*="people"]').replaceWith(newdiv.cloneNode(true));
                      $(activeElement).find('.grid_container').append("<div class=box-"+($(activeElement).find('.grid_container div').length+1)+">"+($(div_second_Refresh).closest('tr').prevAll().length+1)+"</div>");
                      $.ajax({ // Запись доп. ППЧЛЭ 3.1.2. на первый Refresh/Check
                             url: 'write_ppls_for_pilot/'+ id_pilot[0]+'/'+ 0 + '/' + id_pilot[2]+'/'+ div_first_Refresh.attr('id')+ '/' +$('#type_at').val()+'/' + 'ППЧЛЭ 3.1.2.'+'/'
                             +index_select_database,
                             success: function(){
                             alert("Запись ППЧЛЭ 3.1.2. на wcrew_main="+ div_first_Refresh.attr('id'));
                             }
                      });
                      find_and_set_marker_of_missing_crew();
                      }
                });
              }
              find_and_set_marker_of_missing_crew();
          },
          error: function(){ alert("Ошибка добавления пилота!");},
          });
          }
       });
      });

      //Инициализация родительских классов элементов активной таблицы
      PeopleTableListElement = document.getElementById('followers');

      //Инициализация списка всех элементов
      const peopleElements= PeopleTableListElement.querySelectorAll('.test-flex');


      //Начало действия перемещения людей в таблице
      peopleElements.forEach(p => p.addEventListener(`dragstart`, (evt) => {
          evt.target.classList.add(`selected`);
      }));

      //Конец действия перемещения людей в таблице
      peopleElements.forEach(p => p.addEventListener(`dragend`, (evt) => {
          evt.target.classList.remove(`selected`);
          for (const inst of p.children) {
              inst.classList.remove(`selected`);
      }
      }));

      //Замена людей внутри одной сессии
      peopleElements.forEach(p => p.addEventListener(`dragover`, (evt) => {
          // Разрешаем сбрасывать элементы в эту область
          evt.preventDefault();

          // Находим перемещаемый элемент
          const activeElement = p.querySelector(`.selected`);
          // Находим элемент, над которым в данный момент находится курсор
          const currentElement = document.elementFromPoint(event.clientX, event.clientY);
          // Проверяем, что событие сработало:
          // 1. не на том элементе, который мы перемещаем,
          // 2. именно на элементе списка
          const isMoveable = activeElement !== currentElement &&
          currentElement.classList.contains(`people`) && !currentElement.classList.contains(`selected`);

          // Если нет, прерываем выполнение функции
          if (!isMoveable) {
          return;
        }

        // Находим элемент, перед которым будем вставлять
          const nextElement = (currentElement === activeElement.nextElementSibling) ?
            currentElement.nextElementSibling :
            currentElement;

         // Вставляем activeElement перед nextElement
          //p.insertBefore(activeElement, nextElement);
          const tmp=activeElement.innerHTML;
          activeElement.innerHTML=currentElement.innerHTML;
          currentElement.innerHTML=tmp;
          activeElement.classList.remove(`selected`);
          currentElement.classList.add(`selected`);
      }));
      };
/*$("#delete_color_table").click(
    function(){
    $('#context-menu').removeClass( ['visible' ] )
    const point_position = $("#delete_color_table").position();
    const point_position_global = $("#delete_color_table").offset();
    const currentElement = document.elementFromPoint(parseInt($('#context-menu').css('left'))-1,
    parseInt($('#context-menu').css('top'))-1);
    if (!currentElement.parentNode.classList.contains(`test-flex`) || !parseInt(currentElement.parentNode.id)) {return;}
    id_mass_pars = currentElement.id.split('/');
    if (!parseInt(id_mass_pars[0])) return;
    if (confirm('Удалить '+currentElement.innerHTML+' ?') )
       $.ajax({ // Удаление из сессии человека
          url: 'delete_color_table/'+currentElement.parentNode.id+'/'+id_mass_pars[0],
          success: function(){
          console.log("Удаление успешно");

          });
    }

);*/



