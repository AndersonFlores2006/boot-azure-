document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const chatContainer = document.getElementById("chat-container");
  const chatToggleBtn = document.getElementById("chat-toggle-btn");
  const closeChatBtn = document.getElementById("close-chat-btn");

  // --- Chatbot visibility ---
  chatToggleBtn.addEventListener("click", () => {
    chatContainer.classList.toggle("hidden");
  });

  closeChatBtn.addEventListener("click", () => {
    chatContainer.classList.add("hidden");
  });

  // --- Chat functionality ---
  const addMessage = (message, sender) => {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", `${sender}-message`);

    const p = document.createElement("p");
    p.innerHTML = message; // Use innerHTML to render potential formatting from the bot
    messageElement.appendChild(p);

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
  };

  const sendMessage = async () => {
    const messageText = userInput.value.trim();
    if (messageText === "") return;

    addMessage(messageText, "user");
    userInput.value = "";

    try {
      // Send message to the Flask backend
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: messageText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const botReply = data.reply;

      // Display bot's response
      addMessage(botReply, "bot");
    } catch (error) {
      console.error("Error sending message:", error);
      addMessage(
        "Lo siento, no puedo conectarme con el servidor en este momento.",
        "bot"
      );
    }
  };

  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });
});
