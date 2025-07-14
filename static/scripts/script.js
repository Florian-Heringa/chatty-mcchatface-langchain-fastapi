var ws = new WebSocket("ws://localhost:8000/ws");
ws.onmessage = function(event) {
    addMessageToList(`Chatty: ${event.data}`);
};
function sendMessage(event) {
    var input = document.getElementById("messageText");
    ws.send(input.value);
    addMessageToList(`Me: ${input.value}`);
    input.value = "";
    event.preventDefault();
};

function addMessageToList(content) {
    let messageList = document.getElementById('message-list');
    let newMessageItem = document.createElement('li');
    var content = document.createTextNode(content);
    newMessageItem.appendChild(content);
    messageList.appendChild(newMessageItem);
}

let dialog = document.getElementById("alert-dialog");

function clearMemory() {
    fetch("/clear").then(_ => {
        dialog.innerHTML = "<p>Memory Cleared!</p>";
        dialog.showModal();
        setTimeout(() => dialog.close(), 1000);
    });
}


