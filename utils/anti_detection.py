"""
Anti-detection utilities for avoiding bot detection
"""

import random
import time
import logging
import os
from typing import Dict, List
from datetime import datetime

def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('civic_scraper')
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create handlers
    file_handler = logging.FileHandler(f'logs/scraper_{datetime.now().strftime("%Y%m%d")}.log')
    console_handler = logging.StreamHandler()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class AntiDetectionManager:
    """Manages anti-detection measures"""
    
    def __init__(self, config):
        self.config = config
        self.session_start = time.time()
        self.request_count = 0
        self.last_request_time = 0
        
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.config.USER_AGENTS)
    
    def get_browser_headers(self) -> Dict[str, str]:
        """Get realistic browser headers"""
        return {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def get_random_delay(self, min_delay: float = None, max_delay: float = None) -> float:
        """Get random delay between requests"""
        min_d = min_delay or self.config.MIN_DELAY
        max_d = max_delay or self.config.MAX_DELAY
        
        # Add some randomness to avoid patterns
        base_delay = random.uniform(min_d, max_d)
        
        # Occasional longer delays (10% chance)
        if random.random() < 0.1:
            base_delay *= random.uniform(1.5, 2.5)
        
        return base_delay
    
    def should_rotate_session(self) -> bool:
        """Determine if session should be rotated"""
        # Rotate after every 15-20 requests
        return self.request_count > 0 and self.request_count % random.randint(15, 20) == 0
    
    def increment_request_count(self):
        """Increment request counter"""
        self.request_count += 1
        self.last_request_time = time.time()
    
    def get_session_stats(self) -> Dict[str, float]:
        """Get session statistics"""
        elapsed = time.time() - self.session_start
        return {
            'elapsed_time': elapsed,
            'request_count': self.request_count,
            'requests_per_minute': (self.request_count / elapsed) * 60 if elapsed > 0 else 0
        }
