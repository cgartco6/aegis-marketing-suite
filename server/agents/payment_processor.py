# agents/payment_processor.py
import stripe
from datetime import datetime, timedelta
import requests
from base_agent import AIAgent

class PaymentProcessorAgent(AIAgent):
    async def initialize(self):
        self.capabilities = [
            "process_payments",
            "generate_invoices",
            "manage_subscriptions",
            "handle_refunds",
            "currency_conversion",
            "distribute_funds"
        ]
        
        # Initialize payment APIs
        stripe.api_key = self.config.get("stripe_secret_key")
        
        # Bank account details
        self.accounts = {
            "owner": self.config.get("owner_account"),
            "ai_fund": self.config.get("ai_fund_account"),
            "reserve": self.config.get("reserve_account")
        }
        
        print(f"Payment Processor Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
    
    async def process_task(self, task: Dict):
        task_type = task["type"]
        payload = task["payload"]
        
        if task_type == "payment_process":
            return await self.process_payment(payload)
        elif task_type == "payment_invoice":
            return await self.generate_invoice(payload)
        elif task_type == "payment_distribute":
            return await self.distribute_funds(payload)
        elif task_type == "payment_convert":
            return await self.convert_currency(payload)
        else:
            return {"error": f"Unsupported payment task type: {task_type}"}
    
    async def process_payment(self, payload: Dict):
        """Process a payment through Stripe"""
        amount = payload.get("amount", 0)
        currency = payload.get("currency", "zar")
        description = payload.get("description", "")
        customer_email = payload.get("customer_email", "")
        
        try:
            # Create a PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                description=description,
                receipt_email=customer_email,
                automatic_payment_methods={"enabled": True}
            )
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency
            }
        except stripe.error.StripeError as e:
            return {"error": f"Payment processing failed: {str(e)}"}
    
    async def distribute_funds(self, payload: Dict = None):
        """Distribute funds according to the specified percentages"""
        try:
            # Get total revenue for the week
            week_ago = datetime.now() - timedelta(days=7)
            revenue = self.get_revenue_since(week_ago)
            
            # Calculate distribution amounts
            distribution = {
                "owner": revenue * 0.6,
                "ai_fund": revenue * 0.2,
                "reserve": revenue * 0.2
            }
            
            # Execute transfers (simplified - would use actual banking APIs)
            results = {}
            for account_type, amount in distribution.items():
                if amount > 0:
                    results[account_type] = self.transfer_to_account(
                        self.accounts[account_type],
                        amount
                    )
            
            return {
                "success": True,
                "total_revenue": revenue,
                "distribution": distribution,
                "transfer_results": results
            }
            
        except Exception as e:
            return {"error": f"Fund distribution failed: {str(e)}"}
    
    def get_revenue_since(self, since_date):
        """Calculate revenue since a specific date"""
        # This would query your database for payments
        # For now, return a placeholder value
        return 10000.00  # Placeholder
    
    def transfer_to_account(self, account_details, amount):
        """Transfer funds to a specific bank account"""
        # This would use FNB's API or another banking API
        # Placeholder implementation
        return {"status": "success", "amount": amount, "account": account_details[-4:]}
    
    async def convert_currency(self, payload: Dict):
        """Convert between currencies using real exchange rates"""
        amount = payload.get("amount", 0)
        from_currency = payload.get("from_currency", "zar").upper()
        to_currency = payload.get("to_currency", "usd").upper()
        
        try:
            # Use a currency conversion API
            response = requests.get(
                f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
            )
            data = response.json()
            
            if data.get("success", False):
                return {
                    "success": True,
                    "original_amount": amount,
                    "original_currency": from_currency,
                    "converted_amount": data["result"],
                    "converted_currency": to_currency,
                    "exchange_rate": data["info"]["rate"],
                    "date": data["date"]
                }
            else:
                return {"error": "Currency conversion failed"}
                
        except Exception as e:
            return {"error": f"Currency conversion error: {str(e)}"}
