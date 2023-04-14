$(document).on('click', '#Table_7000_simulator', function(event) {
  let cell = event.target.parentNode.parentNode;
  if (cell.tagName.toLowerCase() != 'td')
    return;
  let i = cell.parentNode.rowIndex;
  let j = cell.cellIndex;
  /*let table = document.querySelector('table');
  for (var m = 0; m < table.rows.length; m++) {
    for (var n = 0; n < table.rows[m].cells.length; n++) {
      if (table.rows[m].cells[n] == cell) {
        i = m;
        j = n;
      }
    }
  }*/
  console.log(i, j);
});


$(document).on('click', '#Table_5000_simulator', function(event) {
  let cell = event.target.parentNode.parentNode;
  if (cell.tagName.toLowerCase() != 'td')
    return;
  let i = cell.parentNode.rowIndex;
  let j = cell.cellIndex;
  /*let table = document.querySelector('table');
  for (var m = 0; m < table.rows.length; m++) {
    for (var n = 0; n < table.rows[m].cells.length; n++) {
      if (table.rows[m].cells[n] == cell) {
        i = m;
        j = n;
      }
    }
  }*/
  console.log(i, j);
});
//Скрытие-раскрытие сессий, время которых определено в именнованном массиве string_time_session
$('#checkbox_hide_extra_sessions').click(function(){
    string_time_session={
        '320':{
            '7000': [['00:05', '06:05'],['04:10','10:10'],['08:15','14:15'],['13:15','19:15'], ['17:20','23:20']],  //  можно добавить вывод технических часов
            '5000': [['00:45','06:45'],['07:30','13:30'],['11:35','17:35'],['16:35','22:35'],['20:40','02:40']],
              },
        '330':{
             '7000': [['00:05','06:05'],['06:35', '12:35'],['11:35','17:35'],['15:40','21:40'],['19:45','01:45']],
               },
        '350':{
             '7000': [['00:15','06:15'],['06:30', '12:30'],['10:45','16:45'],['15:45','21:45'],['20:00','02:00']],
               },
    };
    if (this.checked)
    {
         //string_time_session[$('#tabs .active').text()]
        console.log($('#main_display_table div.active table thead tr th').text());
        var select_mass_th=[];
        $('#main_display_table div.active table thead tr th').each(function() {
            select_mass_th.push($(this).text());
        });
        console.log(select_mass_th);
        for (i=0; i < select_mass_th.length ; i++)
        {
            select_mass_th[i] = select_mass_th[i].match(/\d{2}:\d{2}/g) || ['',''];
            for (j=0;j<string_time_session[$('#type_at').val()][$('#tabs .active').text()].length;j++)
               {
//               console.log(string_time_session[$('#type_at').val()][$('#tabs .active').text()][j]+'--- '+select_mass_th[i])
               flag_compare=false;
               if (string_time_session[$('#type_at').val()][$('#tabs .active').text()][j].length == select_mass_th[i].length)
                    if (string_time_session[$('#type_at').val()][$('#tabs .active').text()][j].every(function(element, index) {
                                                                                                return element == select_mass_th[i][index];
                                                                                                }))
                    {
                        flag_compare=true;
                        break;
                    }
                }
                if (!flag_compare && i!=0)
                $('#main_display_table div.active table td:nth-child('+(i+1)+'),#main_display_table div.active table th:nth-child('+(i+1)+')').hide();
        }
        console.log(select_mass_th);
    }
    else
    $('#main_display_table div.active table td,#main_display_table div.active table th').show();
});

