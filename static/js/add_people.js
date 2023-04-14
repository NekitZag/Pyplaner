$(document).ready(function(){
update_list_pilots();
//html.find('script[src="http://firstScript.com"]').remove();
});

$('input[name=date_send_add_people]').change(update_list_pilots);
$('#type_at').change (update_list_pilots);

function update_list_pilots()
{
var date = new Date($('input[name=date_send_add_people]').val());
month = date.getMonth()+1;
year = date.getFullYear();
console.log(month);
console.log(year);
$.ajax({ // Обновление списка людей
        url: 'display_pilots_and_instructors/' +  $('#type_at').val() + '/1/' +$('input[name=date_send_add_people]').val()+ '/' + month + '/' + year + '/'+index_select_database,
    success: function (data) {
       $('#show_people').html($(data.html));
       $('#show_people div[id="pilots"] div[class*="people"][id!=null]').append('<a onClick="hide_people_from_list_DB(this);" class="delete-from-list"><img class="material-icons" src="/static/logo/trash.svg" /></a>');
//        $(data.html).find('div').each(function(){
//        var img = '<a href="#" class="delete-from-list"><img class="material-icons" src="{% static ''logo/trash.svg''%}" /></a>';
//        $(this).append(img);
//        console.log('img append');
//       });
       $('#instructors').remove();
      },
    });
}

function hide_people_from_list_DB(element)
{
    sap_tab=0;flag=true;
    $(element).closest('div[class*="people"]').text().split(" ").forEach(function(elem){ if (parseInt(elem) && flag) {sap_tab=elem; flag=false;} })
    console.log(sap_tab);
    $.ajax({ // Поиск по sap номеру человека
          url: 'search_sap/' + sap_tab+'/'+index_select_database ,
          success: function(data){
              select_data=[];
              for (i=0;i<data["pilot_id"].length;i++)
                if (data["pilot_id"][i][9]==$('#type_at').val())
                    select_data=data["pilot_id"][i];
              $.ajax({ // Скрытие пилота из списока, идентификатор "не виден" (hide_people=1)
                  url: 'add_pilots_in_active_list/' + select_data[1]+'/'+select_data[9]+'/'+$('input[name=date_send_add_people]').val()+"-01"+'/1'+'/'+index_select_database,
                  success: function(data){
                  console.log('Cкрыт пилот с SAP: ' + sap_tab);
                  $(element).closest('div[class*="people"]').hide();
                  },
                  error: function(){ console.log("Не добавлен пилот в ручной лист");
                    alert("Пилот уже присутсвует в списке! Будьте внимательнее!");
                  },

                  });
            },
          error: function(){ console.log("Sap search!");},
      });

};


$('#search_pilots').keydown(function(e) {
if (e.keyCode === 13) $("#search_add_pilot").click(); // Поиск человека по Enter
});
$("#search_add_pilot").click(function() {
    sap_tab = $('#search_pilots').val();
        $.ajax({ // Поиск по sap номеру человека
          url: 'search_sap/' + sap_tab +'/'+index_select_database,
          success: function(data){
          console.log('ENTER' + sap_tab);
            $('#adding_people').html($(data.html));
          },
          error: function(){ console.log("Error");},
      });

  });

$(".block_all_pilots").on('click','a[class="add-to-another-list"]',function(){
    console.log($('input[name=date_send_add_people]').val());
   $.ajax({ // Добавление пилота в ручной список с идентификатором "виден" (hide_people=0)
          url: 'add_pilots_in_active_list/' + $(this).closest('li').attr('id')+'/'+$('input[name=date_send_add_people]').val()+"-01"+'/0'+'/'+index_select_database,
          success: function(data){
          console.log('Добавлен пилот в ручной лист с SAP: ' + sap_tab);
          update_list_pilots();
          },
          error: function(){ console.log("Не добавлен пилот в ручной лист");
            alert("Пилот уже присутсвует в списке! Будьте внимательнее!");
          },
      });
});

// $("#search_delete_pilot").on ('click', function() {
//    sap_tab = $('#filter_instructors').val();
//    console.log('yep!',sap_tab);
//
//        $.ajax({ // Апдейт типа тренажера в базе Аккорд
//          url: 'delete_people/' + sap_tab ,
//          success: function(data){
//          console.log('ENTER' + sap_tab);
//            $('#delete_people').replaceWith($(data.html));
//          },
//          error: function(){ console.log("Error");},
//      });
//
//  });
