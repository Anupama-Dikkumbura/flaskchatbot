$(document).ready(function(){
    var socket = io.connect("http://localhost:5000");

    socket.on('connect', function(){
        socket.send("User connected!");
    });

    socket.on('message', function(data){
        appendMessage(data);
    });

    $('#sendBtn').on('click', function(){
        var message = $('#message').val();
        if (message) {
            socket.send(message);
            appendMessage('You: ' + message);
            $('#message').val('');
        }
    });

    function appendMessage(message) {
        $('#messages').append($('<p>').text(message));
        scrollToBottom();
    }

    function scrollToBottom() {
        var messagesDiv = document.getElementById('messages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
});
