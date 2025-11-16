"""
Security-Focused Rate Limiting
DDoS protection, brute force protection, API abuse prevention
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SecurityRateLimiter:
    """
    Security-focused rate limiter for DDoS and brute force protection
    """
    
    def __init__(self):
        """Initialize security rate limiter"""
        self.ip_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.account_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
        self.blocked_accounts: Dict[str, datetime] = {}
        
        # Rate limit configurations
        self.max_attempts_per_minute = 10
        self.max_attempts_per_hour = 50
        self.block_duration_minutes = 15
        logger.info("SecurityRateLimiter initialized")
    
    def check_rate_limit(
        self,
        identifier: str,
        identifier_type: str = "ip",
        max_attempts: Optional[int] = None,
        window_minutes: int = 1
    ) -> Dict[str, Any]:
        """
        Check if rate limit is exceeded
        
        Args:
            identifier: IP address or account identifier
            identifier_type: "ip" or "account"
            max_attempts: Maximum attempts allowed (uses default if None)
            window_minutes: Time window in minutes
        
        Returns:
            Rate limit check result
        """
        # Check if blocked
        if identifier_type == "ip":
            if identifier in self.blocked_ips:
                block_until = self.blocked_ips[identifier]
                if datetime.utcnow() < block_until:
                    remaining = (block_until - datetime.utcnow()).total_seconds()
                    return {
                        "allowed": False,
                        "blocked": True,
                        "reason": "IP blocked due to excessive attempts",
                        "retry_after_seconds": int(remaining)
                    }
                else:
                    # Block expired, remove
                    del self.blocked_ips[identifier]
        
        elif identifier_type == "account":
            if identifier in self.blocked_accounts:
                block_until = self.blocked_accounts[identifier]
                if datetime.utcnow() < block_until:
                    remaining = (block_until - datetime.utcnow()).total_seconds()
                    return {
                        "allowed": False,
                        "blocked": True,
                        "reason": "Account blocked due to excessive attempts",
                        "retry_after_seconds": int(remaining)
                    }
                else:
                    del self.blocked_accounts[identifier]
        
        # Get attempts list
        if identifier_type == "ip":
            attempts = self.ip_attempts[identifier]
        else:
            attempts = self.account_attempts[identifier]
        
        # Clean old attempts
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        attempts[:] = [attempt for attempt in attempts if attempt > cutoff]
        
        # Check limit
        if max_attempts is None:
            max_attempts = self.max_attempts_per_minute if window_minutes == 1 else self.max_attempts_per_hour
        
        if len(attempts) >= max_attempts:
            # Block the identifier
            block_until = datetime.utcnow() + timedelta(minutes=self.block_duration_minutes)
            if identifier_type == "ip":
                self.blocked_ips[identifier] = block_until
            else:
                self.blocked_accounts[identifier] = block_until
            
            logger.warning(f"Rate limit exceeded for {identifier_type}: {identifier}. Blocked until {block_until}")
            
            return {
                "allowed": False,
                "blocked": True,
                "reason": f"Rate limit exceeded: {len(attempts)} attempts in {window_minutes} minute(s)",
                "retry_after_seconds": self.block_duration_minutes * 60,
                "attempts": len(attempts)
            }
        
        # Record attempt
        attempts.append(datetime.utcnow())
        
        return {
            "allowed": True,
            "blocked": False,
            "remaining_attempts": max_attempts - len(attempts),
            "attempts": len(attempts)
        }
    
    def record_failed_attempt(self, identifier: str, identifier_type: str = "ip"):
        """
        Record a failed authentication attempt
        
        Args:
            identifier: IP address or account identifier
            identifier_type: "ip" or "account"
        """
        if identifier_type == "ip":
            self.ip_attempts[identifier].append(datetime.utcnow())
        else:
            self.account_attempts[identifier].append(datetime.utcnow())
    
    def reset_attempts(self, identifier: str, identifier_type: str = "ip"):
        """
        Reset attempts for an identifier (e.g., after successful authentication)
        
        Args:
            identifier: IP address or account identifier
            identifier_type: "ip" or "account"
        """
        if identifier_type == "ip":
            if identifier in self.ip_attempts:
                del self.ip_attempts[identifier]
            if identifier in self.blocked_ips:
                del self.blocked_ips[identifier]
        else:
            if identifier in self.account_attempts:
                del self.account_attempts[identifier]
            if identifier in self.blocked_accounts:
                del self.blocked_accounts[identifier]
    
    def cleanup_old_blocks(self):
        """Clean up expired blocks"""
        now = datetime.utcnow()
        
        expired_ips = [
            ip for ip, block_until in self.blocked_ips.items()
            if now >= block_until
        ]
        for ip in expired_ips:
            del self.blocked_ips[ip]
        
        expired_accounts = [
            account for account, block_until in self.blocked_accounts.items()
            if now >= block_until
        ]
        for account in expired_accounts:
            del self.blocked_accounts[account]
        
        if expired_ips or expired_accounts:
            logger.info(f"Cleaned up {len(expired_ips)} IP blocks and {len(expired_accounts)} account blocks")


# Global instance
security_rate_limiter = SecurityRateLimiter()

