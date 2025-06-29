// UWLbot JavaScript functionality
class UWLBot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        
        this.init();
    }
    
    init() {
        // Set welcome message time
        this.setWelcomeTime();
        
        // Event listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.messageInput.addEventListener('keypress', (e) => this.handleKeyPress(e));
        this.messageInput.addEventListener('input', () => this.handleInput());
        
        // Focus on input when page loads
        this.messageInput.focus();
        
        // Auto-scroll to bottom
        this.scrollToBottom();
    }
    
    setWelcomeTime() {
        const welcomeTimeElement = document.getElementById('welcomeTime');
        if (welcomeTimeElement) {
            welcomeTimeElement.textContent = this.getCurrentTime();
        }
    }
    
    handleSubmit(e) {
        e.preventDefault();
        const message = this.messageInput.value.trim();
        
        if (message) {
            this.sendMessage(message);
        }
    }
    
    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSubmit(e);
        }
    }
    
    handleInput() {
        // Enable/disable send button based on input
        this.sendButton.disabled = !this.messageInput.value.trim();
    }
    
    async sendMessage(message) {
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and disable send button
        this.messageInput.value = '';
        this.sendButton.disabled = true;
        
        // Show loading indicator
        this.showLoading();
        
        try {
            // Send message to Flask backend
            const response = await this.sendToBackend(message);
            
            // Hide loading indicator
            this.hideLoading();
            
            // Add bot response to chat
            this.addMessage(response.answer, 'bot');
            
        } catch (error) {
            console.error('Error sending message:', error);
            
            // Hide loading indicator
            this.hideLoading();
            
            // Show error message
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
        
        // Re-focus input
        this.messageInput.focus();
    }
    
    async sendToBackend(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = this.formatMessage(content);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.getCurrentTime();
        
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageTime);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Basic formatting for bot responses
        // Convert line breaks to <br> tags
        let formatted = content.replace(/\n/g, '<br>');
        
        // Convert **bold** to <strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert *italic* to <em>
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert lists (basic)
        formatted = formatted.replace(/^- (.+)$/gm, '• $1');
        
        return formatted;
    }
    
    showLoading() {
        this.loadingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideLoading() {
        this.loadingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        // Smooth scroll to bottom
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize the bot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new UWLBot();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Re-focus input when page becomes visible
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.focus();
        }
    }
});

// Handle window resize for mobile responsiveness
window.addEventListener('resize', () => {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

// Error handling for uncaught errors
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    // Could show a user-friendly error message here
});

// Service worker registration (optional - for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment if you want to add service worker functionality
        // navigator.serviceWorker.register('/sw.js');
    });
}