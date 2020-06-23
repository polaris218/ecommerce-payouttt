//preloader
$(window).on('load', function() {
  $('#status').fadeOut();
  $('#preloader').delay(100).fadeOut();
});




// sidebar
$(document).ready(function () {  
  $('.list-unstyled button').on('click', function () {
    $('.wrapper').toggleClass('open');
    $('#sidebar').toggleClass('active');
    
  });
});
$(".close .d-none").click(function(){
  $("#sidebar").removeClass("active");
  $('body').removeClass('active');
});
$("#sidebarCollapse").click(function(){
  $("#sidebar").addClass("active");
});
$("button#sidebarCollapse").click(function(){
  $(".list-unstyled").removeClass("show");
   $('body').addClass('active');
});


$(document).ready(function(){
  if ( screen.width < 768 ) {
    $(".search_scroll").click(function() {
        $(".logo_left_search").addClass("intro");
        $(".overlay").addClass("active");
        $("body,html").addClass("active");
    })
    $(".search_remove_on,.overlay").click(function() {
        $(".logo_left_search").removeClass("intro");
        $(".overlay").removeClass("active");
        $("body,html").removeClass("active");
    })
  }
});


!function(e){
  var r=e(window),s=e("#sidebar");
  r.resize(function(){
    if(r.width()>768)return s.addClass("responsive-add-sidebar");s.removeClass("responsive-add-sidebar")
  }).trigger("resize")}(jQuery);
$(".responsive-add-sidebar > ul > li a").click(function(){
  $("#sidebar").removeClass("active");
});
$(".responsive-add-sidebar > ul > li").click(function(){
    $(".wrapper").removeClass("open");
});
// fixed-navbar
$(window).scroll(function(){
  if($(window).scrollTop() >= 300){
    $('.navbar').addClass('fixed-header');
  }
  else{
      $('.navbar').removeClass('fixed-header');
  }
});
// dark mode

jQuery(document).ready(function(){
    jQuery(".post__tags__section").insertBefore(".grow-sec");
});
  
(function() {
  // Theme switch
  var themeSwitch = document.getElementById('themeSwitch');
  if(themeSwitch) {
    initTheme(); // if user has already selected a specific theme -> apply it
    themeSwitch.addEventListener('change', function(event){
      resetTheme(); // update color theme
    });
    
    function initTheme() {
      var darkThemeSelected = (localStorage.getItem('themeSwitch') !== null && localStorage.getItem('themeSwitch') === 'dark');
      // update checkbox
      jQuery("body").removeClass("dark-mode");
      themeSwitch.checked = darkThemeSelected;
      // update body data-theme attribute
      
      darkThemeSelected ?   document.body.setAttribute('id', 'dark') : document.body.removeAttribute('id');     
        
    };
    
  if(jQuery('.switch input').prop("checked") == true){
    jQuery("body").addClass("dark-mode");
  }else{
    jQuery("body").removeClass("dark-mode");
  }

    function resetTheme() {
      if(themeSwitch.checked) { // dark theme has been selected
        document.body.setAttribute('id', 'dark');
      jQuery("body").addClass("dark-mode");
        localStorage.setItem('themeSwitch', 'dark');
      } else {
        document.body.removeAttribute('id');
        localStorage.removeItem('themeSwitch');
      jQuery("body").removeClass("dark-mode");
      } 
    };
  }
}());

jQuery(document).ready(function(){
    jQuery(".post__tags__section").insertBefore(".grow-sec");
});
    
(function() {
    // Theme switch
    var themeSwitch_mobile = document.getElementById('themeSwitch_mobile');
    if(themeSwitch_mobile) {
        initTheme(); // if user has already selected a specific theme -> apply it
        themeSwitch_mobile.addEventListener('change', function(event){
        resetTheme(); // update color theme
    });
        
    function initTheme() {
        var darkThemeSelected = (localStorage.getItem('themeSwitch_mobile') !== null && localStorage.getItem('themeSwitch_mobile') === 'dark');
        // update checkbox
        jQuery("body").removeClass("dark-mode");
        themeSwitch_mobile.checked = darkThemeSelected;
            // update body data-theme attribute
            
            darkThemeSelected ?   document.body.setAttribute('id', 'dark') : document.body.removeAttribute('id');         
            
    };
        
    if(jQuery('.switch input').prop("checked") == true){
        jQuery("body").addClass("dark-mode");
    }else{
        jQuery("body").removeClass("dark-mode");
    }

    function resetTheme() {
        if(themeSwitch_mobile.checked) { // dark theme has been selected
            document.body.setAttribute('id', 'dark');
            jQuery("body").addClass("dark-mode");
            localStorage.setItem('themeSwitch_mobile', 'dark');
        } else {
            document.body.removeAttribute('id');
            localStorage.removeItem('themeSwitch_mobile');
            jQuery("body").removeClass("dark-mode");
        } 
    };
    }
}()); 



$('.news-slider').owlCarousel({
    loop:false,
    margin:0,
    dots:false,
    nav:true,
    responsive:{
        0:{
            items:1
        },
        600:{
            items:1
        },
        992:{
            items:2,
            margin:10
        },
        1200:{
            items:2,
            margin:10
        },
        1360:{
            items:1
        }
    }
}) 