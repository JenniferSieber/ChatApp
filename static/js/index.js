const socketio = io();
const messages = document.getElementById('messages');
let bannedWords = [];

fetch('/static/js/banned_words.txt')
  .then(response => response.text())
  .then(data => {
    bannedWords = data.split('\n').map(word => word.trim()).filter(word => word.length > 0);
  })
  .catch(error => console.error('Error fetching banned words:', error));

const createMessage = (name, msg, dateCreated) => {
  const content = `
  <div class="text">
      <span>
          <strong class="msg-name">${name}:</strong> ${msg}
      </span>
      <span class="muted">
          ${dateCreated}
      </span>
  </div>
  `;
  messages.innerHTML += content;
};

socketio.on("message", (data) => {
  createMessage(data.name, data.message, data.date_created);
});

const sanitizeInput = (input) => {
  // Escape HTML and template syntax
  let sanitized = input
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/{{/g, "&#123;&#123;")
    .replace(/}}/g, "&#125;&#125;")
    .replace(/{%/g, "&#123;%")
    .replace(/%}/g, "%&#125;");

  // Replace anned words with '****'
  bannedWords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    sanitized = sanitized.replace(regex, '****');
  });

  return sanitized;
};

const sendMessage = () => {
  const message = document.getElementById('message');
  if (message.value.trim() === "") return;
  
  const sanitizedMessage = sanitizeInput(message.value);
  
  socketio.emit('message', {data: sanitizedMessage});
  message.value = "";
  
  // Reset textarea rows to 3
  message.rows = 3;
  message.style.height = 'auto';  // Reset height in case of auto-resize
};

const autoResize = (textarea) => {
  textarea.style.height = 'auto';
  textarea.style.height = (textarea.scrollHeight) + 'px';
};
