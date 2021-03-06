define(['headroom1', 'headroom', 'cookie', 'bootstrap'],
	function(headroom) {

       return {

        init: function(classie, Chart) { 

            var bodyEl = document.body,
            content = document.querySelector( '.content-wrap' ),
            openbtn = document.getElementById( 'open-button' ),
            closebtn = document.getElementById( 'close-button' ),
            isOpen = false,
            upcomingPlayedMatchesTabs = $("#upcoming-past-nav li"),
            played_matches_cooks = $.cookie("show_played_matches"),
            unplayedButton = $("#upcoming-past-nav li.unplayed");
            playedButton = $("#upcoming-past-nav li.played"),
            homeAwayModuleTabs = $('.module-home-away__tab'),
            homeAwayModuleContentPanels = $('.module-home-away__content'),
            Chartjs = Chart.noConflict(),
            //connect to the socket server.
            socket = io.connect('http://' + document.domain + ':' + location.port + '/test'),
            navMessages = $('#navMessages');


            window.setTimeout(function() {
                 $(".alert").fadeTo(1200, 0)
                            .slideUp(1200, function(){
                                $(this).remove();
                            });
            }, 1000);


            /* Making room for the content of the page */
            $(".headroom").headroom({
                 "tolerance": 20,
                 "offset": 50,
                 "classes": {
                     "initial": "animated",
                     "pinned": "slideDown",
                     "unpinned": "slideUp"
                 }
            });

            /* Switching between tabs in the Prediction Module Home/Away */
            homeAwayModuleTabs.click(function(e){
                 e.preventDefault();

                 var tab_id = $(this).attr('data-tab');

                 homeAwayModuleTabs.removeClass('active');
                 homeAwayModuleContentPanels.removeClass('active');

                 $(this).addClass('active');
                    $("#"+tab_id).addClass('active');
                });

                if (played_matches_cooks == 1) {
                    unplayedButton
                    .removeClass("active")
                    .siblings()
                    .addClass("active")
                } else {
                    playedButton    
                    .removeClass("active")
                    .siblings()
                    .addClass("active")
                }


        $('input[name="hunchRadio"]').change(function(event) {
            var my_hunch = $(this).val(),
                match_id = $('.module-hunch').attr('data');

            $("#hunch").text(my_hunch);
            $.getJSON('http://' + $SCRIPT_ROOT + '/update_hunch/' + match_id, {
                hunch: my_hunch
            });
            return false;
        });

        /* receiving updated winner data 
            sent from the server after change in user hunch */
        socket.on('hunch_updated', function(msg) {

            //update html for the overall prediction
            $('#predictedMatchWinner').html(msg.data.team_winner_name);
            $('#predictedProbability').html(Math.round(msg.data.probability*10,1)/10 + '%');
        });

            /*$.ajax({
                type : "POST",
                //url : url_for('main.update_hunch') | safe,
                data: {json_str: JSON.stringify(my_hunch)},
                contentType: 'application/json;charset=UTF-8',
                success: function(result) {
                    console.log(result);
            }
        });*/
 

            /*allCookies = document.cookie;
            console.log(allCookies.getItem('showed_played_matches').split('=')[1])*/

            upcomingPlayedMatchesTabs.click(function(){
                $(".active").removeClass("active");
                $(this).addClass("active");
            });

            if (openbtn) {
                openbtn.addEventListener( 'click', toggleMenu );
            }

            if( closebtn ) {
                closebtn.addEventListener( 'click', toggleMenu );
            }

            // close the menu element if the target it´s not the menu element or one of its descendants..
            if (!content == null) {
                content.addEventListener( 'click', function(ev) {
                    var target = ev.target;
                    if( isOpen && target !== openbtn ) {
                        toggleMenu();
                    }
                });  
            }  

            function toggleMenu() {
                if( isOpen ) {
                    classie.remove( bodyEl, 'show-menu' );
                    $(openbtn).show();
                } else {
                    classie.add( bodyEl, 'show-menu' );
                    $(openbtn).delay(200).hide();
                }
                isOpen = !isOpen;
            }


    		//no more new messages found for this user
    		socket.on('no_new_messages', function(msg) {
              navMessages.removeClass('orange');
          });

        }//end of init
    }
});  