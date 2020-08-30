var ctx = document.getElementById("myChart").getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Tokyo",   "Mumbai",   "Mexico City",  "Shanghai", "Sao Paulo",    "New York", "Karachi"],
            datasets: [{
                label: 'Best Result ', // Name the series
                data: [350,300, 518 ,   521 ,  250,  240,0],
                fill: false,
                borderColor: '#63a62e', 
                backgroundColor: '#63a62e',
                borderWidth: 1,
                weight: 100,
            }]
        },       
        options: {
            legend: {
                display: false,
            },
            scales: {
            yAxes: [{
                display:false,
                ticks: {
                    display: false
                },
                gridLines: {
                  display: false,
                },
                tooltip: {
                      // enabled: false,
                      disabled :true,
                      offsetX: 0,
                      display:false
                },
            }],xAxes: [{
                display:false,
                ticks: {
                    display: false
                },gridLines: {
                  display: false,
                }
            }],          
        },
          responsive: true, 
          maintainAspectRatio: false, 
        }
    });

    // 

    var ctx3 = document.getElementById("myChart3").getContext('2d');
    var myChart = new Chart(ctx3, {
        type: 'line',
        data: {
            labels: ["Tokyo",   "Mumbai",   "Mexico City",  "Shanghai", "Sao Paulo",    "New York", "Karachi"],
            datasets: [{
                label: 'Best Result ', // Name the series
                data: [350,300, 518 ,   521 ,  250,  240,0],
                fill: false,
                borderColor: '#63a62e', 
                backgroundColor: '#63a62e',
                borderWidth: 1,
                weight: 100,
            }]
        },       
        options: {
            legend: {
                display: false,
            },
            scales: {
            yAxes: [{
                display:false,
                ticks: {
                    display: false
                },
                gridLines: {
                  display: false,
                },
                tooltip: {
                      // enabled: false,
                      disabled :true,
                      offsetX: 0,
                      display:false
                },
            }],xAxes: [{
                display:false,
                ticks: {
                    display: false
                },gridLines: {
                  display: false,
                }
            }],         
        },
          responsive: true, 
          maintainAspectRatio: false, 
        }
    });
   
    // 

    var ctx2 = document.getElementById("myChart2");

    var config2 = {

      animationEnabled: true,

      type: 'pie',

      data: {

        labels: [

        "Green",

        "gray"

        ],

        datasets: [{

          data: [73.5,26.5],

          backgroundColor: [

            '#63a62e',

            '#dfe4ea'

          ],

          borderWidth: 0,

        }]

      },

      options: {

        cutoutPercentage: 45,

        responsive: true,

        legend:false,

        aspectRatio:10

      }

    };

    var chart2 = new Chart(ctx2, config2);



    // 

    var ctx5 = document.getElementById("myChart5");

    var config5 = {

      animationEnabled: true,

      type: 'pie',

      data: {

        labels: [

        "Green",

        "gray"

        ],

        datasets: [{

          data: [73.5,26.5],

          backgroundColor: [

            '#63a62e',

            '#dfe4ea'

          ],

          borderWidth: 0,

        }]

      },

      options: {

        cutoutPercentage: 45,

        responsive: true,

        legend:false,

        aspectRatio:10

      }

    };

    var chart5 = new Chart(ctx5, config5);

    // slider

    $(".owl-carousel").owlCarousel({

        navigation : false,

        dots: false,

        arrow:true,

        items:3,

         loop: true,

        autoplay:true,fluidSpeed:true,

        autoplayHoverPause: true,

        URLhashListener:true,

        startPosition: 'URLHash',

        slideSpeed: 2000,

        smartSpeed: 1500,

        responsiveClass:true,

        responsive:{

            0:{

                items:1,

                nav:true

            },

            600:{

                items:3,

                nav:false

            }

        }

    });



    // Select Dropdown

    $('select').each(function() {

        var $this = $(this),

            numberOfOptions = $(this).children('option').length;



        $this.addClass('select-hidden');

        $this.wrap('<div class="select"></div>');

        $this.after('<div class="select-styled"></div>');



        var $styledSelect = $this.next('div.select-styled');

        $styledSelect.text($this.children('option').eq(0).text());



        var $list = $('<ul />', {

            'class': 'select-options'

        }).insertAfter($styledSelect);



        for (var i = 0; i < numberOfOptions; i++) {

            $('<li />', {

                text: $this.children('option').eq(i).text(),

                rel: $this.children('option').eq(i).val()

            }).appendTo($list);

        }



        var $listItems = $list.children('li');



        $styledSelect.click(function(e) {

            e.stopPropagation();

            $('div.select-styled.active').not(this).each(function() {

                $(this).removeClass('active').next('ul.select-options').hide();

            });

            $(this).toggleClass('active').next('ul.select-options').toggle();

        });



        $listItems.click(function(e) {

            e.stopPropagation();

            $styledSelect.text($(this).text()).removeClass('active');

            $this.val($(this).attr('rel'));

            $list.hide();

            //console.log($this.val());

        });



        $(document).click(function() {

            $styledSelect.removeClass('active');

            $list.hide();

        });



    });

    

      var debugMode, getClientsForMap, log, mapOptions, markerPath, myLogoPath, siLogoPath, testIntervalId;

      debugMode = true;

      testIntervalId = -1;

      markerPath = 'images/marker1.png';

      siLogoPath = 'images/map_hover.png';

      myLogoPath = 'images/map_hover.png';

      mapOptions = {

        dotRadius: 3,

        width: $('#smallimap').width(),

        height:$('#smallimap').height(),

        colors: {

          lights: ["#bec7d1", "#bec7d1", "#bec7d1", "#bec7d1", "#bec7d1"],

          darks: ["#bec7d1", "#bec7d1", "#bec7d1", "#bec7d1"]

        }

      };

      log = function(message) {

        var _ref;

        if (debugMode) {

          return (_ref = window.console) != null ? _ref.log(message) : void 0;

        }

      };

      getClientsForMap = function() {        

        smallimap.addMapIcon('Shoe Shop', 'Canada', markerPath, myLogoPath,-92.905831, 30.495368);

        smallimap.addMapIcon('Shoe Shop', 'Australia', markerPath, myLogoPath,99.995889, -50.495368);

        smallimap.addMapIcon('Shoe Shop', 'Italy', markerPath, myLogoPath,42.905831, 12.495368);

        

        //return smallimap.addMapIcon('Shoe Shop', 'Australia', markerPath, siLogoPath,-26.927634, 133.874295);

      };

      

      $('.smallipop').smallipop({

        theme: 'white',

        cssAnimations: {

          enabled: true,

          show: 'animated flipInX',

          hide: 'animated flipOutX'

        }

      });

      window.smallimap = $('#smallimap').smallimap(mapOptions).data('api');

      smallimap.run();

      getClientsForMap();











      var debugMode1, getClientsForMap1, log1, mapOptions1, markerPath1, myLogoPath1, siLogoPath1, testIntervalId1;

      debugMode1 = true;

      testIntervalId1 = -1;

      markerPath1 = 'images/marker1.png';

      siLogoPath1 = 'images/map_hover.png';

      myLogoPath1 = 'images/map_hover.png';

      mapOptions1 = {

        dotRadius: 3,

        width: $('#smallimap').width(),

        height:$('#smallimap').height(),

        colors: {

          lights: ["#bec7d1", "#bec7d1", "#bec7d1", "#bec7d1", "#bec7d1"],

          darks: ["#bec7d1", "#bec7d1", "#bec7d1", "#bec7d1"]

        }

      };

      log1 = function(message) {

        var _ref;

        if (debugMode) {

          return (_ref = window.console) != null ? _ref.log(message) : void 0;

        }

      };

      getClientsForMap1 = function() {        

        smallimap.addMapIcon('Shoe Shop', 'Canada', markerPath1, myLogoPath1,-92.905831, 30.495368);

        smallimap.addMapIcon('Shoe Shop', 'Australia', markerPath1, myLogoPath1,99.995889, -50.495368);

        smallimap.addMapIcon('Shoe Shop', 'Italy', markerPath1, myLogoPath1,42.905831, 12.495368);

        

        //return smallimap.addMapIcon('Shoe Shop', 'Australia', markerPath, siLogoPath,-26.927634, 133.874295);

      };

      

      $('.smallipop').smallipop({

        theme: 'white',

        cssAnimations: {

          enabled: true,

          show: 'animated flipInX',

          hide: 'animated flipOutX'

        }

      });

      window.smallimap = $('#smallimap1').smallimap(mapOptions1).data('api');

      smallimap.run();

      getClientsForMap();