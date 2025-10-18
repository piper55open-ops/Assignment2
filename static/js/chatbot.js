document.addEventListener("DOMContentLoaded", function () {
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const chatbot = document.querySelector(".chatbot");
    const closeBtn = document.querySelector(".close-btn");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendBtn = document.querySelector(".chat-input span");

    chatbotToggler.addEventListener("click", () => chatbot.classList.toggle("show-chatbot"));
    closeBtn.addEventListener("click", () => chatbot.classList.remove("show-chatbot"));

    const inputInitHeight = chatInput.scrollHeight;

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        let chatContent =
            className === "outgoing"
                ? `<p>${message}</p>`
                : `<span class="material-symbols-outlined">smart_toy</span><p>${message}</p>`;
        chatLi.innerHTML = chatContent;
        return chatLi;
    };

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        chatInput.value = "";
        chatInput.style.height = `${inputInitHeight}px`;

        const chatBox = document.querySelector(".chatbox");
        chatBox.appendChild(createChatLi(userMessage, "outgoing"));
        chatBox.scrollTo(0, chatBox.scrollHeight);

        // Show loading while waiting
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatBox.appendChild(incomingChatLi);
        chatBox.scrollTo(0, chatBox.scrollHeight);

        fetch("/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage }),
        })
            .then((res) => res.json())
            .then((data) => {
                incomingChatLi.querySelector("p").textContent = data.response;
            })
            .catch(() => {
                incomingChatLi.querySelector("p").textContent =
                    "Sorry, I’m having trouble responding right now. Please try again soon.";
            });
    };

    sendBtn.addEventListener("click", handleChat);
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleChat();
        }
    });
});
