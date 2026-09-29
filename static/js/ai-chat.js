/* AGROTEK AI — Agricultural question-and-answer chat */
(function () {
    'use strict';

    const form = document.getElementById('aiChatForm');
    const input = document.getElementById('aiChatInput');
    const sendButton = document.getElementById('aiChatSend');
    const clearButton = document.getElementById('aiChatClear');
    const messagesBox = document.getElementById('aiChatMessages');
    const suggestions = document.querySelectorAll('.ai-chat-suggestions [data-prompt]');

    if (!form || !input || !sendButton || !clearButton || !messagesBox) return;

    const greeting = 'Halo! Saya siap membantu pertanyaan pertanian. Ceritakan tanaman, lokasi, umur tanaman, dan gejala yang Anda lihat agar saran saya lebih sesuai.';
    const conversation = [];
    const maxMessages = 8;

    function addMessage(role, text, state) {
        const message = document.createElement('div');
        message.className = `ai-chat-message ${role}${state ? ` ${state}` : ''}`;
        message.textContent = text;
        messagesBox.appendChild(message);
        messagesBox.scrollTop = messagesBox.scrollHeight;
        return message;
    }

    function resetChat() {
        conversation.length = 0;
        messagesBox.replaceChildren();
        addMessage('assistant', greeting);
        input.value = '';
        input.focus();
    }

    clearButton.addEventListener('click', resetChat);

    suggestions.forEach((button) => {
        button.addEventListener('click', () => {
            input.value = button.dataset.prompt || '';
            input.focus();
        });
    });

    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            form.requestSubmit();
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const text = input.value.trim();
        if (!text || sendButton.disabled) return;

        const nextConversation = [
            ...conversation.slice(-(maxMessages - 2)),
            { role: 'user', content: text },
        ];
        addMessage('user', text);
        input.value = '';
        input.disabled = true;
        sendButton.disabled = true;
        clearButton.disabled = true;
        suggestions.forEach((button) => { button.disabled = true; });
        sendButton.textContent = 'Menjawab...';
        const pendingMessage = addMessage('assistant', 'Sedang menyiapkan jawaban...', 'pending');

        try {
            const response = await fetch('/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: nextConversation }),
            });
            const result = await response.json();
            pendingMessage.remove();

            if (!response.ok || !result.ok) {
                addMessage('assistant', result.error || 'Maaf, pertanyaan belum dapat dijawab. Coba lagi nanti.', 'error');
                return;
            }

            conversation.push(
                { role: 'user', content: text },
                { role: 'model', content: result.answer }
            );
            if (conversation.length > maxMessages) {
                conversation.splice(0, conversation.length - maxMessages);
            }
            addMessage('assistant', result.answer);
        } catch (error) {
            console.error('[AGROTEK] Chat request failed:', error);
            pendingMessage.remove();
            addMessage('assistant', 'Tidak dapat terhubung ke server. Periksa koneksi lalu coba lagi.', 'error');
        } finally {
            input.disabled = false;
            sendButton.disabled = false;
            clearButton.disabled = false;
            suggestions.forEach((button) => { button.disabled = false; });
            sendButton.textContent = 'Kirim';
            input.focus();
        }
    });
})();
