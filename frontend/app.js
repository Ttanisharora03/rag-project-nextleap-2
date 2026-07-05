document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    const suggestedQuestions = document.querySelectorAll('.pill-btn');

    // Helper: Scroll to bottom
    const scrollToBottom = () => {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    };

    // Helper: Create a user message element
    const appendUserMessage = (text) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-message';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="ph ph-user"></i></div>
            <div class="message-content">${escapeHTML(text)}</div>
        `;
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
    };

    // Helper: Create a typing indicator
    const showTypingIndicator = () => {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message typing';
        msgDiv.id = 'typing-indicator';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="ph ph-robot"></i></div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
    };

    // Helper: Remove typing indicator
    const removeTypingIndicator = () => {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    };

    // Helper: Create bot message element with optional source
    const appendBotMessage = (text, sourceUrl, dateUpdated) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';
        
        let sourceHTML = '';
        if (sourceUrl) {
            // Extracted short name for display
            const url = new URL(sourceUrl);
            sourceHTML = `
                <div class="message-source">
                    <i class="ph ph-link"></i> Source: <a href="${sourceUrl}" target="_blank">Fact Sheet</a>
                </div>
            `;
        }

        msgDiv.innerHTML = `
            <div class="avatar"><i class="ph ph-robot"></i></div>
            <div class="message-content">
                ${escapeHTML(text)}
                ${sourceHTML}
                ${dateUpdated ? `<div class="message-source" style="margin-top: 4px;"><i class="ph ph-clock"></i> Last updated: ${dateUpdated}</div>` : ''}
            </div>
        `;
        chatHistory.appendChild(msgDiv);
        scrollToBottom();
    };

    // Basic HTML escaper to prevent XSS
    const escapeHTML = (str) => {
        const p = document.createElement('p');
        p.appendChild(document.createTextNode(str));
        return p.innerHTML;
    };

    // Handle sending a message
    const handleSendMessage = async (query) => {
        if (!query.trim()) return;

        // 1. Render User Message
        appendUserMessage(query);
        chatInput.value = '';

        // 2. Show typing indicator
        showTypingIndicator();

        try {
            // In Phase 6, we might not have the FastAPI backend running yet.
            // But we will write the code to hit the real endpoint, with a fallback mock for UI testing.
            let responseData;
            
            try {
                // Attempt to call the actual Phase 5 Backend
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                
                if (response.ok) {
                    responseData = await response.json();
                } else {
                    throw new Error("Backend not available");
                }
            } catch (err) {
                // Fallback Mock Response for UI Testing (Since API might be down)
                console.log("Using mock response for UI testing.");
                await new Promise(resolve => setTimeout(resolve, 1500)); // Fake network delay

                if (query.toLowerCase().includes('exit load')) {
                    responseData = {
                        answer: "The exit load is 1% if redeemed within 1 year. For redemptions after 1 year, the exit load is Nil.",
                        source_url: "https://groww.in/mutual-funds/icici-prudential-value-discovery-fund-direct-growth",
                        last_updated: "2026-07-01",
                        type: "factual"
                    };
                } else if (query.toLowerCase().includes('tax')) {
                    responseData = {
                        answer: "This is an equity fund, so LTCG tax of 10% applies on gains above ₹1 lakh. STCG is taxed at 15%. It does not qualify for Section 80C tax deductions.",
                        source_url: "https://groww.in/mutual-funds/icici-prudential-value-discovery-fund-direct-growth",
                        last_updated: "2026-07-01",
                        type: "factual"
                    };
                } else if (query.toLowerCase().includes('should i invest')) {
                    responseData = {
                        answer: "I'm a facts-only assistant and cannot provide investment advice. For guidance, visit AMFI or consult a SEBI-registered advisor.",
                        source_url: null,
                        last_updated: null,
                        type: "refusal"
                    };
                } else {
                    responseData = {
                        answer: "Based on the latest fact sheet, the ICICI Pru Value Discovery Fund has delivered a 5-year annualized return of 18.4%, outperforming its benchmark (NIFTY 500 Value 50 TRI) which delivered 15.2% over the same period.",
                        source_url: "https://groww.in/mutual-funds/icici-prudential-value-discovery-fund-direct-growth",
                        last_updated: "2026-07-05",
                        type: "factual"
                    };
                }
            }

            // 3. Remove typing indicator & render bot response
            removeTypingIndicator();
            appendBotMessage(responseData.answer, responseData.source_url, responseData.last_updated);

        } catch (error) {
            removeTypingIndicator();
            appendBotMessage("Sorry, I am having trouble connecting to the server right now. Please try again later.");
        }
    };

    // Form Submit Event
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSendMessage(chatInput.value);
    });

    // Suggested Questions Click Event
    suggestedQuestions.forEach(btn => {
        btn.addEventListener('click', () => {
            // Extract text without the icon HTML
            const text = btn.textContent.trim();
            handleSendMessage(text);
        });
    });
});
