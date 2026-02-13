document.addEventListener('DOMContentLoaded', () => {
    // ================= DOM ELEMENTS =================
    const screens = {
        home: document.getElementById('home-screen'),
        loading: document.getElementById('loading-screen'),
        chat: document.getElementById('chat-screen')
    };

    // Inputs
    const nickInput = document.getElementById('input-nick');
    const interestsInput = document.getElementById('input-interests');
    const chatInput = document.getElementById('chat-input');

    // Buttons
    const startBtn = document.getElementById('start-btn');
    const cancelSearchBtn = document.getElementById('cancel-search-btn');
    const skipBtn = document.getElementById('skip-btn');
    const sendBtn = document.getElementById('send-btn');

    // Display Areas
    const messageLog = document.getElementById('messagelog');
    const partnerNameDisplay = document.getElementById('partner-name');
    const partnerStatusDisplay = document.getElementById('partner-status');
    const loadingStatus = document.getElementById('loading-status');

    // ================= STATE =================
    let socket = null;
    let isConnected = false;
    let typingTimeout = null;

    // ================= NAVIGATION =================
    function showScreen(screenName) {
        Object.values(screens).forEach(s => s.classList.remove('active'));
        screens[screenName].classList.add('active');
    }

    // ================= WEBSOCKET LOGIC =================
    function connect() {
        if (socket) {
            socket.close();
        }

        const nick = nickInput.value.trim() || "Stranger";
        const interests = interestsInput.value.trim();
        const clientId = Math.random().toString(36).substring(7);

        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Encode query params
        const url = `${proto}//${window.location.host}/ws/${clientId}?nick=${encodeURIComponent(nick)}&interests=${encodeURIComponent(interests)}`;

        socket = new WebSocket(url);

        socket.onopen = () => {
            console.log("Connected to server");
            loadingStatus.textContent = "Looking for a match...";
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleMessage(data);
        };

        socket.onclose = () => {
            console.log("Disconnected");
            isConnected = false;
            updatePartnerStatus("Disconnected", "offline");
        };

        socket.onerror = (err) => {
            console.error("WebSocket Error:", err);
            loadingStatus.textContent = "Connection Error. Retrying...";
        };
    }

    function handleMessage(data) {
        switch (data.type) {
            case 'connected':
                isConnected = true;
                partnerNameDisplay.textContent = data.partner;
                updatePartnerStatus("Online", "online");
                messageLog.innerHTML = ''; // Clear chat
                addSystemMessage(`You are talking to ${data.partner}. Say Hi!`);
                showScreen('chat');
                break;

            case 'waiting':
                showScreen('loading');
                loadingStatus.textContent = data.message || "Searching...";
                break;

            case 'message':
                addMessage(data.content, 'stranger', data.sender);
                // Clear typing indicator if message received
                updatePartnerStatus("Online", "online");
                break;

            case 'partner_disconnected':
                isConnected = false;
                updatePartnerStatus("Stranger Disconnected", "offline");
                addSystemMessage("Partner disconnected. Press ESC to find new.");
                break;

            case 'typing':
                if (data.state) {
                    updatePartnerStatus("Typing...", "typing");
                } else {
                    updatePartnerStatus("Online", "online");
                }
                break;
        }
    }

    function sendMessage() {
        const content = chatInput.value.trim();
        if (content && isConnected) {
            socket.send(JSON.stringify({ type: 'message', content: content }));
            addMessage(content, 'user');
            chatInput.value = '';
        }
    }

    function skip() {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'skip' }));
            showScreen('loading');
            loadingStatus.textContent = "Skipping... finding new match";
            messageLog.innerHTML = '';
        } else {
            // Reconnect if socket closed
            connect();
            showScreen('loading');
        }
    }

    // ================= UI HELPERS =================
    function addMessage(text, type, senderName = null) {
        const div = document.createElement('div');
        div.className = `message ${type}`;

        // Allow HTML for bolding names in group chat
        if (senderName && type === 'stranger' && text.includes('<b>')) {
            div.innerHTML = text;
        } else {
            div.textContent = text;
        }

        messageLog.appendChild(div);
        scrollToBottom();
    }

    function addSystemMessage(text) {
        const div = document.createElement('div');
        div.className = 'system-message';
        div.textContent = text;
        messageLog.appendChild(div);
        scrollToBottom();
    }

    function scrollToBottom() {
        messageLog.scrollTop = messageLog.scrollHeight;
    }

    function updatePartnerStatus(text, state) {
        partnerStatusDisplay.textContent = text;

        // Visual indicator could be added here
        if (state === 'typing') {
            partnerStatusDisplay.style.color = 'var(--primary)';
        } else if (state === 'offline') {
            partnerStatusDisplay.style.color = 'var(--danger)';
        } else {
            partnerStatusDisplay.style.color = 'var(--primary)';
        }
    }

    // ================= EVENTS =================
    startBtn.addEventListener('click', () => {
        showScreen('loading');
        connect();
    });

    cancelSearchBtn.addEventListener('click', () => {
        if (socket) socket.close();
        showScreen('home');
    });

    sendBtn.addEventListener('click', sendMessage);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Typing Indicator Logic
    chatInput.addEventListener('input', () => {
        if (!isConnected) return;

        // Send typing ON
        socket.send(JSON.stringify({ type: 'typing', state: true }));

        // Debounce typing OFF
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            if (isConnected) {
                socket.send(JSON.stringify({ type: 'typing', state: false }));
            }
        }, 1000); // 1 second after stop typing
    });

    skipBtn.addEventListener('click', skip);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (screens.chat.classList.contains('active')) {
                skip();
            }
        }
    });
});
