document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");

  const addMessage = (message, sender) => {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", `${sender}-message`);

    const p = document.createElement("p");
    p.textContent = message;
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
      // Enviar el mensaje al backend de Flask
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

      // Mostrar la respuesta del bot
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
