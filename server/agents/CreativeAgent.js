// server/agents/CreativeAgent.js
const OpenAI = require('openai');
const openai = new OpenAI(process.env.OPENAI_API_KEY);

class CreativeAgent {
    static async generateQuote(jobBrief) {
        // Use an LLM to generate a professional quote based on the brief's complexity
        const prompt = `Based on this marketing job description: "${jobBrief.description}", generate a detailed quote in ZAR. The quote should include a breakdown of costs for video, image, and copywriting creation. Format the response as JSON: { "price": 2500, "currency": "ZAR", "breakdown": "1x 30s HD video, 3x social media posts" }`;
        
        try {
            const completion = await openai.chat.completions.create({
                messages: [{ role: "user", content: prompt }],
                model: "gpt-4",
            });
            const quote = JSON.parse(completion.choices[0].message.content);
            // TODO: Save this quote to the database linked to the user and job
            return quote;
        } catch (error) {
            console.error("Error generating quote:", error);
            return { price: 1000, currency: "ZAR", breakdown: "Standard marketing package" }; // Fallback quote
        }
    }

    static async generateImage(prompt) {
        // Generate an image using DALL-E
        const response = await openai.images.generate({
            model: "dall-e-3",
            prompt: prompt,
            size: "1024x1024",
            quality: "hd",
        });
        return response.data[0].url; // Returns the URL of the generated image
    }
    // ... methods for video, audio, etc.
}

module.exports = CreativeAgent;
