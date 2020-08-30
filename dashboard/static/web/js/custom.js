
// ==================================== Header Js Start ====================================
    // $(document).ready(function(){
    //     $(window).resize(function(){
            if ( $(window).width() > 10 ) {
                //footer fixed js
                    $(document).ready(function() {
                        var footer_padd = $("nav").height() + "px";
                        $("main").css("padding-top", footer_padd);
                    })
            }
    //     });
    // });

// ==================================== footer Js Start ====================================
    $(document).ready(function(){
        if ( $(window).width() > 991 ) {
            //footer fixed js
            $(document).ready(function() {
                var footer_padd = $("footer").height() + "px";
                $("main").css("margin-bottom", footer_padd);
            })
        }
    });

    // When the user scrolls the page, execute myFunction
    window.onscroll = function() {myFunction()};
    // Get the header
    var header = document.getElementById("myHeader");
    // Get the offset position of the navbar
    var sticky = header.offsetTop;
    // Add the sticky class to the header when you reach its scroll position. Remove "sticky" when you leave the scroll position
    function myFunction() {
      if (window.pageYOffset > sticky) {
        header.classList.add("sticky");
      } else {
        header.classList.remove("sticky");
      }
    }


    $(document).ready(function(){
        // if ( $(window).width() < 992 ) {
            $(document).ready(function() {
                $(".responsive_toggle .responsive_side_toggle,.seacr_coll").click(function() {
                    $(".right_menu_responsive").addClass("active");
                    // $(".overlay").addClass("active");
                    $("body,html").addClass("active");
                });
                $(".right_menu_close,.overlay").click(function() {
                    $(".right_menu_responsive").removeClass("active");
                    // $(".overlay").removeClass("active");
                    $("body,html").removeClass("active");
                });
            });
        // };
    });
// ==================================== Header Js End ====================================
/*=============Init Accordian============*/
var responsiveflag = false;

jQuery(document).ready(function () {
    responsiveResize();
    jQuery(window).resize(responsiveResize);
});
function responsiveResize()
{
    if (jQuery(window).width() <= 767 && responsiveflag == false)
    {
        accordion('enable');
        responsiveflag = true;
    }
    else if (jQuery(window).width() >= 768)
    {
        accordion('disable');
        responsiveflag = false;
    }
}
function accordion(status)
{
    if(status == 'enable')
    {
        var accordion_selector = '.footer_menu_list > h4';

        jQuery(accordion_selector).on('click', function(e){
            jQuery(this).toggleClass('active').next().stop().slideToggle('medium');
            e.preventDefault();
        });
        jQuery(accordion_selector).next().slideUp('fast');
    }
    else
    {
        jQuery('.footer_menu_list > h4').removeClass('active').off().next().removeAttr('style').slideDown('fast');
    }
}

// top to bottom arrow
$(document).ready(function(){ 
$(window).scroll(function(){ 
    if ($(this).scrollTop() > 100) { 
        $('#scroll').fadeIn(); 
    } else { 
        $('#scroll').fadeOut(); 
    } 
}); 
$('#scroll').click(function(){ 
    $("html").animate({ scrollTop: 0 }, 500); 
    return false; 
}); 
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

// search bar
$(".sreach-icon").click(function(){
        $(".products-search-top,body").addClass('active');
    });
    $(".close-icon,.overlay").click(function(){
        $(".products-search-top,body").removeClass('active');
    });
   

//preloader
$(window).on('load', function() {
  $('#status').fadeOut();
  $('#preloader').delay(100).fadeOut();
});

