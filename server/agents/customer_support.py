import openai
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
from .base_agent import AIAgent
import asyncio

class CustomerSupportAgent(AIAgent):
    """AI agent for handling customer support in a human-like manner"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("customer_support", config)
        self.agent_name = "Robyn"
    
    async def initialize(self):
        """Initialize the customer support agent"""
        self.capabilities = [
            "answer_questions",
            "troubleshoot_issues",
            "provide_product_info",
            "handle_complaints",
            "process_returns",
            "escalate_issues",
            "collect_feedback"
        ]
        
        # Initialize AI API
        openai.api_key = self.config.get("openai_api_key")
        
        # Load knowledge base
        self.faqs = self.config.get("faqs", [])
        self.product_info = self.config.get("product_info", {})
        self.support_guidelines = self.config.get("support_guidelines", {})
        
        # Conversation history storage
        self.conversation_history = {}
        
        # Load previous conversations
        self.load_conversation_history()
        
        print(f"Customer Support Agent {self.agent_id} ({self.agent_name}) initialized with {len(self.capabilities)} capabilities")
        return {"status": "initialized", "capabilities": self.capabilities, "agent_name": self.agent_name}
    
    def load_conversation_history(self):
        """Load conversation history from storage"""
        try:
            with open("data/conversation_history.json", "r") as f:
                self.conversation_history = json.load(f)
        except FileNotFoundError:
            self.conversation_history = {}
    
    def save_conversation_history(self):
        """Save conversation history to storage"""
        with open("data/conversation_history.json", "w") as f:
            json.dump(self.conversation_history, f, indent=2)
    
    async def _process_task(self, task: Dict) -> Dict:
        """Process customer support tasks"""
        task_type = task.get("type", "")
        payload = task.get("payload", {})
        
        if task_type == "support_chat":
            return await self.handle_chat_message(payload)
        elif task_type == "support_faq":
            return await self.get_faq_answer(payload)
        elif task_type == "support_ticket":
            return await self.create_support_ticket(payload)
        elif task_type == "support_feedback":
            return await self.collect_feedback(payload)
        else:
            raise ValueError(f"Unsupported support task type: {task_type}")
    
    async def handle_chat_message(self, payload: Dict) -> Dict:
        """Handle a customer chat message"""
        user_id = payload.get("user_id", "anonymous")
        message = payload.get("message", "")
        conversation_id = payload.get("conversation_id", f"conv_{user_id}_{datetime.now().strftime('%Y%m%d')}")
        
        # Get or create conversation history
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = {
                "user_id": user_id,
                "start_time": datetime.now().isoformat(),
                "messages": [],
                "resolved": False
            }
        
        # Add user message to history
        self.conversation_history[conversation_id]["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate response
        response = await self.generate_response(conversation_id, message)
        
        # Add assistant response to history
        self.conversation_history[conversation_id]["messages"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if conversation is resolved
        is_resolved = await self.check_if_resolved(conversation_id)
        if is_resolved:
            self.conversation_history[conversation_id]["resolved"] = True
            self.conversation_history[conversation_id]["end_time"] = datetime.now().isoformat()
        
        # Save conversation history
        self.save_conversation_history()
        
        return {
            "conversation_id": conversation_id,
            "response": response,
            "resolved": is_resolved,
            "message_count": len(self.conversation_history[conversation_id]["messages"])
        }
    
    async def generate_response(self, conversation_id: str, message: str) -> str:
        """Generate a response to a customer message"""
        # Get conversation context
        context = self.get_conversation_context(conversation_id)
        
        # Prepare system message with guidelines and context
        system_message = f"""
        You are {self.agent_name}, a friendly and helpful customer support agent.
        Guidelines:
        - Be empathetic, patient, and professional
        - Use the customer's name if available
        - Answer questions based on the provided knowledge base
        - If you don't know something, admit it and offer to escalate
        - Keep responses concise but thorough
        - Always aim to resolve issues completely
        
        Knowledge Base:
        FAQs: {json.dumps(self.faqs[:5])}
        Product Info: {json.dumps(self.product_info)}
        Support Guidelines: {json.dumps(self.support_guidelines)}
        
        Current Conversation Context: {context}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"I'm experiencing technical difficulties. Please try again in a moment. Error: {str(e)}"
    
    def get_conversation_context(self, conversation_id: str) -> str:
        """Get context from conversation history"""
        if conversation_id not in self.conversation_history:
            return "New conversation"
        
        messages = self.conversation_history[conversation_id]["messages"]
        if len(messages) > 10:
            # Only use the last 10 messages for context
            messages = messages[-10:]
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        return context
    
    async def check_if_resolved(self, conversation_id: str) -> bool:
        """Check if the customer's issue has been resolved"""
        if conversation_id not in self.conversation_history:
            return False
        
        messages = self.conversation_history[conversation_id]["messages"]
        if len(messages) < 2:
            return False
        
        # Check if the customer expressed satisfaction
        last_user_message = next((msg for msg in reversed(messages) if msg["role"] == "user"), None)
        if not last_user_message:
            return False
        
        satisfaction_indicators = [
            "thank", "thanks", "thank you", "that helps", "problem solved", "issue resolved",
            "fixed", "working now", "appreciate", "great help", "perfect", "awesome"
        ]
        
        message_lower = last_user_message["content"].lower()
        if any(indicator in message_lower for indicator in satisfaction_indicators):
            return True
        
        # Check if the conversation has been going on for too long without resolution
        start_time = datetime.fromisoformat(self.conversation_history[conversation_id]["start_time"])
        if datetime.now() - start_time > timedelta(minutes=30):
            return True
        
        return False
    
    async def get_faq_answer(self, payload: Dict) -> Dict:
        """Get answer to a frequently asked question"""
        question = payload.get("question", "")
        
        # Try to find matching FAQ
        best_match = None
        best_score = 0
        
        for faq in self.faqs:
            similarity = await self.calculate_similarity(question, faq["question"])
            if similarity > best_score:
                best_score = similarity
                best_match = faq
        
        if best_match and best_score > 0.7:
            return {
                "question": question,
                "answer": best_match["answer"],
                "confidence": best_score,
                "source": "faq"
            }
        else:
            # Generate answer using AI
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful customer support agent. Answer the question based on general knowledge."},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                
                answer = response.choices[0].message.content.strip()
                
                return {
                    "question": question,
                    "answer": answer,
                    "confidence": 0.5,
                    "source": "generated"
                }
            except Exception as e:
                return {
                    "question": question,
                    "answer": "I'm sorry, I couldn't find an answer to that question. Please contact our support team for assistance.",
                    "confidence": 0,
                    "source": "error"
                }
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simplified)"""
        # This would use a proper similarity algorithm in production
        # For now, use a simple word overlap approach
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def create_support_ticket(self, payload: Dict) -> Dict:
        """Create a support ticket for escalation"""
        user_id = payload.get("user_id", "anonymous")
        issue = payload.get("issue", "")
        priority = payload.get("priority", "medium")
        
        ticket_id = f"TKT{datetime.now().strftime('%Y%m%d')}{len(self.conversation_history) + 1}"
        
        ticket = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "issue": issue,
            "priority": priority,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "assigned_to": None
        }
        
        # Save ticket (would integrate with ticketing system)
        self.save_ticket(ticket)
        
        return {
            "ticket_id": ticket_id,
            "status": "created",
            "message": f"Support ticket {ticket_id} has been created with {priority} priority"
        }
    
    def save_ticket(self, ticket: Dict):
        """Save support ticket to storage"""
        try:
            with open("data/support_tickets.json", "r") as f:
                tickets = json.load(f)
        except FileNotFoundError:
            tickets = []
        
        tickets.append(ticket)
        
        with open("data/support_tickets.json", "w") as f:
            json.dump(tickets, f, indent=2)
    
    async def collect_feedback(self, payload: Dict) -> Dict:
        """Collect customer feedback"""
        conversation_id = payload.get("conversation_id")
        rating = payload.get("rating", 0)
        comments = payload.get("comments", "")
        
        feedback = {
            "conversation_id": conversation_id,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save feedback
        self.save_feedback(feedback)
        
        # Generate response based on rating
        if rating >= 4:
            response = "Thank you for your positive feedback! We're glad we could help."
        elif rating >= 2:
            response = "Thank you for your feedback. We'll use it to improve our service."
        else:
            response = "We're sorry to hear about your experience. We'll address this issue."
        
        return {
            "feedback_id": f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "response": response,
            "rating": rating
        }
    
    def save_feedback(self, feedback: Dict):
        """Save customer feedback to storage"""
        try:
            with open("data/customer_feedback.json", "r") as f:
                feedbacks = json.load(f)
        except FileNotFoundError:
            feedbacks = []
        
        feedbacks.append(feedback)
        
        with open("data/customer_feedback.json", "w") as f:
            json.dump(feedbacks, f, indent=2)
    
    async def self_improve(self):
        """Self-improvement based on customer feedback and conversations"""
        try:
            # Analyze feedback to identify improvement areas
            with open("data/customer_feedback.json", "r") as f:
                feedbacks = json.load(f)
            
            # Calculate average rating
            if feedbacks:
                ratings = [f.get("rating", 0) for f in feedbacks]
                avg_rating = sum(ratings) / len(ratings)
                
                # Identify common issues from low ratings
                low_rating_feedbacks = [f for f in feedbacks if f.get("rating", 0) <= 2]
                common_issues = {}
                
                for feedback in low_rating_feedbacks:
                    comments = feedback.get("comments", "").lower()
                    # Simple keyword analysis (would use NLP in production)
                    if "wait" in comments or "time" in comments:
                        common_issues["response_time"] = common_issues.get("response_time", 0) + 1
                    if "know" in comments or "information" in comments:
                        common_issues["knowledge"] = common_issues.get("knowledge", 0) + 1
                    if "rude" in comments or "unhelpful" in comments:
                        common_issues["attitude"] = common_issues.get("attitude", 0) + 1
                
                # Update knowledge base with improvements
                improvements = []
                if common_issues.get("response_time", 0) > 2:
                    improvements.append("Focus on responding more quickly to customer inquiries")
                if common_issues.get("knowledge", 0) > 2:
                    improvements.append("Update knowledge base with more comprehensive information")
                if common_issues.get("attitude", 0) > 2:
                    improvements.append("Adjust response tone to be more empathetic and helpful")
                
                return {
                    "avg_rating": avg_rating,
                    "common_issues": common_issues,
                    "improvements": improvements,
                    "status": "analysis_complete"
                }
            
            return {"status": "no_feedback_data"}
            
        except FileNotFoundError:
            return {"status": "no_feedback_data"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
