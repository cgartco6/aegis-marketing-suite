import tweepy
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
import asyncio
from typing import Dict, Any
from .base_agent import AIAgent
from datetime import datetime, timedelta
import requests
import json

class SocialPosterAgent(AIAgent):
    """AI agent for posting content to social media platforms"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("social_poster", config)
    
    async def initialize(self):
        """Initialize the social poster agent"""
        self.capabilities = [
            "post_to_facebook",
            "post_to_twitter",
            "post_to_instagram",
            "post_to_linkedin",
            "post_to_pinterest",
            "post_to_tiktok",
            "schedule_posts",
            "analyze_post_performance",
            "manage_multiple_accounts"
        ]
        
        # Initialize API connections
        self.setup_api_connections()
        
        # Initialize scheduling system
        self.scheduled_posts = []
        self.load_scheduled_posts()
        
        # Start background scheduler
        asyncio.create_task(self.scheduler_loop())
        
        print(f"Social Poster Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
        return {"status": "initialized", "capabilities": self.capabilities}
    
    def setup_api_connections(self):
        """Setup connections to all social media APIs"""
        self.apis = {}
        
        try:
            # Twitter API
            if all(k in self.config for k in ["twitter_api_key", "twitter_api_secret", 
                                            "twitter_access_token", "twitter_access_token_secret"]):
                auth = tweepy.OAuthHandler(
                    self.config["twitter_api_key"],
                    self.config["twitter_api_secret"]
                )
                auth.set_access_token(
                    self.config["twitter_access_token"],
                    self.config["twitter_access_token_secret"]
                )
                self.apis["twitter"] = tweepy.API(auth)
            
            # Facebook API
            if all(k in self.config for k in ["facebook_app_id", "facebook_app_secret", 
                                            "facebook_access_token", "facebook_page_id"]):
                FacebookAdsApi.init(
                    self.config["facebook_app_id"],
                    self.config["facebook_app_secret"],
                    self.config["facebook_access_token"]
                )
                self.apis["facebook"] = Page(self.config["facebook_page_id"])
            
            # Additional APIs would be initialized here
            # Instagram, LinkedIn, Pinterest, TikTok, etc.
            
        except Exception as e:
            print(f"Error setting up social media APIs: {e}")
    
    def load_scheduled_posts(self):
        """Load scheduled posts from storage"""
        try:
            with open("data/scheduled_posts.json", "r") as f:
                self.scheduled_posts = json.load(f)
        except FileNotFoundError:
            self.scheduled_posts = []
    
    def save_scheduled_posts(self):
        """Save scheduled posts to storage"""
        with open("data/scheduled_posts.json", "w") as f:
            json.dump(self.scheduled_posts, f, indent=2)
    
    async def scheduler_loop(self):
        """Background task to check for scheduled posts"""
        while True:
            now = datetime.now()
            
            # Check for posts that are due
            for post in self.scheduled_posts[:]:  # Iterate over a copy
                scheduled_time = datetime.fromisoformat(post["scheduled_time"])
                
                if now >= scheduled_time:
                    # Post is due, execute it
                    try:
                        result = await self.post_to_social_media({
                            "platform": post["platform"],
                            "content": post["content"]
                        })
                        
                        # Remove from scheduled posts
                        self.scheduled_posts.remove(post)
                        self.save_scheduled_posts()
                        
                        print(f"Posted scheduled content to {post['platform']}: {result.get('id', 'unknown')}")
                        
                    except Exception as e:
                        print(f"Failed to post scheduled content: {e}")
                        # Keep in schedule for retry or mark as failed
            
            # Wait for 1 minute before checking again
            await asyncio.sleep(60)
    
    async def _process_task(self, task: Dict) -> Dict:
        """Process social media tasks"""
        task_type = task.get("type", "")
        payload = task.get("payload", {})
        
        if task_type == "social_post":
            return await self.post_to_social_media(payload)
        elif task_type == "social_schedule":
            return await self.schedule_post(payload)
        elif task_type == "social_analyze":
            return await self.analyze_performance(payload)
        elif task_type == "social_engagement":
            return await self.analyze_engagement(payload)
        else:
            raise ValueError(f"Unsupported social task type: {task_type}")
    
    async def post_to_social_media(self, payload: Dict) -> Dict:
        """Post content to specified social media platforms"""
        platform = payload.get("platform", "all")
        content = payload.get("content", {})
        
        results = {}
        
        try:
            if platform in ["all", "twitter"] and "text" in content and "twitter" in self.apis:
                results["twitter"] = await self.post_to_twitter(content["text"])
            
            if platform in ["all", "facebook"] and "facebook" in self.apis:
                results["facebook"] = await self.post_to_facebook(
                    content.get("text", ""), 
                    content.get("image", None)
                )
            
            # Add other platforms here
            if platform in ["all", "linkedin"] and "linkedin" in self.config:
                results["linkedin"] = await self.post_to_linkedin(content.get("text", ""))
            
            return {"success": True, "results": results}
            
        except Exception as e:
            raise Exception(f"Failed to post to social media: {str(e)}")
    
    async def post_to_twitter(self, text: str) -> Dict:
        """Post to Twitter/X"""
        try:
            # For longer text, we need to handle thread creation
            if len(text) > 280:
                return await self.post_twitter_thread(text)
            
            tweet = self.apis["twitter"].update_status(text)
            return {"id": tweet.id, "url": f"https://twitter.com/user/status/{tweet.id}"}
        except Exception as e:
            raise Exception(f"Twitter post failed: {str(e)}")
    
    async def post_twitter_thread(self, text: str) -> Dict:
        """Create a thread for longer Twitter posts"""
        # Split text into 280-character chunks
        chunks = [text[i:i+280] for i in range(0, len(text), 280)]
        tweet_ids = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                tweet = self.apis["twitter"].update_status(chunk)
            else:
                tweet = self.apis["twitter"].update_status(
                    chunk, 
                    in_reply_to_status_id=tweet_ids[-1]
                )
            tweet_ids.append(tweet.id)
        
        return {"thread_id": tweet_ids, "url": f"https://twitter.com/user/status/{tweet_ids[0]}"}
    
    async def post_to_facebook(self, text: str, image_data: str = None) -> Dict:
        """Post to Facebook page"""
        try:
            if image_data:
                # Post with image (simplified - would need proper image handling)
                # This is a placeholder implementation
                result = self.apis["facebook"].create_photo(
                    message=text,
                    image_url=image_data if image_data.startswith('http') else None
                )
            else:
                # Post without image
                result = self.apis["facebook"].create_feed_post(message=text)
            
            return {"id": result.get("id"), "success": True}
        except Exception as e:
            raise Exception(f"Facebook post failed: {str(e)}")
    
    async def post_to_linkedin(self, text: str) -> Dict:
        """Post to LinkedIn (placeholder implementation)"""
        # This would use the LinkedIn API
        # For now, return a mock response
        return {
            "status": "success",
            "platform": "linkedin",
            "note": "LinkedIn integration requires API setup"
        }
    
    async def schedule_post(self, payload: Dict) -> Dict:
        """Schedule a post for future publishing"""
        platform = payload.get("platform", "facebook")
        content = payload.get("content", {})
        scheduled_time = payload.get("scheduled_time")
        
        if not scheduled_time:
            raise ValueError("Scheduled time is required")
        
        # Validate scheduled time is in the future
        scheduled_dt = datetime.fromisoformat(scheduled_time)
        if scheduled_dt <= datetime.now():
            raise ValueError("Scheduled time must be in the future")
        
        # Add to scheduled posts
        post_data = {
            "platform": platform,
            "content": content,
            "scheduled_time": scheduled_time,
            "created_at": datetime.now().isoformat()
        }
        
        self.scheduled_posts.append(post_data)
        self.save_scheduled_posts()
        
        return {
            "status": "scheduled",
            "scheduled_time": scheduled_time,
            "post_id": f"sch_{len(self.scheduled_posts)}"
        }
    
    async def analyze_performance(self, payload: Dict) -> Dict:
        """Analyze post performance across platforms"""
        platform = payload.get("platform", "all")
        time_range = payload.get("time_range", "7d")
        
        # This would integrate with each platform's analytics API
        # For now, return mock data
        
        mock_data = {
            "facebook": {
                "impressions": 1250,
                "engagement": 45,
                "clicks": 120,
                "reach": 980
            },
            "twitter": {
                "impressions": 870,
                "engagement": 32,
                "clicks": 65,
                "reach": 650
            },
            "instagram": {
                "impressions": 2100,
                "engagement": 120,
                "clicks": 85,
                "reach": 1500
            }
        }
        
        if platform == "all":
            return mock_data
        else:
            return {platform: mock_data.get(platform, {})}
    
    async def analyze_engagement(self, payload: Dict) -> Dict:
        """Analyze engagement metrics and suggest improvements"""
        platform = payload.get("platform", "all")
        
        # This would analyze engagement patterns and provide suggestions
        # For now, return mock recommendations
        
        recommendations = {
            "facebook": [
                "Post more video content - videos get 3x more engagement on Facebook",
                "Try posting between 1-3 PM for optimal engagement",
                "Use more questions in your posts to encourage comments"
            ],
            "twitter": [
                "Join trending conversations to increase visibility",
                "Use 1-2 hashtags per tweet for best results",
                "Post during lunch hours (12-1 PM) for higher engagement"
            ],
            "instagram": [
                "Use Reels for higher reach - they're prioritized by the algorithm",
                "Post consistently at the same time each day",
                "Use all 30 hashtags allowed for maximum discoverability"
            ]
        }
        
        if platform == "all":
            return recommendations
        else:
            return {platform: recommendations.get(platform, [])}
