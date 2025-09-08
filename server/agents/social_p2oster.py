# agents/social_poster.py
import tweepy
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from linkedin import linkedin
import asyncio
from base_agent import AIAgent

class SocialPosterAgent(AIAgent):
    async def initialize(self):
        self.capabilities = [
            "post_to_facebook",
            "post_to_twitter",
            "post_to_instagram",
            "post_to_linkedin",
            "post_to_pinterest",
            "schedule_posts",
            "analyze_post_performance"
        ]
        
        # Initialize API connections
        self.setup_api_connections()
        
        print(f"Social Poster Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
    
    def setup_api_connections(self):
        """Setup connections to all social media APIs"""
        try:
            # Twitter API
            auth = tweepy.OAuthHandler(
                self.config.get("twitter_api_key"),
                self.config.get("twitter_api_secret")
            )
            auth.set_access_token(
                self.config.get("twitter_access_token"),
                self.config.get("twitter_access_token_secret")
            )
            self.twitter_api = tweepy.API(auth)
            
            # Facebook API
            FacebookAdsApi.init(
                self.config.get("facebook_app_id"),
                self.config.get("facebook_app_secret"),
                self.config.get("facebook_access_token")
            )
            self.facebook_page_id = self.config.get("facebook_page_id")
            
            # LinkedIn API (simplified)
            self.linkedin_api = linkedin.LinkedIn(
                token=self.config.get("linkedin_access_token")
            )
            
        except Exception as e:
            print(f"Error setting up social media APIs: {e}")
    
    async def process_task(self, task: Dict):
        task_type = task["type"]
        payload = task["payload"]
        
        if task_type == "social_post":
            return await self.post_to_social_media(payload)
        elif task_type == "social_schedule":
            return await self.schedule_post(payload)
        elif task_type == "social_analyze":
            return await self.analyze_performance(payload)
        else:
            return {"error": f"Unsupported social task type: {task_type}"}
    
    async def post_to_social_media(self, payload: Dict):
        """Post content to specified social media platforms"""
        platform = payload.get("platform", "all")
        content = payload.get("content", {})
        
        results = {}
        
        try:
            if platform in ["all", "twitter"] and "text" in content:
                results["twitter"] = await self.post_to_twitter(content["text"])
            
            if platform in ["all", "facebook"] and ("text" in content or "image" in content):
                results["facebook"] = await self.post_to_facebook(
                    content.get("text", ""), 
                    content.get("image", None)
                )
            
            if platform in ["all", "linkedin"] and "text" in content:
                results["linkedin"] = await self.post_to_linkedin(content["text"])
            
            return {"success": True, "results": results}
            
        except Exception as e:
            return {"error": f"Failed to post to social media: {str(e)}"}
    
    async def post_to_twitter(self, text: str):
        """Post to Twitter/X"""
        try:
            # For longer text, we need to handle thread creation
            if len(text) > 280:
                return await self.post_twitter_thread(text)
            
            tweet = self.twitter_api.update_status(text)
            return {"tweet_id": tweet.id, "url": f"https://twitter.com/user/status/{tweet.id}"}
        except Exception as e:
            return {"error": f"Twitter post failed: {str(e)}"}
    
    async def post_twitter_thread(self, text: str):
        """Create a thread for longer Twitter posts"""
        # Split text into 280-character chunks
        chunks = [text[i:i+280] for i in range(0, len(text), 280)]
        tweet_ids = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                tweet = self.twitter_api.update_status(chunk)
            else:
                tweet = self.twitter_api.update_status(
                    chunk, 
                    in_reply_to_status_id=tweet_ids[-1]
                )
            tweet_ids.append(tweet.id)
        
        return {"thread_id": tweet_ids, "url": f"https://twitter.com/user/status/{tweet_ids[0]}"}
    
    async def post_to_facebook(self, text: str, image_path: str = None):
        """Post to Facebook page"""
        try:
            page = Page(self.facebook_page_id)
            
            if image_path:
                # Post with image
                response = page.create_photo(
                    message=text,
                    image=open(image_path, 'rb')
                )
            else:
                # Post without image
                response = page.create_feed_post(message=text)
            
            return {"post_id": response.get("id"), "success": True}
        except Exception as e:
            return {"error": f"Facebook post failed: {str(e)}"}
