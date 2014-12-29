 $(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        if (numbers_received.length >= 10){
            numbers_received.shift()
        }
        numbers_received.push(msg.number);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);
    });
    socket.on('data_updated', function(msg) {
        $('#log').append('<p> Data updated at: ' + msg.time + '</p>');
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
