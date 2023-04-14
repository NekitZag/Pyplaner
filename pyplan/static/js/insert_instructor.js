  $("#insert_inst").click(function() {
    var tvs_id = $('#flight').val();
    var group = $('#group').val();
    var pers_id = $('.instructor').attr('id');
    console.log(pers_id)
    console.log(group)
    console.log(tvs_id)
    if (tvs_id == 'Null'){
        alert("Выберите Тип ВС!");}
    else if (group === 'Null'){
        alert("Выберите Группу!");}
    else{
        $.ajax({ // Поиск по sap номеру человека
          url:'insert/' + pers_id + '/' + group +'/'+ tvs_id,
          success: function(data){
            $('#adding_people').html($(data.html));
            alert("Инструктор добавлен!")
            location.reload()
          },
          error: function(){
          alert("Инструктор не добавлен. Чота сломалось... Скажите нам починить... или он уже есть в этом типе ВС")
          console.log("Error");},
      });
    }
  });


$('#id_sap').keydown(function(e) {
if (e.keyCode === 13) $("#search_sap").click(); // Поиск человека по Enter
});

$("#search_sap").click(function() {
    sap_tab = $('#id_sap').val();
        $.ajax({ // Поиск по sap номеру человека
          url: sap_tab,
          success: function(data){
            $('#adding_people').html($(data.html));
          },
          error: function(){ console.log("Error");},
      });

  });