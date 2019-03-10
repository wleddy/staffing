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

function show_hamburger(){
    $('#hamburger').show();
}

function hide_hamburger(){
    $('#hamburger').hide();
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
    // this is called when scree nize changes
    var nav = $("#primary-nav");
    var w = document.body.offsetWidth
    if ( w < 993){
        // display the side menu block
        nav.removeClass('w3-bar').addClass('w3-bar-block').css({'min-height':'100vh',overflow:'auto',position:'absolute',right:0,top:0});
        // dd content pushes lower items down when expanded
        $('.w3-dropdown-content').css({'position':'relative'})
    } else {
        // display horizontal menu bar
        nav.addClass('w3-bar').removeClass('w3-bar-block').css({position:'static','min-height':0,}).show();
        // dd content overlays
        $('.w3-dropdown-content').css({'position':'absolute'})
    }
}

function toggle_table_search(input_field_id,table_id){
    /*
    show the search table and move it into position below the input field
    */
    var input = document.getElementById(input_field_id);
    var table = document.getElementById(table_id);
    
    if (table.style.display != 'none' && table.style.display != ''){ 
        table.style.display = 'none';
        table.style.position = 'static';
    }
    else
    {
        table.style.display = 'block';
        table.style.position = 'absolute'
    }
}


function reset_table_search(table_id){
    // ensure that all rows of the search table are visible
    var table = document.getElementById(table_id);
    var tr = table.getElementsByTagName("tr");
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