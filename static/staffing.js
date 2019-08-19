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

