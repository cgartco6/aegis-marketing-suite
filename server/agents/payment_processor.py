import stripe
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
import json
from .base_agent import AIAgent

class PaymentProcessorAgent(AIAgent):
    """AI agent for processing payments and managing financial transactions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("payment_processor", config)
    
    async def initialize(self):
        """Initialize the payment processor agent"""
        self.capabilities = [
            "process_payments",
            "generate_invoices",
            "manage_subscriptions",
            "handle_refunds",
            "currency_conversion",
            "distribute_funds",
            "generate_financial_reports"
        ]
        
        # Initialize payment APIs
        stripe.api_key = self.config.get("stripe_secret_key")
        
        # Bank account details
        self.accounts = {
            "owner": self.config.get("owner_account"),
            "ai_fund": self.config.get("ai_fund_account"),
            "reserve": self.config.get("reserve_account")
        }
        
        # Payment methods configuration
        self.payment_methods = self.config.get("payment_methods", ["card", "bank_transfer"])
        
        # Load transaction history
        self.load_transaction_history()
        
        print(f"Payment Processor Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
        return {"status": "initialized", "capabilities": self.capabilities}
    
    def load_transaction_history(self):
        """Load transaction history from storage"""
        try:
            with open("data/transactions.json", "r") as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            self.transactions = []
    
    def save_transaction_history(self):
        """Save transaction history to storage"""
        with open("data/transactions.json", "w") as f:
            json.dump(self.transactions, f, indent=2)
    
    async def _process_task(self, task: Dict) -> Dict:
        """Process payment tasks"""
        task_type = task.get("type", "")
        payload = task.get("payload", {})
        
        if task_type == "payment_process":
            return await self.process_payment(payload)
        elif task_type == "payment_invoice":
            return await self.generate_invoice(payload)
        elif task_type == "payment_subscription":
            return await self.manage_subscription(payload)
        elif task_type == "payment_refund":
            return await self.process_refund(payload)
        elif task_type == "payment_distribute":
            return await self.distribute_funds(payload)
        elif task_type == "payment_convert":
            return await self.convert_currency(payload)
        elif task_type == "payment_report":
            return await self.generate_financial_report(payload)
        else:
            raise ValueError(f"Unsupported payment task type: {task_type}")
    
    async def process_payment(self, payload: Dict) -> Dict:
        """Process a payment through Stripe"""
        amount = payload.get("amount", 0)
        currency = payload.get("currency", "zar").lower()
        description = payload.get("description", "")
        customer_email = payload.get("customer_email", "")
        payment_method = payload.get("payment_method", "card")
        
        # Validate payment method
        if payment_method not in self.payment_methods:
            raise ValueError(f"Unsupported payment method: {payment_method}. Supported methods: {self.payment_methods}")
        
        # Convert amount to cents (Stripe requires integer amounts)
        amount_in_cents = int(amount * 100)
        
        try:
            # Create a PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=currency,
                description=description,
                receipt_email=customer_email,
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never"
                },
                metadata={
                    "processed_by": self.agent_id,
                    "customer_email": customer_email
                }
            )
            
            # Record transaction
            transaction = {
                "transaction_id": intent.id,
                "amount": amount,
                "currency": currency,
                "description": description,
                "customer_email": customer_email,
                "status": "requires_payment_method",
                "created_at": datetime.now().isoformat(),
                "payment_method": payment_method
            }
            
            self.transactions.append(transaction)
            self.save_transaction_history()
            
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": intent.status,
                "next_action": "confirm_payment" if intent.status == "requires_payment_method" else "wait"
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Payment processing failed: {str(e)}")
    
    async def confirm_payment(self, payload: Dict) -> Dict:
        """Confirm a payment intent"""
        payment_intent_id = payload.get("payment_intent_id")
        payment_method_id = payload.get("payment_method_id")
        
        try:
            # Confirm the PaymentIntent
            intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id
            )
            
            # Update transaction status
            for transaction in self.transactions:
                if transaction["transaction_id"] == payment_intent_id:
                    transaction["status"] = intent.status
                    transaction["confirmed_at"] = datetime.now().isoformat()
                    break
            
            self.save_transaction_history()
            
            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount_received": intent.amount_received / 100 if intent.amount_received else 0
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Payment confirmation failed: {str(e)}")
    
    async def generate_invoice(self, payload: Dict) -> Dict:
        """Generate an invoice for a customer"""
        customer_id = payload.get("customer_id")
        customer_email = payload.get("customer_email")
        items = payload.get("items", [])
        due_date = payload.get("due_date")
        currency = payload.get("currency", "zar")
        
        # Calculate total amount
        total_amount = sum(item.get("amount", 0) * item.get("quantity", 1) for item in items)
        
        # Create invoice data
        invoice_id = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        invoice = {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "customer_email": customer_email,
            "items": items,
            "total_amount": total_amount,
            "currency": currency,
            "due_date": due_date or (datetime.now() + timedelta(days=30)).isoformat()[:10],
            "status": "unpaid",
            "created_at": datetime.now().isoformat(),
            "payment_link": f"https://pay.example.com/invoice/{invoice_id}"  # Would be a real link
        }
        
        # Save invoice
        self.save_invoice(invoice)
        
        return {
            "invoice_id": invoice_id,
            "amount": total_amount,
            "currency": currency,
            "due_date": invoice["due_date"],
            "payment_link": invoice["payment_link"],
            "status": "generated"
        }
    
    def save_invoice(self, invoice: Dict):
        """Save invoice to storage"""
        try:
            with open("data/invoices.json", "r") as f:
                invoices = json.load(f)
        except FileNotFoundError:
            invoices = []
        
        invoices.append(invoice)
        
        with open("data/invoices.json", "w") as f:
            json.dump(invoices, f, indent=2)
    
    async def manage_subscription(self, payload: Dict) -> Dict:
        """Manage customer subscriptions"""
        action = payload.get("action", "create")
        customer_id = payload.get("customer_id")
        plan_id = payload.get("plan_id")
        interval = payload.get("interval", "month")
        amount = payload.get("amount", 0)
        
        if action == "create":
            # Create a new subscription
            subscription_id = f"SUB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            subscription = {
                "subscription_id": subscription_id,
                "customer_id": customer_id,
                "plan_id": plan_id,
                "interval": interval,
                "amount": amount,
                "currency": "zar",
                "status": "active",
                "start_date": datetime.now().isoformat(),
                "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat()[:10]
            }
            
            # Save subscription
            self.save_subscription(subscription)
            
            return {
                "subscription_id": subscription_id,
                "status": "active",
                "next_billing_date": subscription["next_billing_date"]
            }
        
        elif action == "cancel":
            # Cancel a subscription
            subscription_id = payload.get("subscription_id")
            
            # Find and update subscription
            try:
                with open("data/subscriptions.json", "r") as f:
                    subscriptions = json.load(f)
            except FileNotFoundError:
                raise Exception("No subscriptions found")
            
            for sub in subscriptions:
                if sub["subscription_id"] == subscription_id:
                    sub["status"] = "cancelled"
                    sub["cancelled_at"] = datetime.now().isoformat()
                    break
            
            with open("data/subscriptions.json", "w") as f:
                json.dump(subscriptions, f, indent=2)
            
            return {
                "subscription_id": subscription_id,
                "status": "cancelled"
            }
        
        else:
            raise ValueError(f"Unsupported subscription action: {action}")
    
    def save_subscription(self, subscription: Dict):
        """Save subscription to storage"""
        try:
            with open("data/subscriptions.json", "r") as f:
                subscriptions = json.load(f)
        except FileNotFoundError:
            subscriptions = []
        
        subscriptions.append(subscription)
        
        with open("data/subscriptions.json", "w") as f:
            json.dump(subscriptions, f, indent=2)
    
    async def process_refund(self, payload: Dict) -> Dict:
        """Process a refund for a payment"""
        payment_intent_id = payload.get("payment_intent_id")
        amount = payload.get("amount")
        reason = payload.get("reason", "requested_by_customer")
        
        try:
            # Create refund
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(amount * 100) if amount else None,
                reason=reason
            )
            
            # Update transaction status
            for transaction in self.transactions:
                if transaction["transaction_id"] == payment_intent_id:
                    transaction["refunded_amount"] = refund.amount / 100
                    transaction["refunded_at"] = datetime.now().isoformat()
                    transaction["refund_reason"] = reason
                    break
            
            self.save_transaction_history()
            
            return {
                "refund_id": refund.id,
                "amount": refund.amount / 100,
                "currency": refund.currency,
                "status": refund.status,
                "reason": reason
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Refund processing failed: {str(e)}")
    
    async def distribute_funds(self, payload: Dict = None) -> Dict:
        """Distribute funds according to the specified percentages"""
        try:
            # Get total revenue for the period (default: last week)
            period_days = payload.get("period_days", 7) if payload else 7
            since_date = datetime.now() - timedelta(days=period_days)
            
            revenue = self.get_revenue_since(since_date)
            
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
                    results[account_type] = await self.transfer_to_account(
                        self.accounts[account_type],
                        amount,
                        f"Weekly distribution - {account_type} share"
                    )
            
            # Record distribution
            distribution_record = {
                "distribution_id": f"DIST{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "period_days": period_days,
                "total_revenue": revenue,
                "distribution": distribution,
                "executed_at": datetime.now().isoformat(),
                "results": results
            }
            
            self.save_distribution_record(distribution_record)
            
            return {
                "success": True,
                "total_revenue": revenue,
                "distribution": distribution,
                "transfer_results": results,
                "distribution_id": distribution_record["distribution_id"]
            }
            
        except Exception as e:
            raise Exception(f"Fund distribution failed: {str(e)}")
    
    def get_revenue_since(self, since_date: datetime) -> float:
        """Calculate revenue since a specific date"""
        # This would query your database for successful transactions
        # For now, use the transaction history
        
        revenue = 0.0
        for transaction in self.transactions:
            if (transaction["status"] == "succeeded" and 
                datetime.fromisoformat(transaction.get("confirmed_at", transaction["created_at"])) >= since_date):
                revenue += transaction["amount"]
        
        return revenue
    
    async def transfer_to_account(self, account_details: str, amount: float, description: str) -> Dict:
        """Transfer funds to a specific bank account"""
        # This would use FNB's API or another banking API
        # For now, simulate the transfer
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Generate a fake reference number
        reference = f"TF{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "completed",
            "amount": amount,
            "account": account_details[-4:],  # Last 4 digits for display
            "reference": reference,
            "description": description,
            "completed_at": datetime.now().isoformat()
        }
    
    def save_distribution_record(self, distribution: Dict):
        """Save distribution record to storage"""
        try:
            with open("data/fund_distributions.json", "r") as f:
                distributions = json.load(f)
        except FileNotFoundError:
            distributions = []
        
        distributions.append(distribution)
        
        with open("data/fund_distributions.json", "w") as f:
            json.dump(distributions, f, indent=2)
    
    async def convert_currency(self, payload: Dict) -> Dict:
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
                raise Exception("Currency conversion API returned an error")
                
        except Exception as e:
            raise Exception(f"Currency conversion error: {str(e)}")
    
    async def generate_financial_report(self, payload: Dict) -> Dict:
        """Generate a financial report"""
        report_type = payload.get("report_type", "revenue")
        period = payload.get("period", "month")
        
        # Calculate start date based on period
        now = datetime.now()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)  # Default to month
        
        if report_type == "revenue":
            return await self.generate_revenue_report(start_date, now)
        elif report_type == "expenses":
            return await self.generate_expenses_report(start_date, now)
        elif report_type == "profit":
            return await self.generate_profit_report(start_date, now)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
    
    async def generate_revenue_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate a revenue report for the specified period"""
        revenue = 0.0
        transactions_in_period = []
        
        for transaction in self.transactions:
            transaction_date = datetime.fromisoformat(transaction.get("confirmed_at", transaction["created_at"]))
            if start_date <= transaction_date <= end_date and transaction["status"] == "succeeded":
                revenue += transaction["amount"]
                transactions_in_period.append(transaction)
        
        # Group by currency
        revenue_by_currency = {}
        for transaction in transactions_in_period:
            currency = transaction["currency"]
            revenue_by_currency[currency] = revenue_by_currency.get(currency, 0) + transaction["amount"]
        
        return {
            "report_type": "revenue",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_revenue": revenue,
            "revenue_by_currency": revenue_by_currency,
            "transaction_count": len(transactions_in_period)
        }
    
    async def generate_expenses_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate an expenses report for the specified period"""
        # This would include actual expenses data
        # For now, return a mock report
        
        expenses = {
            "hosting": 299.00,
            "api_costs": 150.00,
            "marketing": 500.00,
            "software": 199.00
        }
        
        total_expenses = sum(expenses.values())
        
        return {
            "report_type": "expenses",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_expenses": total_expenses,
            "expenses_by_category": expenses,
            "category_count": len(expenses)
        }
    
    async def generate_profit_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate a profit report for the specified period"""
        revenue_report = await self.generate_revenue_report(start_date, end_date)
        expenses_report = await self.generate_expenses_report(start_date, end_date)
        
        revenue = revenue_report["total_revenue"]
        expenses = expenses_report["total_expenses"]
        profit = revenue - expenses
        
        return {
            "report_type": "profit",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "revenue": revenue,
            "expenses": expenses,
            "profit": profit,
            "profit_margin": (profit / revenue) * 100 if revenue > 0 else 0
        }
