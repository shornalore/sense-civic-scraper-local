"""
Enhanced configuration settings for the civic sense scraper
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Enhanced configuration class for scraper settings"""
    
    # Email settings with debugging
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') 
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
    
    # Scraping settings
    MIN_DELAY = float(os.getenv('MIN_DELAY', '2.0'))
    MAX_DELAY = float(os.getenv('MAX_DELAY', '5.0')) 
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    # User agents
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    # Target subreddits
    TARGET_SUBREDDITS = [
        'india', 'bangalore', 'mumbai', 'delhi', 'pune', 'chennai', 'hyderabad',
        'AskIndia', 'CarsIndia', 'indianbikes', 'IndiaSpeaks', 'TwoXIndia'
    ]
    
    # Enhanced search queries with stricter civic sense focus
    SEARCH_QUERIES = [
        'civic sense india', 'road rage india', 'bad driving india', 
        'traffic sense india', 'indian roads civic', 'driving etiquette india',
        'road safety india', 'traffic violations india', 'rash driving india',
        'road accidents india', 'traffic rules india', 'lane discipline india', 
        'honking india', 'signal jumping india', 'wrong side driving india', 
        'helmet violation india', 'drunk driving india', 'civic responsibility india'
    ]
    
    # Enhanced topic keywords with more specific terms
    TOPIC_KEYWORDS = {
        'civic_sense': [
            'civic sense', 'civic responsibility', 'civic awareness', 'civic duty',
            'public behavior', 'social responsibility', 'civic education', 'civic consciousness'
        ],
        'road_rage': [
            'road rage', 'aggressive driving', 'driver anger', 'road violence', 
            'traffic fight', 'road anger', 'driver rage', 'traffic rage',
            'vehicle aggression', 'driving anger'
        ],
        'bad_driving': [
            'bad driving', 'rash driving', 'reckless driving', 'poor driving', 
            'dangerous driving', 'irresponsible driving', 'negligent driving',
            'careless driving', 'unsafe driving'
        ],
        'traffic_violations': [
            'signal jump', 'red light violation', 'wrong side', 'helmet violation', 
            'drunk driving', 'overspeeding', 'lane violation', 'traffic rules violation',
            'driving license violation', 'vehicle registration', 'traffic fine'
        ],
        'road_safety': [
            'road safety', 'accident prevention', 'safe driving', 'traffic rules', 
            'driving laws', 'safety awareness', 'road discipline', 'traffic discipline',
            'defensive driving', 'responsible driving'
        ]
    }
    
    def __init__(self):
        """Initialize config and debug email settings"""
        self.debug_email_config()
    
    def debug_email_config(self):
        """Debug email configuration on initialization"""
        print("\n🔍 Config Email Configuration Debug:")
        print(f"SENDER_EMAIL: {self.SENDER_EMAIL or 'NOT SET'}")
        print(f"RECIPIENT_EMAIL: {self.RECIPIENT_EMAIL or 'NOT SET'}")
        print(f"SENDER_PASSWORD: {'SET (' + str(len(self.SENDER_PASSWORD)) + ' chars)' if self.SENDER_PASSWORD else 'NOT SET'}")
        print(f"SMTP_SERVER: {self.SMTP_SERVER}")
        print(f"SMTP_PORT: {self.SMTP_PORT}")
        
        # Check if all required fields are present
        missing_fields = []
        if not self.SENDER_EMAIL:
            missing_fields.append("SENDER_EMAIL")
        if not self.SENDER_PASSWORD:
            missing_fields.append("SENDER_PASSWORD")
        if not self.RECIPIENT_EMAIL:
            missing_fields.append("RECIPIENT_EMAIL")
        
        if missing_fields:
            print(f"❌ Missing email fields: {', '.join(missing_fields)}")
            print("💡 Make sure your .env file contains:")
            print("   SENDER_EMAIL=your.email@gmail.com")
            print("   SENDER_PASSWORD=your_16_char_app_password")
            print("   RECIPIENT_EMAIL=your.personal@email.com")
        else:
            print("✅ All email fields are configured properly")
        print("-" * 60)
    
    def get_search_strategy(self) -> List[Dict[str, Any]]:
        """Get enhanced search strategy focusing on civic sense terms"""
        strategy = []
        
        # 1. Search popular subreddits for new posts (50% of requests)
        for subreddit in self.TARGET_SUBREDDITS[:6]:  # Top 6 subreddits
            strategy.append({
                'type': 'subreddit_new',
                'target': subreddit,
                'limit': 30  # Increased to get more candidates for filtering
            })
        
        # 2. Search specific civic sense queries (40% of requests)  
        priority_queries = self.SEARCH_QUERIES[:8]  # Top 8 specific queries
        for query in priority_queries:
            strategy.append({
                'type': 'search',
                'target': 'all',
                'query': query,
                'limit': 30
            })
        
        # 3. Hot posts from key subreddits (10% of requests)
        key_subreddits = ['india', 'bangalore', 'CarsIndia']
        for subreddit in key_subreddits:
            strategy.append({
                'type': 'subreddit_hot', 
                'target': subreddit,
                'limit': 50
            })
        
        return strategy
    
    def classify_post_topic(self, title: str, content: str = "") -> str:
        """Enhanced post topic classification"""
        text = f"{title} {content}".lower()
        
        # Priority order for classification
        priority_topics = [
            ('civic_sense', 'Civic Sense'),
            ('road_rage', 'Road Rage'),
            ('bad_driving', 'Bad Driving'),
            ('traffic_violations', 'Traffic Violations'),
            ('road_safety', 'Road Safety')
        ]
        
        for topic_key, topic_name in priority_topics:
            keywords = self.TOPIC_KEYWORDS[topic_key]
            if any(keyword in text for keyword in keywords):
                return topic_name
        
        return "General Traffic Discussion"
    
    def validate_email_config(self) -> bool:
        """Validate that all email configuration is present"""
        return all([self.SENDER_EMAIL, self.SENDER_PASSWORD, self.RECIPIENT_EMAIL])
    
    def get_missing_email_fields(self) -> List[str]:
        """Get list of missing email configuration fields"""
        missing = []
        if not self.SENDER_EMAIL:
            missing.append("SENDER_EMAIL")
        if not self.SENDER_PASSWORD:
            missing.append("SENDER_PASSWORD")
        if not self.RECIPIENT_EMAIL:
            missing.append("RECIPIENT_EMAIL")
        return missing
