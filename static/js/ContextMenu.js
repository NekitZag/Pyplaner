const contextMenu = document.getElementById("context-menu");
const scope = document.querySelector("body");

scope.addEventListener("contextmenu", (event) => {
  event.preventDefault();

  const { clientX: mouseX, clientY: mouseY } = event;
  const currentElement = document.elementFromPoint(mouseX, mouseY);
  $('#pilot_editor').css('display','none');
  $('#pilot_editor span[level="editor"]').text("");
  $('#pilot_editor span[level="date"]').text("");
  if (currentElement.classList.contains('people'))
  {
    contextMenu.classList.add("visible");
    $.ajax({
    url:'pilot_editor/'+$(currentElement).attr('editor'),
    success:function(data){
//        console.log(data['editor']);
        if(data['editor']!=="" && data['editor']!=null)
        $('#pilot_editor').css('display','block');
        $('#pilot_editor span[level="editor"]').text(data['editor']);
        $('#pilot_editor span[level="date"]').text($(currentElement).attr('date_edit'));
    }
    });
  }
  else
  {
    contextMenu.classList.remove("visible");
    return;
  }
  contextMenu.style.top = `${mouseY}px`;
  contextMenu.style.left = `${mouseX}px`;


//  setTimeout(() =>{
//    contextMenu.classList.add("visible");
//  });
});

scope.addEventListener("click",(e) =>{
  if (e.target.offsetParent != contextMenu) {
    contextMenu.classList.remove("visible");
  }
});