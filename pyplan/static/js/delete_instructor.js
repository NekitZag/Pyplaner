  $("#delete_inst").click(function() {
    alert('CLICK');
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
          url:'delete/' + pers_id + '/' + group +'/'+ tvs_id,
          success: function(data){
            $('#instr_in_list').html($(data.html));
            alert("Инструктор УДАЛЕН из списка")
            location.reload()
          },
          error: function(){
          alert("Инструктор не удален. Чота сломалось... Скажите нам починить...")
          console.log("Error");},
      });
    }
  });