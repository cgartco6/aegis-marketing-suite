import openai
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import base64
from typing import Dict, Any
from .base_agent import AIAgent
from datetime import datetime
import os

class ContentCreatorAgent(AIAgent):
    """AI agent for creating high-quality content including images, videos, and text"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("content_creator", config)
        
    async def initialize(self):
        """Initialize the content creator agent"""
        self.capabilities = [
            "generate_text_content",
            "create_images",
            "edit_videos",
            "produce_audio_content",
            "design_graphics",
            "create_social_media_posts",
            "write_articles",
            "generate_video_scripts"
        ]
        
        # Initialize AI APIs
        openai.api_key = self.config.get("openai_api_key")
        
        # Load style guidelines
        self.style_guide = self.config.get("style_guide", {
            "brand_voice": "professional",
            "color_palette": ["#1a4b8c", "#34a853", "#fbbc04", "#ea4335"],
            "font_preferences": ["Roboto", "Open Sans", "Montserrat"],
            "content_guidelines": "Be concise, engaging, and professional"
        })
        
        print(f"Content Creator Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
        return {"status": "initialized", "capabilities": self.capabilities}
    
    async def _process_task(self, task: Dict) -> Dict:
        """Process content creation tasks"""
        task_type = task.get("type", "")
        payload = task.get("payload", {})
        
        if task_type == "content_create_post":
            return await self.create_social_media_post(payload)
        elif task_type == "content_generate_image":
            return await self.generate_image(payload)
        elif task_type == "content_produce_video":
            return await self.produce_video_content(payload)
        elif task_type == "content_write_article":
            return await self.write_article(payload)
        elif task_type == "content_create_script":
            return await self.generate_video_script(payload)
        elif task_type == "content_design_graphic":
            return await self.design_graphic(payload)
        else:
            raise ValueError(f"Unsupported content task type: {task_type}")
    
    async def create_social_media_post(self, payload: Dict) -> Dict:
        """Create engaging social media content"""
        platform = payload.get("platform", "general")
        topic = payload.get("topic", "")
        tone = payload.get("tone", self.style_guide["brand_voice"])
        target_audience = payload.get("target_audience", "general")
        
        prompt = f"""
        Create a {tone} social media post for {platform} about {topic} targeting {target_audience}.
        Include relevant hashtags and emojis if appropriate.
        Make it engaging and platform-appropriate.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Generate hashtags
            hashtag_prompt = f"Generate 5 relevant hashtags for a post about {topic} on {platform}"
            hashtag_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": hashtag_prompt}],
                max_tokens=50,
                temperature=0.7
            )
            
            hashtags = hashtag_response.choices[0].message.content.strip()
            
            return {
                "content": content,
                "hashtags": hashtags,
                "platform": platform,
                "recommended_post_time": self.calculate_optimal_post_time(platform),
                "character_count": len(content)
            }
        except Exception as e:
            raise Exception(f"Failed to create social media content: {str(e)}")
    
    async def generate_image(self, payload: Dict) -> Dict:
        """Generate HD images using AI"""
        description = payload.get("description", "")
        style = payload.get("style", "realistic")
        dimensions = payload.get("dimensions", "1024x1024")
        aspect_ratio = payload.get("aspect_ratio", "1:1")
        
        enhanced_prompt = f"{description}, {style} style, high quality, HD, 4K, professional photography, trending on art station"
        
        try:
            response = openai.Image.create(
                prompt=enhanced_prompt,
                n=1,
                size=dimensions,
                response_format="url"
            )
            
            image_url = response['data'][0]['url']
            
            # Download image
            image_response = requests.get(image_url)
            image_data = image_response.content
            
            # Optimize image
            optimized_image = await self.optimize_image(image_data, dimensions, aspect_ratio)
            
            # Encode to base64 for easy storage/transmission
            base64_image = base64.b64encode(optimized_image).decode('utf-8')
            
            return {
                "image_url": image_url,
                "image_data": base64_image,
                "dimensions": dimensions,
                "aspect_ratio": aspect_ratio,
                "prompt_used": enhanced_prompt
            }
        except Exception as e:
            raise Exception(f"Failed to generate image: {str(e)}")
    
    async def optimize_image(self, image_data: bytes, dimensions: str, aspect_ratio: str) -> bytes:
        """Optimize image for web and social media"""
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Resize if needed
            if dimensions:
                width, height = map(int, dimensions.split('x'))
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            
            # Optimize quality
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            
            return output.getvalue()
        except Exception as e:
            print(f"Image optimization failed: {e}, returning original")
            return image_data
    
    async def produce_video_content(self, payload: Dict) -> Dict:
        """Produce video content (placeholder for video generation API integration)"""
        # This would integrate with video generation APIs like RunwayML, HeyGen, etc.
        script = payload.get("script", "")
        style = payload.get("style", "professional")
        duration = payload.get("duration", 30)
        
        # For now, return a mock response
        return {
            "status": "video_queued",
            "estimated_completion_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "video_parameters": {
                "script": script[:100] + "..." if len(script) > 100 else script,
                "style": style,
                "duration": duration
            },
            "note": "Video generation requires integration with specialized APIs"
        }
    
    async def write_article(self, payload: Dict) -> Dict:
        """Write long-form articles"""
        topic = payload.get("topic", "")
        word_count = payload.get("word_count", 1000)
        style = payload.get("style", "informative")
        
        prompt = f"""
        Write a {style} article about {topic} with approximately {word_count} words.
        Include an engaging introduction, several sections with subheadings, and a conclusion.
        Make it well-researched and informative.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=word_count * 1.2,  # Account for token-word ratio
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract title and sections
            lines = content.split('\n')
            title = lines[0] if lines else f"Article about {topic}"
            sections = [line for line in lines if line.strip() and not line.startswith('#')]
            
            return {
                "title": title.replace('#', '').strip(),
                "content": content,
                "word_count": len(content.split()),
                "section_count": len(sections)
            }
        except Exception as e:
            raise Exception(f"Failed to write article: {str(e)}")
    
    async def generate_video_script(self, payload: Dict) -> Dict:
        """Generate video scripts"""
        topic = payload.get("topic", "")
        video_type = payload.get("video_type", "explainer")
        duration = payload.get("duration", 60)
        
        prompt = f"""
        Create a {video_type} video script about {topic} with a duration of approximately {duration} seconds.
        Include scene descriptions, dialogue, and visual cues.
        Format it professionally with clear scene headings and action lines.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.8
            )
            
            script = response.choices[0].message.content.strip()
            
            return {
                "script": script,
                "estimated_duration": duration,
                "scene_count": script.count('SCENE') or script.count('INT.') or script.count('EXT.') or 1
            }
        except Exception as e:
            raise Exception(f"Failed to generate video script: {str(e)}")
    
    async def design_graphic(self, payload: Dict) -> Dict:
        """Design graphics for social media, ads, etc."""
        purpose = payload.get("purpose", "social media post")
        dimensions = payload.get("dimensions", "1080x1080")
        text = payload.get("text", "")
        
        # Create a simple graphic with text (placeholder for more advanced design)
        try:
            width, height = map(int, dimensions.split('x'))
            image = Image.new('RGB', (width, height), color=(73, 109, 137))
            draw = ImageDraw.Draw(image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
            
            # Calculate text position
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            
            # Draw text
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Encode to base64
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
            
            return {
                "graphic_data": base64_image,
                "dimensions": dimensions,
                "text_included": text,
                "purpose": purpose
            }
        except Exception as e:
            raise Exception(f"Failed to design graphic: {str(e)}")
    
    def calculate_optimal_post_time(self, platform: str) -> str:
        """Calculate best time to post based on platform analytics"""
        # This would integrate with your analytics data
        optimal_times = {
            "facebook": "13:00-16:00",
            "twitter": "12:00-15:00",
            "instagram": "11:00-14:00",
            "linkedin": "09:00-11:00",
            "tiktok": "17:00-20:00",
            "pinterest": "20:00-23:00"
        }
        
        return optimal_times.get(platform.lower(), "12:00-15:00")
