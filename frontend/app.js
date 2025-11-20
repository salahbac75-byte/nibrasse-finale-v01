const API_BASE_URL = 'http://127.0.0.1:8000/api';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const documentsList = document.getElementById('documentsList');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const btnSend = document.getElementById('btnSend');
const btnNewChat = document.getElementById('btnNewChat');

// State
let uploadedDocuments = [];
let currentChat = [];

// Initialize
init();

async function init() {
    setupEventListeners();
    await loadDocuments();
    loadChatHistory();
}

function setupEventListeners() {
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--accent-primary)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border-color)';
    });

    uploadArea.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        const files = Array.from(e.dataTransfer.files);
        for (const file of files) {
            await handleFile(file);
        }
    });

    btnSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    btnNewChat.addEventListener('click', startNewChat);
}

async function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        for (const file of files) {
            await handleFile(file);
        }
    }
}

async function handleFile(file) {
    if (!file.name.endsWith('.txt')) {
        showError('يرجى اختيار ملف نصي (.txt)');
        return;
    }

    const fileItem = createFileItem(file.name, 'جاري الرفع...');
    fileList.appendChild(fileItem);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('فشل رفع الملف');
        }

        const result = await response.json();

        updateFileItemStatus(fileItem, 'تم الرفع بنجاح', true);

        uploadedDocuments.push({
            id: result.data.document_id,
            name: file.name,
            chunks: result.data.total_chunks,
            uploadDate: new Date()
        });

        updateDocumentsList();
        enableChat();

        addSystemMessage(`تم رفع الملف "${file.name}" بنجاح. يحتوي على ${result.data.total_chunks} مقطع نصي.`);

    } catch (error) {
        console.error('Upload error:', error);
        updateFileItemStatus(fileItem, 'فشل الرفع', false);
        showError('حدث خطأ أثناء رفع الملف');
    }
}

function createFileItem(name, status) {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.innerHTML = `
        <span class="file-item-name">${name}</span>
        <span class="file-item-status">${status}</span>
    `;
    return div;
}

function updateFileItemStatus(fileItem, status, success) {
    const statusSpan = fileItem.querySelector('.file-item-status');
    statusSpan.textContent = status;
    if (success) {
        statusSpan.classList.add('success');
    }
}

function updateDocumentsList() {
    if (uploadedDocuments.length === 0) {
        documentsList.innerHTML = '<p class="empty-state">لا توجد مستندات بعد</p>';
        return;
    }

    documentsList.innerHTML = uploadedDocuments.map(doc => `
        <div class="document-item">
            <div class="document-name">${doc.name}</div>
            <div class="document-meta">${doc.chunks} مقطع • ${formatDate(doc.uploadDate)}</div>
        </div>
    `).join('');
}

function enableChat() {
    chatInput.disabled = false;
    btnSend.disabled = false;
    chatInput.placeholder = 'اكتب سؤالك هنا...';
}

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    addMessage('user', query);
    chatInput.value = '';

    currentChat.push({ type: 'user', content: query, timestamp: new Date() });
    saveChatHistory();

    const loadingMsg = addMessage('assistant', '<div class="loading"></div>');

    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            throw new Error('فشل الاستعلام');
        }

        const result = await response.json();

        loadingMsg.remove();

        // Extract citation numbers from answer
        const citationPattern = /\[(\d+)\]/g;
        const citations = new Set();
        let match;
        while ((match = citationPattern.exec(result.answer)) !== null) {
            citations.add(parseInt(match[1]));
        }

        // Filter to show only cited sources
        const citedSources = [];
        citations.forEach(num => {
            if (num > 0 && num <= result.context.length) {
                citedSources.push({
                    number: num,
                    content: result.context[num - 1]
                });
            }
        });

        citedSources.sort((a, b) => a.number - b.number);

        // Build sources HTML
        let sourcesHtml = '';
        if (citedSources.length > 0) {
            sourcesHtml = `
                <details class="context-preview">
                    <summary>عرض المصادر المستخدمة (${citedSources.length})</summary>
                    ${citedSources.map(source => {
                const titleMatch = source.content.match(/العنوان:\s*([^\n]+)/);
                const title = titleMatch ? titleMatch[1] : 'مصدر';

                return `
                            <div style="margin-top: 0.75rem; padding: 0.75rem; background: var(--bg-primary); border-radius: 6px; border-right: 3px solid var(--accent-primary);">
                                <strong style="color: var(--accent-primary);">[${source.number}] ${title}</strong><br>
                                <span style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem; display: block;">
                                    ${source.content.substring(0, 250)}...
                                </span>
                            </div>
                        `;
            }).join('')}
                </details>
            `;
        }

        const answerHtml = result.answer + sourcesHtml;

        addMessage('assistant', answerHtml);

        currentChat.push({ type: 'assistant', content: result.answer, timestamp: new Date() });
        saveChatHistory();

    } catch (error) {
        console.error('Query error:', error);
        loadingMsg.remove();
        addMessage('assistant', 'عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى.');
    }
}

function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        <div class="message-meta">${formatTime(new Date())}</div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

function addSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-content" style="background: var(--bg-tertiary); color: var(--text-secondary);">
            ${content}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function startNewChat() {
    currentChat = [];
    saveChatHistory();
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h2>محادثة جديدة</h2>
            <p>اطرح أسئلتك عن المستندات المرفوعة</p>
        </div>
    `;
}

function showError(message) {
    alert(message);
}

function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'الآن';
    if (minutes < 60) return `منذ ${minutes} دقيقة`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `منذ ${hours} ساعة`;

    return date.toLocaleDateString('ar-SA');
}

function formatTime(date) {
    return date.toLocaleTimeString('ar-SA', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/documents`);
        if (response.ok) {
            const data = await response.json();
            uploadedDocuments = data.documents.map(doc => ({
                id: doc.id,
                name: doc.filename,
                chunks: doc.total_chunks,
                uploadDate: new Date(doc.upload_date)
            }));
            updateDocumentsList();

            if (uploadedDocuments.length > 0) {
                enableChat();
            }
        }
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

function saveChatHistory() {
    try {
        localStorage.setItem('chatHistory', JSON.stringify(currentChat));
    } catch (error) {
        console.error('Error saving chat history:', error);
    }
}

function loadChatHistory() {
    try {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            currentChat = JSON.parse(saved);

            if (currentChat.length > 0) {
                chatMessages.innerHTML = '';
                currentChat.forEach(msg => {
                    addMessage(msg.type, msg.content);
                });
            }
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}
