# agents/content_creator.py
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from base_agent import AIAgent

class ContentCreatorAgent(AIAgent):
    async def initialize(self):
        self.capabilities = [
            "generate_text_content",
            "create_images",
            "edit_videos",
            "produce_audio_content",
            "design_graphics"
        ]
        
        # Initialize AI APIs
        openai.api_key = self.config.get("openai_api_key")
        
        print(f"Content Creator Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
    
    async def process_task(self, task: Dict):
        task_type = task["type"]
        payload = task["payload"]
        
        if task_type == "content_create_post":
            return await self.create_social_media_post(payload)
        elif task_type == "content_generate_image":
            return await self.generate_image(payload)
        elif task_type == "content_produce_video":
            return await self.produce_video_content(payload)
        elif task_type == "content_write_article":
            return await self.write_article(payload)
        else:
            return {"error": f"Unsupported content task type: {task_type}"}
    
    async def create_social_media_post(self, payload: Dict):
        """Create engaging social media content"""
        platform = payload.get("platform", "general")
        topic = payload.get("topic", "")
        tone = payload.get("tone", "professional")
        
        prompt = f"Create a {tone} social media post for {platform} about {topic}. Include relevant hashtags."
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "content": content,
                "platform": platform,
                "recommended_post_time": self.calculate_optimal_post_time(platform)
            }
        except Exception as e:
            return {"error": f"Failed to create content: {str(e)}"}
    
    async def generate_image(self, payload: Dict):
        """Generate HD images using AI"""
        description = payload.get("description", "")
        style = payload.get("style", "realistic")
        dimensions = payload.get("dimensions", "1024x1024")
        
        try:
            response = openai.Image.create(
                prompt=f"{description} in {style} style, high quality, HD",
                n=1,
                size=dimensions
            )
            
            image_url = response.data[0].url
            
            # Download and optimize image
            image_data = requests.get(image_url).content
            optimized_image = self.optimize_image(image_data)
            
            return {
                "success": True,
                "image_url": image_url,
                "optimized_image": optimized_image,
                "dimensions": dimensions
            }
        except Exception as e:
            return {"error": f"Failed to generate image: {str(e)}"}
    
    def optimize_image(self, image_data):
        """Optimize image for web and social media"""
        # Implementation for image optimization
        return image_data  # Placeholder
    
    def calculate_optimal_post_time(self, platform: str):
        """Calculate best time to post based on platform analytics"""
        # This would integrate with your analytics data
        optimal_times = {
            "facebook": "13:00-16:00",
            "twitter": "12:00-15:00",
            "instagram": "11:00-14:00",
            "linkedin": "09:00-11:00"
        }
        
        return optimal_times.get(platform.lower(), "12:00-15:00")
