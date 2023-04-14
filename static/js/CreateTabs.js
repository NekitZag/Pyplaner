$(document).ready(function() {
    var tabs = $("#container-1").tabs();
    var tabCounter = 1;

    $('#add_tab').click(function() {
        var ul = tabs.find("ul");
        var current_idx = ul.find("li").length +1;
        $("<li><a href='frag-" + current_idx + "'> Call</a></li>").appendTo(ul);
        tabs.append("<div id='frag-" + current_idx + "'> new tab " + current_idx + "</div");
        tabs.tabs("refresh");
        tabs.tabs("select",1);
    });
});