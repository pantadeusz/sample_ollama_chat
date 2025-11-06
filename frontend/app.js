/**
 * Ollama Chat Frontend Application
 * Pure JavaScript (ECMAScript) implementation
 */

// Configuration
const API_BASE_URL = '/api';

// State management
const state = {
    messages: [],
    currentModel: '',
    isLoading: false,
    config: null,
    starterMessage: 'Hello! I\'m ready to chat. Choose a model and send a message.'
};

// DOM elements
const elements = {
    messages: document.getElementById('messages'),
    messageInput: document.getElementById('messageInput'),
    sendButton: document.getElementById('sendButton'),
    modelSelect: document.getElementById('modelSelect'),
    reloadConfigButton: document.getElementById('reloadConfig')
};

/**
 * Initialize the application
 */
async function init() {
    setupEventListeners();
    await loadConfig();
    await loadModels();
    addSystemMessage(state.starterMessage);
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    elements.sendButton.addEventListener('click', handleSendMessage);
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    elements.modelSelect.addEventListener('change', handleModelChange);
    elements.reloadConfigButton.addEventListener('click', handleReloadConfig);
    
    // Auto-resize textarea
    elements.messageInput.addEventListener('input', autoResizeTextarea);
}

/**
 * Auto-resize textarea based on content
 */
function autoResizeTextarea() {
    elements.messageInput.style.height = 'auto';
    elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 150) + 'px';
}

/**
 * Load configuration from backend
 */
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/config`);
        if (!response.ok) throw new Error('Failed to load config');
        
        state.config = await response.json();
        state.currentModel = state.config.model;
        state.starterMessage = state.config.starter_message || state.starterMessage;
    } catch (error) {
        console.error('Error loading config:', error);
        addErrorMessage('Błąd ładowania konfiguracji');
    }
}

/**
 * Load available models from Ollama
 */
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`);
        if (!response.ok) throw new Error('Failed to load models');
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        populateModelSelect(data.models || []);
    } catch (error) {
        console.error('Error loading models:', error);
        elements.modelSelect.innerHTML = '<option value="">Błąd ładowania modeli</option>';
        addErrorMessage('Nie można załadować modeli. Upewnij się, że Ollama działa.');
    }
}

/**
 * Populate model select dropdown
 */
function populateModelSelect(models) {
    elements.modelSelect.innerHTML = '';
    
    if (models.length === 0) {
        elements.modelSelect.innerHTML = '<option value="">Brak dostępnych modeli</option>';
        return;
    }
    
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.name;
        option.textContent = model.name;
        if (model.name === state.currentModel) {
            option.selected = true;
        }
        elements.modelSelect.appendChild(option);
    });
}

/**
 * Handle model selection change
 */
function handleModelChange(e) {
    state.currentModel = e.target.value;
    addSystemMessage(`Zmieniono model na: ${state.currentModel}`);
}

/**
 * Handle reload configuration
 */
async function handleReloadConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/reload-config`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed to reload config');
        
        const data = await response.json();
        state.config = data.config;
        state.currentModel = data.config.model;
        state.starterMessage = data.config.starter_message || state.starterMessage;
        
        addSystemMessage('Konfiguracja została przeładowana');
        await loadModels();
    } catch (error) {
        console.error('Error reloading config:', error);
        addErrorMessage('Błąd przeładowania konfiguracji');
    }
}

/**
 * Handle send message
 */
async function handleSendMessage() {
    const message = elements.messageInput.value.trim();
    
    if (!message || state.isLoading) return;
    
    if (!state.currentModel) {
        addErrorMessage('Wybierz model przed wysłaniem wiadomości');
        return;
    }
    
    // Add user message
    addMessage('user', message);
    elements.messageInput.value = '';
    autoResizeTextarea();
    
    // Add to state
    state.messages.push({ role: 'user', content: message });
    
    // Send to backend
    await sendChatRequest();
}

/**
 * Send chat request to backend
 */
async function sendChatRequest() {
    state.isLoading = true;
    elements.sendButton.disabled = true;
    
    const typingIndicator = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: state.messages,
                model: state.currentModel,
                stream: true
            })
        });
        
        if (!response.ok) throw new Error('Failed to send message');
        
        removeTypingIndicator(typingIndicator);
        
        await handleStreamedResponse(response);
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator(typingIndicator);
        addErrorMessage('Błąd wysyłania wiadomości: ' + error.message);
    } finally {
        state.isLoading = false;
        elements.sendButton.disabled = false;
    }
}

/**
 * Handle streamed response from backend
 */
async function handleStreamedResponse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let assistantMessage = '';
    let messageElement = null;
    
    try {
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.slice(6);
                    try {
                        const data = JSON.parse(jsonStr);
                        
                        if (data.error) {
                            addErrorMessage(`Błąd: ${data.error}`);
                            break;
                        }
                        
                        if (data.message && data.message.content) {
                            assistantMessage += data.message.content;
                            
                            if (!messageElement) {
                                messageElement = addMessage('assistant', assistantMessage);
                            } else {
                                updateMessageContent(messageElement, assistantMessage);
                            }
                        }
                        
                        if (data.done) {
                            state.messages.push({ role: 'assistant', content: assistantMessage });
                        }
                    } catch (e) {
                        console.error('Error parsing JSON:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error reading stream:', error);
        addErrorMessage('Błąd odczytu odpowiedzi');
    }
}

/**
 * Add message to chat
 */
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessageContent(content);
    
    messageDiv.appendChild(contentDiv);
    elements.messages.appendChild(messageDiv);
    
    scrollToBottom();
    
    return contentDiv;
}

/**
 * Update message content
 */
function updateMessageContent(element, content) {
    element.innerHTML = formatMessageContent(content);
    scrollToBottom();
}

/**
 * Format message content with code blocks
 */
function formatMessageContent(content) {
    // Replace triple backticks code blocks with <pre> elements
    // Supports both ```code``` and ```language\ncode\n```
    const codeBlockRegex = /```(\w+)?\n?([\s\S]*?)```/g;
    
    let formatted = content.replace(codeBlockRegex, (match, language, code) => {
        const lang = language ? ` class="language-${language}"` : '';
        return `<pre${lang}><code>${escapeHtml(code.trim())}</code></pre>`;
    });
    
    // Replace inline code (single backticks)
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Escape any remaining HTML and preserve line breaks
    const parts = formatted.split(/(<pre[\s\S]*?<\/pre>|<code>[\s\S]*?<\/code>)/);
    formatted = parts.map((part, index) => {
        if (part.startsWith('<pre') || part.startsWith('<code>')) {
            return part; // Keep pre and code tags as-is
        }
        return escapeHtml(part).replace(/\n/g, '<br>');
    }).join('');
    
    return formatted;
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Add system message
 */
function addSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    elements.messages.appendChild(messageDiv);
    
    scrollToBottom();
}

/**
 * Add error message
 */
function addErrorMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = '⚠️ ' + content;
    
    messageDiv.appendChild(contentDiv);
    elements.messages.appendChild(messageDiv);
    
    scrollToBottom();
}

/**
 * Add typing indicator
 */
function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = 'typing-indicator';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    
    messageDiv.appendChild(indicator);
    elements.messages.appendChild(messageDiv);
    
    scrollToBottom();
    
    return messageDiv;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator(element) {
    if (element && element.parentNode) {
        element.parentNode.removeChild(element);
    }
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    const container = document.getElementById('chatContainer');
    container.scrollTop = container.scrollHeight;
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
