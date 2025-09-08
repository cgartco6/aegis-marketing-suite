// server/routes/api.js
const express = require('express');
const router = express.Router();
const Orchestrator = require('../agents/Orchestrator');

// POST /api/process-message
// This is the main endpoint the frontend talks to
router.post('/process-message', async (req, res) => {
    try {
        const { message, userId } = req.body;
        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        // Send the message to the Orchestrator for processing
        const result = await Orchestrator.processRequest(message, userId);
        res.json(result);

    } catch (error) {
        console.error("API Error:", error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
