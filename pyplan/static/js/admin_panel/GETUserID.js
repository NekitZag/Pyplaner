$("#GETUserId").click(function() {
    pers_id = $('#inputPersId').val();
    console.log(pers_id);
        $.ajax({
          url: pers_id,
          success: function(data){
            $('#blockUserId').html($(data.html));
          },
          error: function(){ console.log("Error");},
      });

  });