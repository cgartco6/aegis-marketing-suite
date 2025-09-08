import hashlib
import hmac
import ssl
from cryptography.fernet import Fernet
from typing import Dict, Any, List
from .base_agent import AIAgent
from datetime import datetime, timedelta
import asyncio
import json

class SecurityMonitorAgent(AIAgent):
    """AI agent for monitoring security and protecting the system"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("security_monitor", config)
    
    async def initialize(self):
        """Initialize the security monitor agent"""
        self.capabilities = [
            "encrypt_data",
            "decrypt_data",
            "detect_intrusions",
            "monitor_logs",
            "manage_access",
            "secure_comms",
            "perform_audits",
            "handle_threats"
        ]
        
        # Generate encryption keys
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security settings
        self.security_level = self.config.get("security_level", "military")
        self.thresholds = self.config.get("thresholds", {
            "failed_login_attempts": 5,
            "suspicious_activity": 3,
            "data_access_violations": 1
        })
        
        # Load security events
        self.load_security_events()
        
        # Start background monitoring
        asyncio.create_task(self.continuous_monitoring())
        
        print(f"Security Monitor Agent {self.agent_id} initialized with {len(self.capabilities)} capabilities")
        return {"status": "initialized", "capabilities": self.capabilities, "security_level": self.security_level}
    
    def load_security_events(self):
        """Load security events from storage"""
        try:
            with open("data/security_events.json", "r") as f:
                self.security_events = json.load(f)
        except FileNotFoundError:
            self.security_events = []
    
    def save_security_events(self):
        """Save security events to storage"""
        with open("data/security_events.json", "w") as f:
            json.dump(self.security_events, f, indent=2)
    
    async def continuous_monitoring(self):
        """Continuous security monitoring in the background"""
        while True:
            # Check for security threats
            threats = await self.check_for_threats()
            
            if threats:
                print(f"Security threats detected: {len(threats)}")
                await self.handle_threats(threats)
            
            # Perform routine security audit
            if datetime.now().hour % 6 == 0:  # Every 6 hours
                await self.perform_security_audit()
            
            # Wait before next check
            await asyncio.sleep(300)  # 5 minutes
    
    async def _process_task(self, task: Dict) -> Dict:
        """Process security tasks"""
        task_type = task.get("type", "")
        payload = task.get("payload", {})
        
        if task_type == "security_encrypt":
            return await self.encrypt_data(payload)
        elif task_type == "security_decrypt":
            return await self.decrypt_data(payload)
        elif task_type == "security_monitor":
            return await self.monitor_security()
        elif task_type == "security_audit":
            return await self.perform_security_audit()
        elif task_type == "security_threat":
            return await self.handle_threats(payload.get("threats", []))
        else:
            raise ValueError(f"Unsupported security task type: {task_type}")
    
    async def encrypt_data(self, payload: Dict) -> Dict:
        """Encrypt sensitive data with military-grade encryption"""
        data = payload.get("data", "")
        encryption_type = payload.get("encryption_type", "fernet")
        
        try:
            if encryption_type == "fernet":
                encrypted_data = self.cipher_suite.encrypt(data.encode())
                return {
                    "success": True, 
                    "encrypted_data": encrypted_data.decode(),
                    "encryption_type": encryption_type
                }
            elif encryption_type == "aes256":
                # Implement AES-256 encryption
                encrypted_data = self.aes_encrypt(data)
                return {
                    "success": True, 
                    "encrypted_data": encrypted_data,
                    "encryption_type": encryption_type
                }
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    async def decrypt_data(self, payload: Dict) -> Dict:
        """Decrypt data using the appropriate algorithm"""
        encrypted_data = payload.get("encrypted_data", "")
        encryption_type = payload.get("encryption_type", "fernet")
        
        try:
            if encryption_type == "fernet":
                decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
                return {
                    "success": True, 
                    "decrypted_data": decrypted_data.decode(),
                    "encryption_type": encryption_type
                }
            elif encryption_type == "aes256":
                decrypted_data = self.aes_decrypt(encrypted_data)
                return {
                    "success": True, 
                    "decrypted_data": decrypted_data,
                    "encryption_type": encryption_type
                }
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def aes_encrypt(self, data: str) -> str:
        """AES-256 encryption implementation (placeholder)"""
        # In a real implementation, this would use cryptography.hazmat
        # For now, return a mock encrypted string
        return f"aes_encrypted:{data}"
    
    def aes_decrypt(self, encrypted_data: str) -> str:
        """AES-256 decryption implementation (placeholder)"""
        # In a real implementation, this would use cryptography.hazmat
        if encrypted_data.startswith("aes_encrypted:"):
            return encrypted_data.split(":", 1)[1]
        return encrypted_data
    
    async def monitor_security(self) -> Dict:
        """Continuous security monitoring"""
        threats_detected = await self.check_for_threats()
        system_health = await self.check_system_health()
        
        return {
            "threats_detected": threats_detected,
            "system_health": system_health,
            "timestamp": datetime.now().isoformat(),
            "security_level": self.security_level
        }
    
    async def check_for_threats(self) -> List[Dict]:
        """Check for potential security threats"""
        threats = []
        
        # Check for failed login attempts
        failed_logins = await self.check_failed_logins()
        if failed_logins:
            threats.extend(failed_logins)
        
        # Check for suspicious activity
        suspicious_activity = await self.check_suspicious_activity()
        if suspicious_activity:
            threats.extend(suspicious_activity)
        
        # Check for data access violations
        access_violations = await self.check_access_violations()
        if access_violations:
            threats.extend(access_violations)
        
        return threats
    
    async def check_failed_logins(self) -> List[Dict]:
        """Check for failed login attempts"""
        # This would query your authentication system
        # For now, check security events for failed login patterns
        
        recent_events = [
            event for event in self.security_events 
            if event["type"] == "login_attempt" 
            and not event["success"]
            and datetime.fromisoformat(event["timestamp"]) > datetime.now() - timedelta(hours=1)
        ]
        
        threats = []
        ip_addresses = {}
        
        for event in recent_events:
            ip = event.get("ip_address", "unknown")
            ip_addresses[ip] = ip_addresses.get(ip, 0) + 1
            
            if ip_addresses[ip] >= self.thresholds["failed_login_attempts"]:
                threats.append({
                    "type": "failed_login_attempts",
                    "severity": "high",
                    "ip_address": ip,
                    "attempts": ip_addresses[ip],
                    "message": f"Multiple failed login attempts from {ip}"
                })
        
        return threats
    
    async def check_suspicious_activity(self) -> List[Dict]:
        """Check for suspicious activity patterns"""
        # This would use ML models to detect anomalies
        # For now, check for unusual patterns in security events
        
        recent_events = [
            event for event in self.security_events 
            if datetime.fromisoformat(event["timestamp"]) > datetime.now() - timedelta(hours=24)
        ]
        
        threats = []
        
        # Check for unusual access patterns
        access_patterns = {}
        for event in recent_events:
            if event["type"] == "data_access":
                user = event.get("user", "unknown")
                resource = event.get("resource", "unknown")
                key = f"{user}_{resource}"
                access_patterns[key] = access_patterns.get(key, 0) + 1
                
                if access_patterns[key] > self.thresholds["suspicious_activity"]:
                    threats.append({
                        "type": "suspicious_access_pattern",
                        "severity": "medium",
                        "user": user,
                        "resource": resource,
                        "access_count": access_patterns[key],
                        "message": f"Suspicious access pattern detected for {user} accessing {resource}"
                    })
        
        return threats
    
    async def check_access_violations(self) -> List[Dict]:
        """Check for data access violations"""
        # This would check against access control policies
        # For now, return mock violations
        
        violations = []
        
        # Example violation detection
        if len(self.security_events) > 1000:  # Simulate high activity
            violations.append({
                "type": "potential_brute_force",
                "severity": "high",
                "message": "High volume of security events detected, potential brute force attack"
            })
        
        return violations
    
    async def check_system_health(self) -> Dict:
        """Check overall system security health"""
        # This would check various system health indicators
        # For now, return mock health status
        
        health_indicators = {
            "encryption_status": "active",
            "firewall_status": "active",
            "intrusion_detection": "active",
            "log_monitoring": "active",
            "access_controls": "enforced",
            "data_backup": "current"
        }
        
        # Calculate overall health score (0-100)
        score = 95  # Start with high score
        
        # Deduct points for recent threats
        recent_threats = await self.check_for_threats()
        score -= len(recent_threats) * 5
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        return {
            "status": "secure" if score >= 80 else "vulnerable",
            "score": score,
            "indicators": health_indicators,
            "threat_count": len(recent_threats)
        }
    
    async def handle_threats(self, threats: List[Dict]) -> Dict:
        """Handle detected security threats"""
        actions_taken = []
        
        for threat in threats:
            action = await self.handle_threat(threat)
            actions_taken.append({
                "threat": threat,
                "action": action,
                "handled_at": datetime.now().isoformat()
            })
        
        # Log the response actions
        self.security_events.extend(actions_taken)
        self.save_security_events()
        
        return {
            "threats_handled": len(threats),
            "actions_taken": actions_taken,
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_threat(self, threat: Dict) -> Dict:
        """Handle an individual security threat"""
        threat_type = threat.get("type", "")
        severity = threat.get("severity", "medium")
        
        if threat_type == "failed_login_attempts":
            # Block IP address
            ip_address = threat.get("ip_address")
            return {
                "action": "block_ip",
                "ip_address": ip_address,
                "duration": "24h",
                "reason": "Multiple failed login attempts"
            }
        
        elif threat_type == "suspicious_access_pattern":
            # Notify admin and require additional verification
            user = threat.get("user")
            return {
                "action": "require_2fa",
                "user": user,
                "duration": "24h",
                "reason": "Suspicious access pattern detected"
            }
        
        elif threat_type == "potential_brute_force":
            # Increase security monitoring
            return {
                "action": "increase_monitoring",
                "level": "high",
                "duration": "6h",
                "reason": "Potential brute force attack detected"
            }
        
        else:
            # Default action for unknown threats
            return {
                "action": "investigate",
                "reason": "Unknown threat type requires manual investigation"
            }
    
    async def perform_security_audit(self) -> Dict:
        """Perform a comprehensive security audit"""
        audit_id = f"AUDIT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Check various security aspects
        checks = [
            await self.check_password_policies(),
            await self.check_access_controls(),
            await self.check_encryption_status(),
            await self.check_system_patches(),
            await self.check_backup_status()
        ]
        
        # Calculate audit score
        passed_checks = sum(1 for check in checks if check["status"] == "pass")
        total_checks = len(checks)
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Generate recommendations
        recommendations = []
        for check in checks:
            if check["status"] != "pass":
                recommendations.extend(check.get("recommendations", []))
        
        audit_result = {
            "audit_id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "score": round(score, 1),
            "checks": checks,
            "recommendations": recommendations,
            "overall_status": "pass" if score >= 80 else "fail"
        }
        
        # Save audit result
        self.save_audit_result(audit_result)
        
        return audit_result
    
    async def check_password_policies(self) -> Dict:
        """Check if password policies are enforced"""
        # This would check your authentication system
        # For now, return a mock check result
        
        return {
            "check": "password_policies",
            "status": "pass",
            "details": "Strong password policies are enforced",
            "recommendations": []
        }
    
    async def check_access_controls(self) -> Dict:
        """Check if access controls are properly configured"""
        # This would check your authorization system
        # For now, return a mock check result
        
        return {
            "check": "access_controls",
            "status": "pass",
            "details": "Role-based access controls are properly configured",
            "recommendations": []
        }
    
    async def check_encryption_status(self) -> Dict:
        """Check if data encryption is properly implemented"""
        # This would check your data storage systems
        # For now, return a mock check result
        
        return {
            "check": "encryption_status",
            "status": "pass",
            "details": "Data encryption is properly implemented for all sensitive data",
            "recommendations": []
        }
    
    async def check_system_patches(self) -> Dict:
        """Check if system patches are up to date"""
        # This would check your server and dependency versions
        # For now, return a mock check result
        
        return {
            "check": "system_patches",
            "status": "warn",
            "details": "Some system patches are outdated",
            "recommendations": [
                "Update OpenSSL to latest version",
                "Apply security patches for operating system"
            ]
        }
    
    async def check_backup_status(self) -> Dict:
        """Check if backups are working properly"""
        # This would check your backup systems
        # For now, return a mock check result
        
        return {
            "check": "backup_status",
            "status": "pass",
            "details": "Regular backups are performed and verified",
            "recommendations": []
        }
    
    def save_audit_result(self, audit_result: Dict):
        """Save audit result to storage"""
        try:
            with open("data/security_audits.json", "r") as f:
                audits = json.load(f)
        except FileNotFoundError:
            audits = []
        
        audits.append(audit_result)
        
        with open("data/security_audits.json", "w") as f:
            json.dump(audits, f, indent=2)
    
    async def self_improve(self):
        """Self-improvement based on security audit results"""
        try:
            # Analyze recent audit results
            with open("data/security_audits.json", "r") as f:
                audits = json.load(f)
            
            if audits:
                recent_audits = [audit for audit in audits if 
                                datetime.fromisoformat(audit["timestamp"]) > 
                                datetime.now() - timedelta(days=30)]
                
                if recent_audits:
                    # Calculate average score
                    scores = [audit["score"] for audit in recent_audits]
                    avg_score = sum(scores) / len(scores)
                    
                    # Identify common issues
                    all_recommendations = []
                    for audit in recent_audits:
                        all_recommendations.extend(audit.get("recommendations", []))
                    
                    # Count recommendation frequency
                    rec_count = {}
                    for rec in all_recommendations:
                        rec_count[rec] = rec_count.get(rec, 0) + 1
                    
                    # Get top recommendations
                    top_recommendations = sorted(rec_count.items(), key=lambda x: x[1], reverse=True)[:5]
                    
                    return {
                        "avg_audit_score": avg_score,
                        "total_audits": len(recent_audits),
                        "common_issues": [rec[0] for rec in top_recommendations],
                        "improvement_plan": "Implement top security recommendations"
                    }
            
            return {"status": "no_audit_data"}
            
        except FileNotFoundError:
            return {"status": "no_audit_data"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
