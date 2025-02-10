function scrollToBottom() {
    const chatInterface = document.getElementById('chat_interface');
    chatInterface.scrollTop = chatInterface.scrollHeight;
    console.log("It happened")
  }
document.addEventListener('DOMContentLoaded', scrollToBottom);

var socket = io();

var socket = io();  // Initialize WebSocket connection

document.addEventListener("DOMContentLoaded", function () {
    var messageForm = document.getElementById("message_form");
    var messageInput = document.getElementById("msg-input");
    var messagesDiv = document.getElementById("messages");
    var chatInterface = document.getElementById("chat_interface");
    var recipient = chatInterface.dataset.recipient;  // Get recipient from HTML

    if (!messageForm || !messageInput || !messagesDiv || !recipient) {
        console.error("Some elements are missing in the DOM.");
        return;
    }

    // Handle message sending
    messageForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var msg = messageInput.value.trim();
        if (msg === "") return;

        // Emit message via WebSocket
        socket.emit("message", { recipient: recipient, msg: msg });

        // Clear input field
        messageInput.value = "";
    });

    // Listen for incoming messages & update UI in real-time
    socket.on("message", function (data) {
        var messageElement = document.createElement("div");
        messageElement.classList.add("msg", data.sender);
        messageElement.innerHTML = `<p>${data.msg}</p>`;
        messagesDiv.appendChild(messageElement);

        // Auto-scroll to the latest message
        scrollToBottom();
    });
});
