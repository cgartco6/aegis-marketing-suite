// server/agents/SupportAgent.js
const OpenAI = require('openai');
const openai = new OpenAI(process.env.OPENAI_API_KEY);

// In-memory store for conversation history. Use a database like Redis in production!
const conversationHistory = {}; 

class SupportAgent {
    static async generateResponse(userMessage, userId) {
        // Get or create the user's conversation history
        if (!conversationHistory[userId]) {
            conversationHistory[userId] = [];
        }
        const history = conversationHistory[userId];

        // Prepare the conversation context for the AI
        const messages = [
            { 
                role: "system", 
                content: "You are Robyn, a friendly and helpful AI support agent for AEGIS Marketing. Answer the user's questions about marketing services, pricing, and their account. Be concise and helpful. If you don't know something, say so." 
            },
            ...history, // Add the past conversation
            { role: "user", content: userMessage } // Add the latest message
        ];

        try {
            const completion = await openai.chat.completions.create({
                messages: messages,
                model: "gpt-4",
                max_tokens: 250,
            });

            const aiResponse = completion.choices[0].message.content;

            // Update conversation history (keeping last 10 exchanges to manage context window)
            history.push({ role: "user", content: userMessage });
            history.push({ role: "assistant", content: aiResponse });
            if (history.length > 20) history.splice(0, 2); // Remove oldest pair

            return aiResponse;
        } catch (error) {
            console.error("Error with Support Agent:", error);
            return "I'm experiencing a technical issue right now. Please try again in a moment.";
        }
    }
}

module.exports = SupportAgent;
