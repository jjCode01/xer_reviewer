var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.maxHeight){
            content.style.maxHeight = null;
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
        } 
    });
}


function clickHandle(evt, id) {
    var i, x, tablinks;
    x = document.getElementsByClassName("cat");
    for (i = 0; i < x.length; i++) {
      x[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < x.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" blue_but", "");
    }
    document.getElementById(id).style.display = "flex";
    evt.currentTarget.className += " blue_but";
}