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
    sendButton: document.getElementById('sendButton')
};

/**
 * Initialize the application
 */
async function init() {
    setupEventListeners();
    await loadConfig();
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
        addErrorMessage('Error loading configuration');
    }
}

/**
 * Handle send message
 */
async function handleSendMessage() {
    const message = elements.messageInput.value.trim();
    
    if (!message || state.isLoading) return;
    
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
                messages: state.messages
            })
        });
        
        if (!response.ok) throw new Error('Failed to send message');
        
        removeTypingIndicator(typingIndicator);
        
        await handleStreamedResponse(response);
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator(typingIndicator);
        addErrorMessage('Error sending message: ' + error.message);
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
                            addErrorMessage(`Error: ${data.error}`);
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
        addErrorMessage('Error reading response');
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
        // Escape HTML first
        let processed = escapeHtml(part);
        
        // Apply markdown formatting (outside of code blocks)
        // Bold: **text** or __text__
        processed = processed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        processed = processed.replace(/__(.+?)__/g, '<strong>$1</strong>');
        
        // Italics: *text* or _text_ (but not inside words)
        processed = processed.replace(/\*(.+?)\*/g, '<em>$1</em>');
        processed = processed.replace(/(?:^|[^a-zA-Z0-9])_(.+?)_(?:[^a-zA-Z0-9]|$)/g, (match, p1) => {
            return match[0] === '_' ? `<em>${p1}</em>` : match[0] + `<em>${p1}</em>` + (match[match.length - 1] === '_' ? '' : match[match.length - 1]);
        });
        
        // Links: [text](url)
        processed = processed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        
        // Replace newlines with <br>
        processed = processed.replace(/\n/g, '<br>');
        
        return processed;
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
