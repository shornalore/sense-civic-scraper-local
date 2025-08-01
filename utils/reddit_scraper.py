"""
Enhanced Reddit scraping utilities with strict content filtering
"""

import requests
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import random

from .anti_detection import AntiDetectionManager
from config import Config

class RedditScraper:
    """Enhanced Reddit scraper with strict content filtering"""
    
    def __init__(self):
        self.config = Config()
        self.anti_detection = AntiDetectionManager(self.config)
        self.session = requests.Session()
        self.logger = None
        self._setup_session()
        
    def _setup_session(self):
        """Setup requests session with proper headers"""
        self.session.headers.update(self.anti_detection.get_browser_headers())
        
    def set_logger(self, logger):
        """Set the logger instance"""
        self.logger = logger
        
    def get_random_delay(self) -> float:
        """Get random delay between requests"""
        return self.anti_detection.get_random_delay()
        
    def scrape_posts(self, search_type: str, target: str, query: str = None, limit: int = 25) -> List[Dict[str, Any]]:
        """Scrape posts based on search type and parameters"""
        
        if search_type == 'subreddit_new':
            return self._scrape_subreddit_new(target, limit)
        elif search_type == 'subreddit_hot':
            return self._scrape_subreddit_hot(target, limit)
        elif search_type == 'search':
            return self._scrape_search(query, limit)
        else:
            if self.logger:
                self.logger.warning(f"Unknown search type: {search_type}")
            return []
    
    def _scrape_subreddit_new(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape new posts from a subreddit"""
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
        return self._make_reddit_request(url, f"r/{subreddit} new posts")
    
    def _scrape_subreddit_hot(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape hot posts from a subreddit"""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        return self._make_reddit_request(url, f"r/{subreddit} hot posts")
    
    def _scrape_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search across Reddit"""
        encoded_query = quote(query)
        url = f"https://www.reddit.com/search.json?q={encoded_query}&sort=new&limit={limit}&t=week"
        return self._make_reddit_request(url, f"search: {query}")
    
    def _make_reddit_request(self, url: str, description: str) -> List[Dict[str, Any]]:
        """Make a request to Reddit and parse the response"""
        
        # Rotate session if needed
        if self.anti_detection.should_rotate_session():
            self._setup_session()
            if self.logger:
                self.logger.debug("🔄 Rotated session")
        
        try:
            if self.logger:
                self.logger.debug(f"🌐 Requesting: {description}")
            
            response = self.session.get(
                url, 
                timeout=self.config.REQUEST_TIMEOUT,
                headers=self.anti_detection.get_browser_headers()
            )
            
            self.anti_detection.increment_request_count()
            
            if response.status_code == 429:
                if self.logger:
                    self.logger.warning("⚠️  Rate limited. Waiting longer...")
                time.sleep(random.uniform(10, 20))
                return []
            
            if response.status_code != 200:
                if self.logger:
                    self.logger.warning(f"⚠️  HTTP {response.status_code} for {description}")
                return []
            
            data = response.json()
            posts = self._parse_reddit_response(data, description)
            
            if self.logger:
                self.logger.info(f"✅ {description}: {len(posts)} posts")
            
            return posts
            
        except requests.RequestException as e:
            if self.logger:
                self.logger.error(f"❌ Request failed for {description}: {e}")
            return []
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"❌ JSON decode failed for {description}: {e}")
            return []
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Unexpected error for {description}: {e}")
            return []
    
    def find_matched_terms(self, text: str) -> List[str]:
        """Find which specific civic sense terms are matched in the text"""
        text_lower = text.lower()
        matched_terms = []
        
        # All possible civic sense terms
        all_terms = [
            'civic sense', 'civic responsibility', 'civic awareness', 'civic duty',
            'road rage', 'road anger', 'driver rage', 'traffic rage',
            'bad driving', 'rash driving', 'reckless driving', 'poor driving', 'dangerous driving',
            'traffic violation', 'traffic rules', 'traffic law', 'driving rules',
            'signal jump', 'red light', 'wrong side', 'helmet violation', 'drunk driving',
            'road safety', 'driving safety', 'traffic safety', 'accident prevention',
            'lane discipline', 'lane cutting', 'improper lane', 'lane violation',
            'honking', 'unnecessary honking', 'horn misuse', 'noise pollution',
            'parking violation', 'wrong parking', 'blocking traffic', 'double parking',
            'overspeeding', 'speed limit', 'reckless speed', 'dangerous speed'
        ]
        
        for term in all_terms:
            if term in text_lower:
                matched_terms.append(term)
        
        return matched_terms
    
    def _parse_reddit_response(self, data: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
        """Parse Reddit JSON response into post data with enhanced filtering"""
        posts = []
        
        try:
            # Handle Reddit's JSON structure
            if 'data' in data and 'children' in data['data']:
                children = data['data']['children']
            else:
                return posts
            
            for child in children:
                if child.get('kind') != 't3':  # t3 = submission/post
                    continue
                    
                post_data = child.get('data', {})
                
                # Extract post information first
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                combined_text = f"{title} {selftext}"
                
                # Find matched terms
                matched_terms = self.find_matched_terms(combined_text)
                
                # Skip if no civic sense terms found
                if not matched_terms:
                    continue
                
                # Filter for relevant posts (enhanced)
                if not self._is_relevant_post_enhanced(post_data, matched_terms):
                    continue
                
                # Create post object
                post = {
                    'title': title,
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'subreddit': post_data.get('subreddit', ''),
                    'author': post_data.get('author', ''),
                    'score': post_data.get('score', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'created_utc': post_data.get('created_utc', 0),
                    'created_time': self._format_timestamp(post_data.get('created_utc', 0)),
                    'selftext': selftext,
                    'is_self': post_data.get('is_self', False),
                    'source': source,
                    'scraped_at': datetime.now().isoformat(),
                    'matched_terms': matched_terms  # Add matched terms
                }
                
                # Add topic classification
                post['matched_topic'] = self.config.classify_post_topic(title, selftext)
                
                # Add preview text
                if selftext:
                    post['preview_text'] = selftext[:200].replace('\n', ' ')
                else:
                    post['preview_text'] = title
                
                posts.append(post)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error parsing Reddit response: {e}")
        
        return posts
    
    def _is_relevant_post_enhanced(self, post_data: Dict[str, Any], matched_terms: List[str]) -> bool:
        """Enhanced relevance check with strict civic sense term requirements"""
        title = post_data.get('title', '').lower()
        selftext = post_data.get('selftext', '').lower()
        subreddit = post_data.get('subreddit', '').lower()
        
        # Must have matched civic sense terms (already checked, but double-check)
        if not matched_terms:
            return False
        
        # Combined text for analysis
        text = f"{title} {selftext}"
        
        # Check for India-related content
        india_keywords = ['india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 
                         'hyderabad', 'pune', 'kolkata', 'gurgaon', 'noida', 'ahmedabad']
        
        # Indian subreddits are automatically relevant
        indian_subreddits = ['india', 'bangalore', 'mumbai', 'delhi', 'pune', 'chennai', 
                           'hyderabad', 'askindia', 'carsindia', 'indianbikes', 'indiaspeaks']
        
        if subreddit in indian_subreddits:
            return True
        
        # For search results, must mention India
        if any(keyword in text for keyword in india_keywords):
            return True
        
        return False
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format Unix timestamp to readable string"""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return 'Unknown'
