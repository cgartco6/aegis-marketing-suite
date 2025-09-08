import uuid
from datetime import datetime
from typing import Dict, Any, List
import json
import asyncio

class AIAgent:
    """Base class for all AI agents in the AEGIS system"""
    
    def __init__(self, agent_type: str, config: Dict[str, Any]):
        self.agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.config = config
        self.capabilities = []
        self.performance_stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0,
            "average_processing_time": 0
        }
        self.knowledge_base = f"knowledge/{self.agent_type}_knowledge.json"
        self.load_knowledge()
        
    def load_knowledge(self):
        """Load agent-specific knowledge base"""
        try:
            with open(self.knowledge_base, 'r') as f:
                self.knowledge = json.load(f)
        except FileNotFoundError:
            self.knowledge = {
                "best_practices": {},
                "error_solutions": {},
                "performance_data": [],
                "learning_data": []
            }
    
    def save_knowledge(self):
        """Save agent-specific knowledge base"""
        with open(self.knowledge_base, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    async def initialize(self):
        """Initialize the agent with its specific capabilities"""
        raise NotImplementedError("Subclasses must implement initialize()")
    
    async def process_task(self, task: Dict) -> Dict:
        """Process a specific task"""
        start_time = datetime.now()
        
        try:
            result = await self._process_task(task)
            end_time = datetime.now()
            
            # Update performance stats
            processing_time = (end_time - start_time).total_seconds()
            self.performance_stats["tasks_completed"] += 1
            self.performance_stats["total_processing_time"] += processing_time
            self.performance_stats["average_processing_time"] = (
                self.performance_stats["total_processing_time"] / 
                self.performance_stats["tasks_completed"]
            )
            
            # Add to knowledge base
            self.knowledge["performance_data"].append({
                "task_type": task.get("type", "unknown"),
                "processing_time": processing_time,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            self.save_knowledge()
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "processing_time": processing_time,
                "result": result
            }
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Update performance stats
            self.performance_stats["tasks_failed"] += 1
            
            # Add to knowledge base
            self.knowledge["performance_data"].append({
                "task_type": task.get("type", "unknown"),
                "processing_time": processing_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            # Store error solution if available
            error_key = str(type(e).__name__)
            if error_key not in self.knowledge["error_solutions"]:
                self.knowledge["error_solutions"][error_key] = {
                    "error": str(e),
                    "solutions": [],
                    "occurrences": 0
                }
            
            self.knowledge["error_solutions"][error_key]["occurrences"] += 1
            self.save_knowledge()
            
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e),
                "processing_time": processing_time
            }
    
    async def _process_task(self, task: Dict) -> Any:
        """Internal task processing method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _process_task()")
    
    async def self_improve(self):
        """Agent-specific self-improvement routines"""
        # Analyze performance data to identify improvement opportunities
        recent_data = [d for d in self.knowledge["performance_data"] 
                      if datetime.fromisoformat(d["timestamp"]) > 
                      datetime.now() - timedelta(days=7)]
        
        if recent_data:
            # Calculate success rate
            success_count = sum(1 for d in recent_data if d["success"])
            success_rate = success_count / len(recent_data)
            
            # Calculate average processing time for successful tasks
            avg_time = sum(d["processing_time"] for d in recent_data if d["success"]) / success_count
            
            # Identify areas for improvement
            if success_rate < 0.9:
                print(f"Agent {self.agent_id} needs improvement. Success rate: {success_rate:.2f}")
                # Implement improvement strategies here
            
            if avg_time > 10:  # More than 10 seconds average
                print(f"Agent {self.agent_id} is slow. Average processing time: {avg_time:.2f}s")
                # Implement optimization strategies here
        
        return {"improvement_status": "completed"}
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "performance": self.performance_stats,
            "knowledge_size": len(self.knowledge["performance_data"])
        }
