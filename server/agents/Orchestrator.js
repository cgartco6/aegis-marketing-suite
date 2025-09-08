// server/agents/Orchestrator.js
const CreativeAgent = require('./CreativeAgent');
const SupportAgent = require('./SupportAgent');
// ... import other agents

class Orchestrator {
    static async processRequest(userInput, userId) {
        // Analyze the user's input to determine intent
        // This is a simple example. A real version would use an AI classification model.
        if (userInput.includes('create ad') || userInput.includes('make a video') || userInput.includes('logo')) {
            // Delegate to the Creative Agent
            const jobBrief = { description: userInput, userId: userId };
            const jobQuote = await CreativeAgent.generateQuote(jobBrief);
            return { type: 'job_quote', data: jobQuote };
        } 
        else if (userInput.includes('support') || userInput.includes('help') || userInput.includes('question')) {
            // Delegate to Robyn, the Support Agent
            const chatResponse = await SupportAgent.generateResponse(userInput, userId);
            return { type: 'support_response', data: chatResponse };
        }
        // ... other conditions for other agents
        else {
            return { type: 'error', data: 'Sorry, I did not understand your request. Please try rephrasing it.' };
        }
    }
}

module.exports = Orchestrator;
