import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import aiohttp
from .base_agent import AIAgent

class MarketingAnalystAgent(AIAgent):
    """AI agent for analyzing marketing performance and providing insights"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("marketing_analyst", config)
    
    async def initialize(self):
        """Initialize the marketing analyst agent"""
        self.capabilities = [
            "analyze_campaign_performance",
            "predict_roi",
            "identify_trends",
            "segment_audience",
            "optimize_budget",
            "generate_reports",
            "provide_recommendations"
        ]
        
        # Initialize data sources
        self.data_sources = self.config.get("data_sources", {})
        
        # Initialize models (would load trained ML models in production)
        self.models = {
            "roi_prediction": None,
            "audience_segmentation": None,
            "trend_analysis": None
        }
        
        print(f"Marketing Analyst Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
        return {"status": "initialized", "capabilities": self.capabilities}
    
    async def _process_task(self, task: Dict) -> Dict:
        """Process marketing analysis tasks"""
        task_type = task.get("type", "")
        payload = task.get("payload", {})
        
        if task_type == "analysis_campaign":
            return await self.analyze_campaign_performance(payload)
        elif task_type == "analysis_roi":
            return await self.predict_roi(payload)
        elif task_type == "analysis_trends":
            return await self.identify_trends(payload)
        elif task_type == "analysis_audience":
            return await self.segment_audience(payload)
        elif task_type == "analysis_budget":
            return await self.optimize_budget(payload)
        elif task_type == "analysis_report":
            return await self.generate_report(payload)
        else:
            raise ValueError(f"Unsupported analysis task type: {task_type}")
    
    async def analyze_campaign_performance(self, payload: Dict) -> Dict:
        """Analyze marketing campaign performance"""
        campaign_id = payload.get("campaign_id", "all")
        time_range = payload.get("time_range", "30d")
        
        # Get campaign data (would connect to actual data source)
        campaign_data = await self.get_campaign_data(campaign_id, time_range)
        
        if not campaign_data:
            return {"error": f"No data found for campaign {campaign_id}"}
        
        # Calculate key metrics
        metrics = self.calculate_metrics(campaign_data)
        
        # Compare against benchmarks
        benchmarks = self.get_industry_benchmarks()
        comparison = self.compare_to_benchmarks(metrics, benchmarks)
        
        # Identify strengths and weaknesses
        analysis = self.analyze_performance(metrics, comparison)
        
        return {
            "campaign_id": campaign_id,
            "time_range": time_range,
            "metrics": metrics,
            "benchmark_comparison": comparison,
            "analysis": analysis,
            "recommendations": self.generate_recommendations(analysis)
        }
    
    async def get_campaign_data(self, campaign_id: str, time_range: str) -> List[Dict]:
        """Get campaign data from data sources"""
        # This would connect to your actual data sources
        # For now, return mock data
        
        if campaign_id == "all":
            # Return data for all campaigns
            return [
                {
                    "date": (datetime.now() - timedelta(days=i)).isoformat()[:10],
                    "impressions": np.random.randint(1000, 5000),
                    "clicks": np.random.randint(50, 300),
                    "conversions": np.random.randint(5, 50),
                    "spend": round(np.random.uniform(100, 1000), 2),
                    "revenue": round(np.random.uniform(500, 5000), 2),
                    "campaign_id": f"campaign_{i % 3 + 1}"
                }
                for i in range(30)
            ]
        else:
            # Return data for specific campaign
            return [
                {
                    "date": (datetime.now() - timedelta(days=i)).isoformat()[:10],
                    "impressions": np.random.randint(1000, 5000),
                    "clicks": np.random.randint(50, 300),
                    "conversions": np.random.randint(5, 50),
                    "spend": round(np.random.uniform(100, 1000), 2),
                    "revenue": round(np.random.uniform(500, 5000), 2),
                    "campaign_id": campaign_id
                }
                for i in range(30)
            ]
    
    def calculate_metrics(self, data: List[Dict]) -> Dict:
        """Calculate key marketing metrics from raw data"""
        df = pd.DataFrame(data)
        
        # Basic metrics
        total_spend = df['spend'].sum()
        total_revenue = df['revenue'].sum()
        total_conversions = df['conversions'].sum()
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        
        # Derived metrics
        roas = total_revenue / total_spend if total_spend > 0 else 0
        cpa = total_spend / total_conversions if total_conversions > 0 else 0
        ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        conversion_rate = total_conversions / total_clicks if total_clicks > 0 else 0
        
        return {
            "total_spend": round(total_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "total_conversions": total_conversions,
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "roas": round(roas, 2),
            "cpa": round(cpa, 2),
            "ctr": round(ctr, 4),
            "conversion_rate": round(conversion_rate, 4)
        }
    
    def get_industry_benchmarks(self) -> Dict:
        """Get industry benchmark metrics"""
        # These would be actual industry benchmarks
        return {
            "roas": 4.0,
            "cpa": 50.0,
            "ctr": 0.02,
            "conversion_rate": 0.05
        }
    
    def compare_to_benchmarks(self, metrics: Dict, benchmarks: Dict) -> Dict:
        """Compare metrics to industry benchmarks"""
        comparison = {}
        
        for key in benchmarks:
            if key in metrics:
                value = metrics[key]
                benchmark = benchmarks[key]
                difference = value - benchmark
                percentage_diff = (difference / benchmark) * 100 if benchmark != 0 else 0
                
                comparison[key] = {
                    "value": value,
                    "benchmark": benchmark,
                    "difference": round(difference, 2),
                    "percentage_diff": round(percentage_diff, 2),
                    "status": "above" if difference > 0 else "below"
                }
        
        return comparison
    
    def analyze_performance(self, metrics: Dict, comparison: Dict) -> Dict:
        """Analyze performance and provide insights"""
        insights = []
        
        # ROAS analysis
        if metrics["roas"] > comparison["roas"]["benchmark"] * 1.2:
            insights.append("Excellent ROAS - significantly above industry average")
        elif metrics["roas"] < comparison["roas"]["benchmark"] * 0.8:
            insights.append("Low ROAS - consider optimizing targeting or creatives")
        
        # CPA analysis
        if metrics["cpa"] < comparison["cpa"]["benchmark"] * 0.8:
            insights.append("Great CPA - acquiring customers at below average cost")
        elif metrics["cpa"] > comparison["cpa"]["benchmark"] * 1.2:
            insights.append("High CPA - customer acquisition costs are above average")
        
        # CTR analysis
        if metrics["ctr"] < comparison["ctr"]["benchmark"] * 0.7:
            insights.append("Low CTR - consider improving ad creatives or targeting")
        
        # Conversion rate analysis
        if metrics["conversion_rate"] < comparison["conversion_rate"]["benchmark"] * 0.7:
            insights.append("Low conversion rate - review landing page and offer")
        
        return {
            "overall_performance": "good" if len(insights) == 0 or "Excellent" in insights[0] else "needs_improvement",
            "insights": insights,
            "score": self.calculate_performance_score(metrics, comparison)
        }
    
    def calculate_performance_score(self, metrics: Dict, comparison: Dict) -> int:
        """Calculate overall performance score (0-100)"""
        score = 75  # Start with average
        
        # Adjust based on performance vs benchmarks
        for key, comp in comparison.items():
            if comp["status"] == "above":
                score += 5
            else:
                score -= 5
        
        return max(0, min(100, score))
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        if analysis["score"] < 70:
            recommendations.extend([
                "Consider A/B testing ad creatives to improve CTR",
                "Review targeting parameters to ensure reaching the right audience",
                "Optimize landing pages for higher conversion rates",
                "Test different bidding strategies to improve ROAS"
            ])
        
        if analysis["score"] >= 85:
            recommendations.extend([
                "Scale successful campaigns to maximize ROI",
                "Explore lookalike audiences based on your best converters",
                "Test new platforms or channels with similar audience profiles"
            ])
        
        # Always include these general recommendations
        recommendations.extend([
            "Regularly review and update your keyword strategy",
            "Monitor competitor activity and adjust accordingly",
            "Use seasonal trends to inform campaign planning"
        ])
        
        return recommendations
    
    async def predict_roi(self, payload: Dict) -> Dict:
        """Predict ROI for a proposed campaign"""
        budget = payload.get("budget", 1000)
        channel = payload.get("channel", "facebook")
        target_audience = payload.get("target_audience", "general")
        
        # This would use a trained ML model in production
        # For now, use historical data and simple forecasting
        
        # Get historical performance data
        historical_data = await self.get_campaign_data("all", "90d")
        channel_data = [d for d in historical_data if d.get("channel", "facebook") == channel]
        
        if not channel_data:
            return {"error": f"No historical data for channel {channel}"}
        
        # Calculate average metrics for this channel
        df = pd.DataFrame(channel_data)
        avg_roas = df['revenue'].sum() / df['spend'].sum() if df['spend'].sum() > 0 else 0
        
        # Predict ROI based on historical performance
        predicted_revenue = budget * avg_roas
        predicted_roi = (predicted_revenue - budget) / budget * 100 if budget > 0 else 0
        
        confidence = 0.7  # Based on data quality and quantity
        
        return {
            "predicted_revenue": round(predicted_revenue, 2),
            "predicted_roi": round(predicted_roi, 2),
            "confidence": round(confidence, 2),
            "based_on_historical_roas": round(avg_roas, 2),
            "recommendation": "proceed" if predicted_roi > 0 else "reconsider"
        }
    
    async def identify_trends(self, payload: Dict) -> Dict:
        """Identify trends in marketing performance"""
        time_range = payload.get("time_range", "90d")
        
        # Get historical data
        historical_data = await self.get_campaign_data("all", time_range)
        df = pd.DataFrame(historical_data)
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate daily metrics
        daily_metrics = df.groupby('date').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'clicks': 'sum',
            'impressions': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calculate derived metrics
        daily_metrics['roas'] = daily_metrics['revenue'] / daily_metrics['spend']
        daily_metrics['ctr'] = daily_metrics['clicks'] / daily_metrics['impressions']
        daily_metrics['conversion_rate'] = daily_metrics['conversions'] / daily_metrics['clicks']
        
        # Identify trends (simplified)
        trends = {}
        
        for metric in ['roas', 'ctr', 'conversion_rate']:
            values = daily_metrics[metric].dropna()
            if len(values) > 1:
                # Simple linear trend calculation
                x = np.arange(len(values))
                slope, intercept = np.polyfit(x, values, 1)
                trend_direction = "increasing" if slope > 0 else "decreasing"
                
                trends[metric] = {
                    "trend": trend_direction,
                    "strength": abs(slope) * 10,  # Arbitrary scaling
                    "current_value": values.iloc[-1],
                    "change_since_start": values.iloc[-1] - values.iloc[0]
                }
        
        return {
            "time_range": time_range,
            "trends": trends,
            "insights": self.generate_trend_insights(trends)
        }
    
    def generate_trend_insights(self, trends: Dict) -> List[str]:
        """Generate insights from identified trends"""
        insights = []
        
        for metric, trend in trends.items():
            if trend["trend"] == "increasing" and trend["strength"] > 0.5:
                insights.append(f"{metric.upper()} is showing strong positive trend - consider increasing investment")
            elif trend["trend"] == "decreasing" and trend["strength"] > 0.5:
                insights.append(f"{metric.upper()} is declining - investigate root causes and implement corrective measures")
        
        return insights
    
    async def segment_audience(self, payload: Dict) -> Dict:
        """Segment audience based on behavior and demographics"""
        # This would use actual customer data and clustering algorithms
        # For now, return mock segments
        
        segments = {
            "high_value_customers": {
                "size": "15%",
                "lifetime_value": "R5,000+",
                "characteristics": ["frequent purchases", "high average order value", "brand loyal"],
                "recommendations": ["Create loyalty program", "Offer exclusive products", "Personalized communication"]
            },
            "at_risk_customers": {
                "size": "20%",
                "lifetime_value": "R500-R1,000",
                "characteristics": ["declining engagement", "not purchased recently", "price sensitive"],
                "recommendations": ["Win-back campaign", "Special discounts", "Re-engagement emails"]
            },
            "new_customers": {
                "size": "25%",
                "lifetime_value": "R100-R500",
                "characteristics": ["recent first purchase", "exploring brand", "responsive to promotions"],
                "recommendations": ["Welcome series", "Educational content", "Introduction to product range"]
            },
            "prospects": {
                "size": "40%",
                "lifetime_value": "R0",
                "characteristics": ["engaged but not purchased", "price comparing", "need nurturing"],
                "recommendations": ["Lead nurturing campaign", "Content marketing", "Free trial offers"]
            }
        }
        
        return {
            "segments": segments,
            "total_audience_size": "10,000",  # Mock data
            "segmentation_criteria": ["purchase history", "engagement level", "demographics"]
        }
    
    async def optimize_budget(self, payload: Dict) -> Dict:
        """Optimize marketing budget allocation"""
        total_budget = payload.get("total_budget", 10000)
        current_allocation = payload.get("current_allocation", {
            "facebook": 40,
            "google": 30,
            "instagram": 20,
            "email": 10
        })
        
        # Get performance data by channel
        historical_data = await self.get_campaign_data("all", "90d")
        df = pd.DataFrame(historical_data)
        
        # Calculate ROAS by channel (simplified)
        channel_performance = {}
        for channel in current_allocation.keys():
            channel_data = df[df['channel'] == channel] if 'channel' in df else df
            if len(channel_data) > 0:
                total_spend = channel_data['spend'].sum()
                total_revenue = channel_data['revenue'].sum()
                roas = total_revenue / total_spend if total_spend > 0 else 0
                channel_performance[channel] = roas
        
        # If no channel data, use mock performance
        if not channel_performance:
            channel_performance = {
                "facebook": 4.2,
                "google": 3.8,
                "instagram": 5.1,
                "email": 7.5
            }
        
        # Calculate optimal allocation based on performance
        total_roas = sum(channel_performance.values())
        optimal_allocation = {}
        
        for channel, roas in channel_performance.items():
            optimal_allocation[channel] = round((roas / total_roas) * 100, 1)
        
        # Calculate expected improvement
        current_roi = sum(current_allocation[channel] * channel_performance.get(channel, 0) 
                         for channel in current_allocation) / 100
        optimal_roi = sum(optimal_allocation[channel] * channel_performance.get(channel, 0) 
                         for channel in optimal_allocation) / 100
        improvement = ((optimal_roi - current_roi) / current_roi) * 100 if current_roi > 0 else 0
        
        return {
            "current_allocation": current_allocation,
            "optimal_allocation": optimal_allocation,
            "channel_performance": channel_performance,
            "expected_improvement": round(improvement, 1),
            "recommended_changes": self.generate_budget_recommendations(current_allocation, optimal_allocation)
        }
    
    def generate_budget_recommendations(self, current: Dict, optimal: Dict) -> List[str]:
        """Generate specific budget reallocation recommendations"""
        recommendations = []
        
        for channel in current:
            current_pct = current[channel]
            optimal_pct = optimal.get(channel, 0)
            change = optimal_pct - current_pct
            
            if change > 5:
                recommendations.append(f"Increase {channel} budget by {change:.1f}%")
            elif change < -5:
                recommendations.append(f"Decrease {channel} budget by {abs(change):.1f}%")
        
        return recommendations
    
    async def generate_report(self, payload: Dict) -> Dict:
        """Generate comprehensive marketing performance report"""
        report_type = payload.get("report_type", "comprehensive")
        time_range = payload.get("time_range", "30d")
        
        # Gather all relevant data
        campaign_performance = await self.analyze_campaign_performance({
            "campaign_id": "all",
            "time_range": time_range
        })
        
        trends = await self.identify_trends({"time_range": time_range})
        audience_segments = await self.segment_audience({})
        budget_optimization = await self.optimize_budget({"total_budget": 10000})
        
        # Compile comprehensive report
        report = {
            "executive_summary": self.generate_executive_summary(campaign_performance, trends),
            "time_period": time_range,
            "campaign_performance": campaign_performance,
            "trend_analysis": trends,
            "audience_insights": audience_segments,
            "budget_recommendations": budget_optimization,
            "key_takeaways": self.extract_key_takeaways(campaign_performance, trends, budget_optimization),
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def generate_executive_summary(self, performance: Dict, trends: Dict) -> str:
        """Generate an executive summary of marketing performance"""
        score = performance.get("analysis", {}).get("score", 0)
        overall_performance = performance.get("analysis", {}).get("overall_performance", "unknown")
        
        summary = f"Marketing Performance Summary: {overall_performance.upper()} (Score: {score}/100)\n\n"
        
        # Add key metrics
        metrics = performance.get("metrics", {})
        summary += f"Key Metrics:\n- ROAS: {metrics.get('roas', 0):.2f}\n- CPA: R{metrics.get('cpa', 0):.2f}\n- CTR: {metrics.get('ctr', 0)*100:.2f}%\n- Conversion Rate: {metrics.get('conversion_rate', 0)*100:.2f}%\n\n"
        
        # Add trend information
        for metric, trend in trends.get("trends", {}).items():
            summary += f"{metric.upper()} is {trend.get('trend', 'stable')} ({trend.get('strength', 0):.1f} strength)\n"
        
        return summary
    
    def extract_key_takeaways(self, performance: Dict, trends: Dict, budget: Dict) -> List[str]:
        """Extract the most important takeaways from the report"""
        takeaways = []
        
        # Performance takeaways
        score = performance.get("analysis", {}).get("score", 0)
        if score >= 80:
            takeaways.append("Excellent overall performance - consider scaling successful strategies")
        elif score <= 60:
            takeaways.append("Performance needs improvement - focus on high-impact optimizations")
        
        # Trend takeaways
        for metric, trend in trends.get("trends", {}).items():
            if trend.get("strength", 0) > 0.8:
                direction = trend.get("trend", "")
                takeaways.append(f"Strong {direction} trend in {metric.upper()} - investigate causes and opportunities")
        
        # Budget takeaways
        improvement = budget.get("expected_improvement", 0)
        if improvement > 10:
            takeaways.append(f"Significant ROI improvement ({improvement:.1f}%) possible through budget reallocation")
        
        return takeaways
