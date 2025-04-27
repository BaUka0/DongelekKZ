document.addEventListener('DOMContentLoaded', () => {
    const chatbotWidget = document.getElementById('chatbot-widget');
    const chatHistory = document.getElementById('chatbot-history');
    const messageInput = document.getElementById('chatbot-message-input');
    const chatForm = document.getElementById('chatbot-form');
    const sendButton = document.getElementById('chatbot-send-button');
    const clearButton = document.getElementById('chatbot-clear-button');
    const toggleButton = document.getElementById('chatbot-toggle-button');
    const closeButton = document.getElementById('chatbot-close-button');
    const urlDiv = document.getElementById('chatbot-urls');
    const LOAD_HISTORY_URL = urlDiv?.dataset.loadHistoryUrl;
    const GET_RESPONSE_URL = urlDiv?.dataset.getResponseUrl;
    const CLEAR_HISTORY_URL = urlDiv?.dataset.clearHistoryUrl;
    const CSRF_TOKEN = urlDiv?.dataset.csrfToken;

    if (!chatbotWidget || !toggleButton) {
        console.log("Chatbot toggle button or widget container not found (likely user not authenticated or base.html issue). Chatbot disabled.");
        if(toggleButton) toggleButton.style.display = 'none';
        return;
    }

    if (!chatHistory || !messageInput || !chatForm || !sendButton || !clearButton || !closeButton || !LOAD_HISTORY_URL || !GET_RESPONSE_URL || !CLEAR_HISTORY_URL || !CSRF_TOKEN) {
        console.error('Chatbot configuration elements or URLs missing inside the widget! Chatbot disabled.');
        toggleButton.style.display = 'none';
        chatbotWidget.style.display = 'none';
        return;
    }

    function scrollToBottom() {
        setTimeout(() => {
             if (chatHistory) {
                chatHistory.scrollTop = chatHistory.scrollHeight;
             }
        }, 50);
    }

    function getAnchor() {
        return document.getElementById('chatbot-anchor');
    }

    function addMessageToChat(senderType, text, timestampFormatted) {
        const messageDiv = document.createElement('div');
        const senderClass = senderType === 'user' ? 'user' : 'bot';
        messageDiv.classList.add('message', senderClass);

        const senderNameDiv = document.createElement('div');
        senderNameDiv.classList.add('sender');
        senderNameDiv.textContent = senderType === 'user' ? 'You' : 'Bot';

        const textBubbleDiv = document.createElement('div');
        textBubbleDiv.classList.add('text-bubble');
        textBubbleDiv.textContent = text;

        const timestampDiv = document.createElement('div');
        timestampDiv.classList.add('timestamp');
        timestampDiv.textContent = timestampFormatted || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageDiv.appendChild(senderNameDiv);
        messageDiv.appendChild(textBubbleDiv);
        messageDiv.appendChild(timestampDiv);

        const currentAnchor = getAnchor();
        if (currentAnchor) {
            chatHistory.insertBefore(messageDiv, currentAnchor);
        } else {
            chatHistory.appendChild(messageDiv);
            if (!getAnchor()) {
                const newAnchor = document.createElement('div');
                newAnchor.id = 'chatbot-anchor';
                chatHistory.appendChild(newAnchor);
            }
        }
        scrollToBottom();
    }

    let loadingIndicator = null;
    function showLoadingIndicator() {
        hideLoadingIndicator();

        loadingIndicator = document.createElement('div');
        loadingIndicator.classList.add('message', 'typing-indicator');
        loadingIndicator.id = 'chatbot-loading-indicator';
        const senderDiv = document.createElement('div');
        senderDiv.classList.add('sender');
        senderDiv.textContent = 'Bot';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('text-bubble');
        bubbleDiv.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';

        loadingIndicator.appendChild(senderDiv);
        loadingIndicator.appendChild(bubbleDiv);

        const currentAnchor = getAnchor();
        if (currentAnchor) {
            chatHistory.insertBefore(loadingIndicator, currentAnchor);
        } else {
            chatHistory.appendChild(loadingIndicator);
        }

        scrollToBottom();
        sendButton.disabled = true;
        messageInput.disabled = true;
    }

    function hideLoadingIndicator() {
        const existingIndicator = document.getElementById('chatbot-loading-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        loadingIndicator = null;
        sendButton.disabled = false;
        messageInput.disabled = false;
    }

    async function loadHistory() {
        chatHistory.innerHTML = '<div id="chatbot-anchor"></div>';

        try {
            const response = await fetch(LOAD_HISTORY_URL, {
                 headers: {
                     'Accept': 'application/json',
                 }
            });
            if (!response.ok) {
                 let errorText = `HTTP error! status: ${response.status}`;
                 try {
                     const errorData = await response.json();
                     errorText = errorData.error || errorText;
                 } catch(e) { /* ignore json parsing error */ }
                throw new Error(errorText);
            }
            const data = await response.json();

            if (data.dialog && Array.isArray(data.dialog)) {
                data.dialog.forEach(msg => {
                    if (msg && typeof msg.sender === 'string' && typeof msg.text === 'string' && typeof msg.timestamp === 'string') {
                        addMessageToChat(msg.sender, msg.text, msg.timestamp);
                    } else {
                        console.warn("Skipping invalid message format from history:", msg);
                    }
                });
                scrollToBottom();
            } else if (data.error) {
                console.error("Error loading history from server:", data.error);
                addMessageToChat("bot", `Ошибка загрузки истории: ${data.error}`, null);
            }

        } catch (error) {
            console.error('Ошибка при выполнении запроса загрузки истории:', error);
            addMessageToChat("bot", `Не удалось загрузить историю чата: ${error.message}`, null);
        } finally {
             scrollToBottom();
        }
    }

    toggleButton.addEventListener('click', () => {
        const isVisible = chatbotWidget.style.display === 'flex';
        if (isVisible) {
            chatbotWidget.style.display = 'none';
        } else {
            chatbotWidget.style.display = 'flex';
            loadHistory();
            messageInput.focus();
        }
    });


    closeButton.addEventListener('click', () => {
        chatbotWidget.style.display = 'none';
    });

    chatForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Предотвращаем стандартную отправку формы
        const userMessage = messageInput.value.trim();
        if (!userMessage) return;

        addMessageToChat('user', userMessage, null);
        messageInput.value = '';
        showLoadingIndicator();

        try {
            // Отправляем запрос на сервер
            const response = await fetch(GET_RESPONSE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN, // Передаем CSRF токен
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ message: userMessage })
            });

            // Скрываем индикатор как только получили ответ (до его обработки)
            hideLoadingIndicator();

            if (!response.ok) {
                let errorMsg = `Ошибка сервера: ${response.status}`;
                try {
                    // Пытаемся извлечь сообщение об ошибке из JSON ответа
                    const errorData = await response.json();
                    errorMsg = `Ошибка: ${errorData.error || errorMsg}`;
                } catch (e) {
                     // Если ответ не JSON или пустой, используем статус код
                    console.warn("Could not parse error response as JSON:", e);
                 }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            if (data.response) {
                addMessageToChat('bot', data.response, data.bot_timestamp);
            } else if (data.error) {
                 console.error("Server returned JSON error with 200 OK:", data.error);
                 addMessageToChat('bot', `Ошибка: ${data.error}`, null);
            }
            else {
                console.warn("Empty or invalid response received from server:", data);
                addMessageToChat('bot', 'Извините, получен неожиданный ответ от сервера.', null);
            }

        } catch (error) {

            console.error('Ошибка при отправке/получении сообщения:', error);
            addMessageToChat('bot', `${error.message || 'Произошла неизвестная ошибка.'}`, null);
        } finally {
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    });

    clearButton.addEventListener('click', async () => {
        if (!confirm('Вы уверены, что хотите безвозвратно удалить всю историю этого диалога?')) {
            return;
        }
        try {
            const response = await fetch(CLEAR_HISTORY_URL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'Content-Type': 'application/json',
                     'Accept': 'application/json',
                },
            });

            if (!response.ok) {
                 let errorMsg = `Ошибка очистки: ${response.status}`;
                 try {
                    const errorData = await response.json();
                    errorMsg = `Ошибка: ${errorData.error || errorMsg}`;
                } catch (e) { /* ignore json parsing error */ }
                throw new Error(errorMsg);
            }

            const data = await response.json();
             chatHistory.innerHTML = '<div id="chatbot-anchor"></div>';
             alert(data.message || 'История чата очищена.');

        } catch (error) {
            console.error('Ошибка при очистке истории:', error);
            alert(`Не удалось очистить историю: ${error.message}`);
        }
    });

    const voiceButton = document.getElementById('chatbot-voice-button');

    voiceButton.addEventListener('click', function () {
        fetch('/chatbot/voice-input/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageInput.value = data.text;
                } else {
                    alert('Не удалось распознать голос. Попробуйте снова.');
                }
            })
            .catch(error => {
                console.error('Ошибка при обработке голосового ввода:', error);
                alert('Ошибка при обработке голосового ввода.');
            });
    });

});