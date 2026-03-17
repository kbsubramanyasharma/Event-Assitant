const API_BASE = '/api';

// UI Toggles
function toggleAuth(type) {
    if (type === 'signup') {
        document.getElementById('loginForm').classList.remove('active-form');
        document.getElementById('loginForm').classList.add('hidden-form');
        document.getElementById('signupForm').classList.remove('hidden-form');
        document.getElementById('signupForm').classList.add('active-form');
    } else {
        document.getElementById('signupForm').classList.remove('active-form');
        document.getElementById('signupForm').classList.add('hidden-form');
        document.getElementById('loginForm').classList.remove('hidden-form');
        document.getElementById('loginForm').classList.add('active-form');
    }
}

// Signup Logic
const signupForm = document.getElementById('signupForm');
if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('signupUsername').value;
        const email = document.getElementById('signupEmail').value;
        const password = document.getElementById('signupPassword').value;
        const errorEl = document.getElementById('signupError');
        const successEl = document.getElementById('signupSuccess');

        errorEl.innerText = '';
        successEl.innerText = '';

        try {
            const res = await fetch(`${API_BASE}/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await res.json();

            if (!res.ok) {
                errorEl.innerText = data.detail || 'Signup failed';
            } else {
                successEl.innerText = 'Account created! Logging you in...';
                // Auto login or switch to login
                setTimeout(() => toggleAuth('login'), 1500);
            }
        } catch (err) {
            errorEl.innerText = 'Network error. Please try again.';
        }
    });
}

// Login Logic
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        const errorEl = document.getElementById('loginError');
        const btn = document.querySelector('#loginForm button');

        errorEl.innerText = '';
        btn.innerText = 'Logging in...';

        try {
            const res = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (!res.ok) {
                errorEl.innerText = data.detail || 'Login failed';
                btn.innerText = 'Go to Chat';
            } else {
                localStorage.setItem('username', data.username);
                window.location.href = 'chat.html';
            }
        } catch (err) {
            errorEl.innerText = 'Network error. Please try again.';
            btn.innerText = 'Go to Chat';
        }
    });
}

function logout() {
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// Chat Logic
const chatForm = document.getElementById('chatForm');
const chatBox = document.getElementById('chatBox');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = messageInput.value.trim();
        if (!msg) return;

        const username = localStorage.getItem('username');

        // Add User message
        appendMessage(msg, 'user');
        messageInput.value = '';

        // Add typing indicator
        const typingId = showTypingIndicator();

        // Disable input while waiting
        messageInput.disabled = true;
        sendBtn.disabled = true;

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, message: msg })
            });

            removeTypingIndicator(typingId);

            if (res.ok) {
                const data = await res.json();
                appendMessage(data.response, 'bot');
            } else {
                appendMessage("Oops, I encountered an error. Please try again.", 'bot');
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            appendMessage("Internet connection issue. Could not reach server.", 'bot');
        } finally {
            messageInput.disabled = false;
            sendBtn.disabled = false;
            messageInput.focus();
        }
    });

    // Voice Recording Logic
    const micBtn = document.getElementById('micBtn');
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;

    if (micBtn && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Handle Start Recording
        const startRecording = async (e) => {
            e.preventDefault();
            if (isRecording) return;
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    stream.getTracks().forEach(track => track.stop()); // explicitly release mic
                    
                    // Stop visual indicator
                    micBtn.classList.remove('recording');
                    
                    // Show a transcribing indicator in the input
                    const originalPlaceholder = messageInput.placeholder;
                    messageInput.placeholder = "Listening and translating...";
                    messageInput.disabled = true;

                    // Send to backend
                    const formData = new FormData();
                    formData.append("file", audioBlob, "recording.webm");

                    try {
                        const res = await fetch(`${API_BASE}/transcribe`, {
                            method: 'POST',
                            body: formData
                        });
                        
                        if (res.ok) {
                            const data = await res.json();
                            if (data.text) {
                                messageInput.value = data.text;
                                // Auto-trigger send or let user review? Let's just put it in the box so they can review it before sending.
                            }
                        } else {
                            console.error("Transcription failed", await res.text());
                            alert("Failed to transcribe audio. Please try typing.");
                        }
                    } catch (err) {
                        console.error("Transcription network error", err);
                    } finally {
                        messageInput.placeholder = originalPlaceholder;
                        messageInput.disabled = false;
                        messageInput.focus();
                    }
                };

                mediaRecorder.start();
                isRecording = true;
                micBtn.classList.add('recording');
            } catch (err) {
                console.error("Microphone access denied or not available", err);
                alert("Please allow microphone access to use voice typing.");
            }
        };

        // Handle Stop Recording
        const stopRecording = (e) => {
            e.preventDefault();
            if (!isRecording || !mediaRecorder) return;
            
            mediaRecorder.stop();
            isRecording = false;
        };

        // Touch/Mouse events for Hold-to-Record
        micBtn.addEventListener('mousedown', startRecording);
        micBtn.addEventListener('mouseup', stopRecording);
        micBtn.addEventListener('mouseleave', stopRecording);
        
        micBtn.addEventListener('touchstart', startRecording);
        micBtn.addEventListener('touchend', stopRecording);
        micBtn.addEventListener('touchcancel', stopRecording);
    }
}

function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message', 'fade-in');

    const content = document.createElement('div');
    content.classList.add('message-content');
    content.innerText = text;

    div.appendChild(content);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.classList.add('message', 'bot-message');

    const content = document.createElement('div');
    content.classList.add('message-content', 'typing-indicator');

    content.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    div.appendChild(content);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

async function loadHistory() {
    const username = localStorage.getItem('username');
    if (!username) return;

    try {
        const res = await fetch(`${API_BASE}/history/${username}`);
        if (res.ok) {
            const data = await res.json();
            if (data.history && data.history.length > 0) {
                // Clear default greeting
                chatBox.innerHTML = '';

                data.history.forEach(chat => {
                    appendMessage(chat.user_message, 'user');
                    appendMessage(chat.bot_response, 'bot');
                });
            }
        }
    } catch (e) {
        console.error("Could not load history", e);
    }
}

// Navigation & Tab Switching
window.switchView = function(view) {
    const chatView = document.getElementById('chatView');
    const bookingsView = document.getElementById('bookingsView');
    const navChatBtn = document.getElementById('navChatBtn');
    const navBookingsBtn = document.getElementById('navBookingsBtn');

    if (view === 'chat') {
        chatView.style.display = 'flex';
        bookingsView.style.display = 'none';
        navChatBtn.classList.add('active');
        navBookingsBtn.classList.remove('active');
    } else if (view === 'bookings') {
        chatView.style.display = 'none';
        bookingsView.style.display = 'flex';
        navChatBtn.classList.remove('active');
        navBookingsBtn.classList.add('active');
        loadBookings();
    }
};

// Fetch & Render Bookings
async function loadBookings() {
    const username = localStorage.getItem('username');
    if (!username) return;

    const tbody = document.getElementById('bookingsTableBody');
    const emptyMsg = document.getElementById('noBookingsMsg');
    
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Loading...</td></tr>';
    emptyMsg.style.display = 'none';

    try {
        const res = await fetch(`${API_BASE}/events/${username}`);
        if (res.ok) {
            const data = await res.json();
            tbody.innerHTML = '';
            
            if (data.events && data.events.length > 0) {
                data.events.forEach(event => {
                    const row = document.createElement('tr');
                    
                    const dateCell = document.createElement('td');
                    dateCell.innerText = event.date || 'TBD';
                    
                    const locCell = document.createElement('td');
                    locCell.innerText = event.location || 'TBD';
                    
                    const guestsCell = document.createElement('td');
                    guestsCell.innerText = event.guests ? `${event.guests} people` : 'TBD';
                    
                    const priceCell = document.createElement('td');
                    priceCell.innerText = event.price ? `₹${event.price}` : 'TBD';
                    priceCell.classList.add('price-cell');
                    
                    row.appendChild(dateCell);
                    row.appendChild(locCell);
                    row.appendChild(guestsCell);
                    row.appendChild(priceCell);
                    
                    tbody.appendChild(row);
                });
            } else {
                emptyMsg.style.display = 'block';
            }
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:red;">Failed to load bookings.</td></tr>';
        }
    } catch (e) {
        console.error("Could not load bookings", e);
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:red;">Network error.</td></tr>';
    }
}
