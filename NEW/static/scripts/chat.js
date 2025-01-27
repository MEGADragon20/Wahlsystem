function scrollToBottom() {
    const chatInterface = document.getElementById('chat_interface');
    chatInterface.scrollTop = chatInterface.scrollHeight;
    console.log("It happened")
  }
document.addEventListener('DOMContentLoaded', scrollToBottom);
