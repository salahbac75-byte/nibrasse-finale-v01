// Configuration
const API_URL = '/api';

// DOM Elements
const chatView = document.getElementById('chat-view');
const libraryView = document.getElementById('library-view');
const libraryBtn = document.getElementById('library-btn');
const backToChatBtn = document.getElementById('back-to-chat-btn');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const dropZone = document.getElementById('drop-zone');
const uploadStatus = document.getElementById('upload-status');
const documentsTableBody = document.getElementById('documents-table-body');
const newChatBtn = document.getElementById('new-chat-btn');

// State
let conversations = JSON.parse(localStorage.getItem('conversations') || '{}');
let currentConversationId = localStorage.getItem('currentConversationId') || Date.now().toString();

// Initialize
renderConversationsList();
if (conversations[currentConversationId]) {
    loadConversation(currentConversationId);
} else {
    startNewChat();
}

// Navigation
libraryBtn.addEventListener('click', () => {
    chatView.classList.add('hidden');
    libraryView.classList.remove('hidden');
    loadDocuments();
});

backToChatBtn.addEventListener('click', () => {
    libraryView.classList.add('hidden');
    chatView.classList.remove('hidden');
});

// Chat Logic
function ensureCurrentConversation() {
    if (!conversations[currentConversationId]) {
        conversations[currentConversationId] = {
            id: currentConversationId,
            title: 'Nouvelle conversation',
            messages: [],
            timestamp: Date.now()
        };
        saveConversations();
    }
}

function saveConversations() {
    localStorage.setItem('conversations', JSON.stringify(conversations));
    localStorage.setItem('currentConversationId', currentConversationId);
    renderConversationsList();
}

function renderConversationsList() {
    const list = document.getElementById('conversations-list');
    if (!list) return;

    list.innerHTML = '';

    // Sort by newest first
    const sorted = Object.values(conversations).sort((a, b) => b.timestamp - a.timestamp);

    sorted.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;
        item.innerHTML = `
            <i class="fa-regular fa-message"></i>
            <span class="conv-title">${conv.title}</span>
            <button class="delete-conv" onclick="deleteConversation(event, '${conv.id}')">
                <i class="fa-solid fa-trash"></i>
            </button>
        `;
        item.onclick = (e) => {
            if (!e.target.closest('.delete-conv')) {
                loadConversation(conv.id);
            }
        };
        list.appendChild(item);
    });
}

function loadConversation(id) {
    currentConversationId = id;
    localStorage.setItem('currentConversationId', currentConversationId);

    chatMessages.innerHTML = '';

    const conv = conversations[id];
    if (conv && conv.messages.length > 0) {
        conv.messages.forEach(msg => renderMessageToUI(msg.content, msg.isUser));
    } else {
        // Show welcome message if empty
        showWelcomeMessage();
    }
    renderConversationsList();
}

window.deleteConversation = function (e, id) {
    e.stopPropagation();
    if (confirm('Supprimer cette conversation ? / حذف هذه المحادثة؟')) {
        delete conversations[id];
        if (id === currentConversationId) {
            startNewChat();
        } else {
            saveConversations();
        }
    }
}

function startNewChat() {
    currentConversationId = Date.now().toString();
    localStorage.setItem('currentConversationId', currentConversationId);
    showWelcomeMessage();
    renderConversationsList();
}

function showWelcomeMessage() {
    chatMessages.innerHTML = `
        <div class="message system-message">
            <div class="message-content">
                <div class="welcome-card">
                    <i class="fa-solid fa-robot pulse-icon"></i>
                    <h2>Bienvenue sur NIBRASSE</h2>
                    <h2 class="arabic-text">مرحباً بكم في نبــراس</h2>
                    <p>Je suis votre assistant IA. Posez-moi des questions sur vos documents.</p>
                    <p class="arabic-text">أنا مساعدك الذكي. اسألني عن مستنداتك.</p>
                </div>
            </div>
        </div>
    `;
}

function renderMessageToUI(content, isUser) {
    // Remove welcome message if it exists and we are adding a user message
    const welcomeCard = chatMessages.querySelector('.welcome-card');
    if (welcomeCard && isUser) {
        // Don't remove it immediately, let the flow handle it, or clear if it's the first message
        if (chatMessages.children.length === 1) {
            chatMessages.innerHTML = '';
        }
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    let formattedContent = content.replace(/\n/g, '<br>');
    messageDiv.innerHTML = `<div class="message-content">${formattedContent}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(content, isUser = false) {
    // 1. Render to UI
    renderMessageToUI(content, isUser);

    // 2. Save to State
    ensureCurrentConversation();
    conversations[currentConversationId].messages.push({ content, isUser });

    // Update title if first user message
    if (isUser && conversations[currentConversationId].messages.length === 1) {
        conversations[currentConversationId].title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
    }
    conversations[currentConversationId].timestamp = Date.now();

    saveConversations();
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    addMessage(text, true);
    userInput.value = '';
    userInput.style.height = 'auto';

    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message';
    loadingDiv.innerHTML = '<div class="message-content"><i class="fa-solid fa-circle-notch fa-spin"></i> Réflexion en cours...</div>';
    chatMessages.appendChild(loadingDiv);

    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: text }),
        });

        chatMessages.removeChild(loadingDiv);

        if (!response.ok) throw new Error('Erreur réseau');

        const data = await response.json();
        addMessage(data.answer);

    } catch (error) {
        chatMessages.removeChild(loadingDiv);
        addMessage("Désolé, une erreur est survenue. Veuillez vérifier que le backend est lancé. / عذراً، حدث خطأ. يرجى التأكد من تشغيل الخادم.", false);
        console.error(error);
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// New Chat
newChatBtn.addEventListener('click', startNewChat);

// File Upload Logic
browseBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', handleFiles);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    handleFiles({ target: { files } });
});

async function handleFiles(e) {
    const files = e.target.files;
    if (!files.length) return;

    uploadStatus.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Téléchargement en cours...';

    for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                uploadStatus.innerHTML = `<span style="color: var(--success-color)"><i class="fa-solid fa-check"></i> ${file.name} téléchargé avec succès!</span>`;
                loadDocuments(); // Refresh list
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            uploadStatus.innerHTML = `<span style="color: var(--error-color)"><i class="fa-solid fa-xmark"></i> Erreur lors du téléchargement de ${file.name}</span>`;
        }
    }

    // Reset status after 3 seconds
    setTimeout(() => {
        uploadStatus.innerHTML = '';
    }, 3000);
}

// Load Documents
async function loadDocuments() {
    try {
        const response = await fetch(`${API_URL}/documents`);
        if (!response.ok) throw new Error('Failed to fetch documents');

        const data = await response.json();
        renderDocuments(data.documents);
    } catch (error) {
        console.error('Error loading documents:', error);
        documentsTableBody.innerHTML = '<tr><td colspan="4">Erreur de chargement / خطأ في التحميل</td></tr>';
    }
}

function renderDocuments(documents) {
    documentsTableBody.innerHTML = '';

    if (!documents || documents.length === 0) {
        documentsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Aucun document trouvé / لا توجد مستندات</td></tr>';
        return;
    }

    documents.forEach(doc => {
        const row = document.createElement('tr');
        const date = new Date(doc.upload_date || Date.now()).toLocaleDateString('fr-FR');

        row.innerHTML = `
            <td><i class="fa-regular fa-file-lines"></i> ${doc.filename}</td>
            <td>${date}</td>
            <td>${doc.total_chunks ? doc.total_chunks + ' chunks' : '-'}</td>
            <td><span style="color: var(--success-color)">Traité / معالج</span></td>
        `;
        documentsTableBody.appendChild(row);
    });
}
