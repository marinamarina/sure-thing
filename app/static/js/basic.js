(function ($) { 
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];
    
    window.setTimeout(function() {
    $(".alert").fadeTo(200, 0)
               .slideUp(200, function(){
        $(this).remove(); 
    });
}, 5000);
        
    
    /* Making room for the menu */
    $(".headroom").headroom({
        "tolerance": 20,
        "offset": 50,
        "classes": {
            "initial": "animated",
            "pinned": "slideDown",
            "unpinned": "slideUp"
        }
    });


    socket.on('data_updated', function(msg) {
        console.log('Data updated at: ' + msg.time);
    });

    var commitToBetButton = $('#commitToBet'),
        navMessages = $('#navMessages');


    commitToBetButton.on('click', function () {
            //var gender = $(this).val();
            //calculatorModel.updateGender(gender);
            socket.emit('matchCommited', $('#teamWinner').text());

    });

    //no more new messages found for this user
    socket.on('no_new_messages', function(msg) {
        navMessages.removeClass('orange');
    });

 });

