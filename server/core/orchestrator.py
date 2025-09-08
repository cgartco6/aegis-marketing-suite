# core/orchestrator.py
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
from enum import Enum

class TaskPriority(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

class AIOrchestrator:
    def __init__(self):
        self.agents = {}
        self.task_queue = asyncio.PriorityQueue()
        self.learning_db = "knowledge/learning_db.json"
        self.performance_metrics = {}
        self.load_knowledge_base()
        
    def load_knowledge_base(self):
        try:
            with open(self.learning_db, 'r') as f:
                self.knowledge = json.load(f)
        except FileNotFoundError:
            self.knowledge = {
                "efficiency_patterns": {},
                "optimization_strategies": {},
                "error_resolutions": {},
                "performance_data": {}
            }
    
    def save_knowledge_base(self):
        with open(self.learning_db, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    async def deploy_agent(self, agent_type: str, config: Dict[str, Any]):
        """Dynamically deploy AI agents based on requirements"""
        agent_classes = {
            "content_creator": ContentCreatorAgent,
            "social_poster": SocialPosterAgent,
            "marketing_analyst": MarketingAnalystAgent,
            "customer_support": CustomerSupportAgent,
            "payment_processor": PaymentProcessorAgent,
            "security_monitor": SecurityMonitorAgent
        }
        
        if agent_type in agent_classes:
            agent = agent_classes[agent_type](config)
            self.agents[agent.agent_id] = agent
            await agent.initialize()
            return agent
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    async process_task(self, task_type: str, payload: Dict, priority: TaskPriority = TaskPriority.MEDIUM):
        """Process tasks through appropriate AI agents"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Queue task based on priority
        await self.task_queue.put((priority.value, {
            "task_id": task_id,
            "type": task_type,
            "payload": payload,
            "status": "queued",
            "created_at": datetime.now().isoformat()
        }))
        
        return task_id
    
    async def run(self):
        """Main orchestration loop"""
        print("AEGIS Orchestrator activated")
        
        while True:
            # Process tasks from queue
            if not self.task_queue.empty():
                priority, task = await self.task_queue.get()
                await self.dispatch_task(task)
            
            # Monitor agent performance
            await self.monitor_agents()
            
            # Self-optimization routines
            await self.self_optimize()
            
            await asyncio.sleep(0.1)  # Prevent CPU overload
    
    async def dispatch_task(self, task: Dict):
        """Dispatch tasks to appropriate AI agents"""
        task["status"] = "processing"
        
        try:
            if task["type"].startswith("content_"):
                agent = self.find_agent("content_creator")
                result = await agent.process_task(task)
            elif task["type"].startswith("social_"):
                agent = self.find_agent("social_poster")
                result = await agent.process_task(task)
            elif task["type"].startswith("analysis_"):
                agent = self.find_agent("marketing_analyst")
                result = await agent.process_task(task)
            elif task["type"].startswith("support_"):
                agent = self.find_agent("customer_support")
                result = await agent.process_task(task)
            elif task["type"].startswith("payment_"):
                agent = self.find_agent("payment_processor")
                result = await agent.process_task(task)
            else:
                result = {"error": f"Unknown task type: {task['type']}"}
            
            task["status"] = "completed"
            task["result"] = result
            
            # Learn from task execution
            self.learn_from_task(task)
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            self.learn_from_error(task, e)
    
    def learn_from_task(self, task: Dict):
        """Self-improvement through task execution learning"""
        task_type = task["type"]
        if task_type not in self.knowledge["efficiency_patterns"]:
            self.knowledge["efficiency_patterns"][task_type] = []
        
        # Store performance data for future optimization
        self.knowledge["efficiency_patterns"][task_type].append({
            "execution_time": task.get("execution_time", 0),
            "success": task["status"] == "completed",
            "timestamp": datetime.now().isoformat()
        })
        
        self.save_knowledge_base()
    
    def learn_from_error(self, task: Dict, error: Exception):
        """Learn from failures to prevent future errors"""
        error_key = str(type(error).__name__)
        if error_key not in self.knowledge["error_resolutions"]:
            self.knowledge["error_resolutions"][error_key] = []
        
        self.knowledge["error_resolutions"][error_key].append({
            "task": task,
            "error": str(error),
            "resolution": "pending",
            "timestamp": datetime.now().isoformat()
        })
        
        self.save_knowledge_base()
    
    async def self_optimize(self):
        """Continuous self-improvement routine"""
        # Analyze performance data and optimize
        for task_type, metrics in self.knowledge["efficiency_patterns"].items():
            if len(metrics) > 10:  # Enough data to analyze
                avg_time = sum(m["execution_time"] for m in metrics) / len(metrics)
                success_rate = sum(1 for m in metrics if m["success"]) / len(metrics)
                
                # Store performance metrics
                if task_type not in self.performance_metrics:
                    self.performance_metrics[task_type] = []
                
                self.performance_metrics[task_type].append({
                    "avg_execution_time": avg_time,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Implement optimizations for poorly performing tasks
                if success_rate < 0.8 or avg_time > 30:  # Thresholds for optimization
                    await self.optimize_task_processing(task_type)
    
    async def optimize_task_processing(self, task_type: str):
        """Implement optimizations for specific task types"""
        print(f"Optimizing task processing for: {task_type}")
        
        # This would involve:
        # 1. Analyzing patterns in failures
        # 2. Adjusting agent parameters
        # 3. Creating new specialized agents if needed
        # 4. Updating processing algorithms
        
        # For now, we'll just log the optimization attempt
        if task_type not in self.knowledge["optimization_strategies"]:
            self.knowledge["optimization_strategies"][task_type] = []
        
        self.knowledge["optimization_strategies"][task_type].append({
            "optimization_applied": "general_parameters_adjustment",
            "timestamp": datetime.now().isoformat(),
            "reason": "low_success_rate_or_high_execution_time"
        })
        
        self.save_knowledge_base()

# Base class for all AI agents
class AIAgent:
    def __init__(self, config: Dict[str, Any]):
        self.agent_id = f"{self.__class__.__name__.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = config
        self.capabilities = []
        self.performance_stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_processing_time": 0
        }
    
    async def initialize(self):
        """Initialize the agent with its specific capabilities"""
        raise NotImplementedError("Subclasses must implement initialize()")
    
    async def process_task(self, task: Dict):
        """Process a specific task"""
        raise NotImplementedError("Subclasses must implement process_task()")
    
    async def self_improve(self):
        """Agent-specific self-improvement routines"""
        pass
