// Scripts for Staffing Web Site



    // for navigation buttons
function w3_open(id_name) {
    document.getElementById(id_name).style.display = "block";
}
function w3_close(id_name) {
    document.getElementById(id_name).style.display = "none";
}
function w3_hide(id_name) {
    document.getElementById(id_name).style.visibility = "hidden";
}
function w3_show(id_name) {
    document.getElementById(id_name).style.visibility = "visible";
}

function signup_count(which,howmany,maxcnt){
    var which = $(which)
    var cnt = parseInt(which.val())
    cnt = cnt + howmany;
    if(cnt >= 0 && cnt <= maxcnt ){
        which.val(cnt.toString());
    }
}

function primary_nav_toggle() {
    // this is envocked from the Hamburger
    var nav = $("#primary-nav");
    if (nav.hasClass('w3-hide-small')){
        nav.removeClass('w3-hide-small').removeClass('w3-hide-medium');
    } else {
        nav.addClass('w3-hide-small').addClass('w3-hide-medium');
    }
    set_menu_style();
}

function set_menu_style(){
    var nav = $("#primary-nav");
    var w = document.body.offsetWidth
    if ( w < 993){
        // display the side menu block
        nav.removeClass('w3-bar').addClass('w3-bar-block').css({'max-height':'80vh',overflow:'scroll',position:'absolute',right:0,top:0});
    } else {
        // display horizontal menu bar
        nav.addClass('w3-bar').removeClass('w3-bar-block').css({position:'static'}).show();
    }
}

function reset_table_search(table_id){
    // ensure that all rows of the search table are visible
    table = document.getElementById(table_id);
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        tr[i].style.display = "";
    }
}

function table_search(input_field_id,table_id,column_num=0) {
  var input, filter, table, tr, td, i;
  input = document.getElementById(input_field_id);
  filter = input.value.toUpperCase();
  table = document.getElementById(table_id);
  
  // reset this display if no text
  if (filter.length == 0){reset_table_search(table_id);}
  
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[column_num];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}