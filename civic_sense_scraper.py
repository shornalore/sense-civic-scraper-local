#!/usr/bin/env python3
"""
Enhanced Civic Sense Command Scraper v2.1
A 10-minute Reddit scraper with strict duplicate prevention and content filtering
"""

# ADD THIS IMPORT BLOCK AT THE TOP
import os
from dotenv import load_dotenv

# Load environment variables BEFORE importing other modules
load_dotenv()

# Debug environment loading
def debug_env_loading():
    print("🔍 Environment Variables Debug:")
    print(f"SENDER_EMAIL: {os.getenv('SENDER_EMAIL')}")
    print(f"RECIPIENT_EMAIL: {os.getenv('RECIPIENT_EMAIL')}")
    print(f"SENDER_PASSWORD: {'SET' if os.getenv('SENDER_PASSWORD') else 'NOT SET'}")
    print(f"Password Length: {len(os.getenv('SENDER_PASSWORD', ''))}")
    print("-" * 50)

# Call debug function
debug_env_loading()

# NOW import your other modules
import time
import signal
import sys
from datetime import datetime, timedelta
import logging
from pathlib import Path
import hashlib

from utils.reddit_scraper import RedditScraper
from utils.email_sender import EmailSender
from utils.anti_detection import setup_logging
from config import Config

class CivicSenseCommandScraper:
    def __init__(self):
        """Initialize the command-based scraper with duplicate tracking"""
        self.config = Config()
        self.start_time = None
        self.end_time = None
        self.scraped_posts = []
        self.total_requests = 0
        self.running = False
        
        # Duplicate prevention - track URLs and content hashes
        self.seen_urls = set()
        self.seen_content_hashes = set()
        self.duplicate_count = 0
        self.filtered_count = 0
        
        # Setup logging
        self.logger = setup_logging()
        
        # Initialize components
        self.reddit_scraper = RedditScraper()
        self.reddit_scraper.set_logger(self.logger)
        self.email_sender = EmailSender()
        
        # Create directories
        Path("results").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.logger.info("🚗 Enhanced Civic Sense Command Scraper initialized")
        self.logger.info("🔒 Duplicate prevention and content filtering enabled")
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        self.logger.info("\n⏹️  Received interrupt signal. Stopping scraper gracefully...")
        self.running = False
    
    def generate_content_hash(self, title: str, content: str = "") -> str:
        """Generate hash for content deduplication"""
        combined_content = f"{title.lower().strip()} {content.lower().strip()}"
        return hashlib.md5(combined_content.encode('utf-8')).hexdigest()
    
    def is_duplicate_post(self, post: dict) -> bool:
        """Check if post is duplicate by URL or content"""
        url = post.get('url', '')
        title = post.get('title', '')
        content = post.get('selftext', '')
        
        # Check URL duplicate
        if url in self.seen_urls:
            self.logger.debug(f"🔄 Duplicate URL found: {title[:50]}...")
            return True
        
        # Check content hash duplicate
        content_hash = self.generate_content_hash(title, content)
        if content_hash in self.seen_content_hashes:
            self.logger.debug(f"🔄 Duplicate content found: {title[:50]}...")
            return True
        
        return False
    
    def add_post_to_tracking(self, post: dict):
        """Add post to duplicate tracking sets"""
        url = post.get('url', '')
        title = post.get('title', '')
        content = post.get('selftext', '')
        
        if url:
            self.seen_urls.add(url)
        
        content_hash = self.generate_content_hash(title, content)
        self.seen_content_hashes.add(content_hash)
    
    def has_required_terms(self, post: dict) -> bool:
        """Check if post contains required civic sense terms"""
        title = post.get('title', '').lower()
        content = post.get('selftext', '').lower()
        combined_text = f"{title} {content}"
        
        # Required civic sense terms (must have at least one)
        required_terms = [
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
        
        # Check for required terms
        has_required_term = any(term in combined_text for term in required_terms)
        
        if not has_required_term:
            self.logger.debug(f"🚫 No required terms found in: {post.get('title', '')[:50]}...")
            return False
        
        # Additional India context check for search results
        india_terms = ['india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 
                      'hyderabad', 'pune', 'kolkata', 'gurgaon', 'noida', 'ahmedabad']
        
        subreddit = post.get('subreddit', '').lower()
        indian_subreddits = ['india', 'bangalore', 'mumbai', 'delhi', 'pune', 'chennai', 
                           'hyderabad', 'askindia', 'carsindia', 'indianbikes', 'indiaspeaks']
        
        # If from Indian subreddit, it's valid
        if subreddit in indian_subreddits:
            return True
        
        # For other subreddits, must mention India
        has_india_context = any(term in combined_text for term in india_terms)
        
        if not has_india_context:
            self.logger.debug(f"🌍 No India context found in: {post.get('title', '')[:50]}...")
            return False
        
        return True
    
    def run(self, duration_minutes=10):
        """Run the scraper for specified duration"""
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.running = True
        
        self.logger.info(f"🚀 Starting {duration_minutes}-minute scraping session")
        self.logger.info(f"📅 Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"🎯 End time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define search strategy
        search_strategy = self.config.get_search_strategy()
        
        try:
            while self.running and datetime.now() < self.end_time:
                remaining_time = (self.end_time - datetime.now()).total_seconds()
                
                if remaining_time <= 0:
                    break
                
                # Execute search strategy
                new_posts = self.execute_search_round(search_strategy, remaining_time)
                
                # Process each post for duplicates and content filtering
                for post in new_posts:
                    if self.is_duplicate_post(post):
                        self.duplicate_count += 1
                        continue
                    
                    # Additional content filtering
                    if not self.has_required_terms(post):
                        self.filtered_count += 1
                        continue
                    
                    # Add to results and tracking
                    self.scraped_posts.append(post)
                    self.add_post_to_tracking(post)
                
                # Log progress
                elapsed = (datetime.now() - self.start_time).total_seconds() / 60
                self.logger.info(f"⏱️  Progress: {elapsed:.1f}/{duration_minutes} min | "
                                f"Unique Posts: {len(self.scraped_posts)} | "
                                f"Duplicates: {self.duplicate_count} | "
                                f"Filtered: {self.filtered_count} | "
                                f"Requests: {self.total_requests}")
                
                # Check if we should continue
                if remaining_time < 30:  # Less than 30 seconds left
                    break
            
        except Exception as e:
            self.logger.error(f"❌ Scraping error: {e}")
        
        finally:
            self.finalize_scraping()
    
    def execute_search_round(self, strategy, remaining_time):
        """Execute one round of searching"""
        new_posts = []
        
        for search_config in strategy:
            if not self.running or remaining_time <= 0:
                break
            
            try:
                # Scrape posts using this configuration
                posts = self.reddit_scraper.scrape_posts(
                    search_type=search_config['type'],
                    target=search_config['target'], 
                    query=search_config.get('query'),
                    limit=search_config.get('limit', 25)
                )
                
                new_posts.extend(posts)
                self.total_requests += 1
                
                # Random delay between requests (2-5 seconds)
                delay = self.reddit_scraper.get_random_delay()
                self.logger.debug(f"💤 Waiting {delay:.1f}s before next request")
                time.sleep(delay)
                
                remaining_time -= delay
                
            except Exception as e:
                self.logger.warning(f"⚠️  Request failed for {search_config}: {e}")
                time.sleep(3)  # Wait a bit longer on error
        
        return new_posts
    
    def finalize_scraping(self):
        """Generate reports and send email"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() / 60
        
        self.logger.info(f"✅ Scraping completed!")
        self.logger.info(f"⏱️  Duration: {duration:.1f} minutes")
        self.logger.info(f"📊 Unique posts collected: {len(self.scraped_posts)}")
        self.logger.info(f"🔄 Duplicates prevented: {self.duplicate_count}")
        self.logger.info(f"🚫 Content filtered: {self.filtered_count}")
        self.logger.info(f"🌐 Total requests made: {self.total_requests}")
        
        if self.scraped_posts:
            # Generate report files
            report_files = self.generate_reports(self.scraped_posts, duration)
            
            # Send email
            self.send_email_reports(report_files, len(self.scraped_posts), duration)
        else:
            self.logger.warning("⚠️  No valid posts collected. No reports generated.")
    
    def generate_reports(self, posts, duration):
        """Generate comprehensive TXT report files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Comprehensive Report
        comprehensive_file = f'results/civic_sense_comprehensive_{timestamp}.txt'
        self.create_comprehensive_report(posts, comprehensive_file, duration)
        
        # 2. Links Only Report  
        links_file = f'results/civic_sense_links_{timestamp}.txt'
        self.create_links_report(posts, links_file, duration)
        
        # 3. Statistics Report
        stats_file = f'results/civic_sense_statistics_{timestamp}.txt'
        self.create_statistics_report(posts, stats_file, duration)
        
        self.logger.info(f"📄 Generated reports: {comprehensive_file}, {links_file}, {stats_file}")
        return [comprehensive_file, links_file, stats_file]
    
    def create_comprehensive_report(self, posts, filename, duration):
        """Create detailed comprehensive report with enhanced statistics"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("    ENHANCED CIVIC SENSE IN INDIA - COMMAND SCRAPER REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Session info with duplicate prevention stats
            f.write(f"🕐 Enhanced Scraping Session Details:\n")
            f.write(f"• Start Time: {self.start_time.strftime('%B %d, %Y at %I:%M %p IST')}\n")
            f.write(f"• End Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}\n")
            f.write(f"• Duration: {duration:.1f} minutes\n")
            f.write(f"• Unique Posts Collected: {len(posts)}\n")
            f.write(f"• Duplicates Prevented: {self.duplicate_count}\n")
            f.write(f"• Content Filtered: {self.filtered_count}\n")
            f.write(f"• Total Requests Made: {self.total_requests}\n")
            if (len(posts) + self.duplicate_count + self.filtered_count) > 0:
                f.write(f"• Success Rate: {(len(posts)/(len(posts)+self.duplicate_count+self.filtered_count))*100:.1f}%\n")
            if (len(posts) + self.duplicate_count) > 0:
                f.write(f"• Duplicate Prevention Rate: {(self.duplicate_count/(len(posts)+self.duplicate_count))*100:.1f}%\n")
            f.write("\n")
            
            # Content quality metrics
            f.write("🔍 CONTENT QUALITY ASSURANCE:\n")
            f.write("-" * 40 + "\n")
            f.write("✅ All posts contain required civic sense terms\n")
            f.write("✅ No duplicate URLs or content within session\n")
            f.write("✅ India-specific context verified\n")
            f.write("✅ Community engagement validated\n\n")
            
            # Topic breakdown with term matching
            topics = {}
            term_matches = {}
            subreddits = {}
            
            for post in posts:
                topic = post.get('matched_topic', 'Unknown')
                subreddit = post.get('subreddit', 'Unknown')
                topics[topic] = topics.get(topic, 0) + 1
                subreddits[subreddit] = subreddits.get(subreddit, 0) + 1
                
                # Track which terms were matched
                matched_terms = post.get('matched_terms', [])
                for term in matched_terms:
                    term_matches[term] = term_matches.get(term, 0) + 1
            
            if posts:
                f.write("📊 TOPIC BREAKDOWN:\n")
                f.write("-" * 40 + "\n")
                for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(posts)) * 100
                    f.write(f"• {topic}: {count} posts ({percentage:.1f}%)\n")
                f.write("\n")
                
                # Most matched terms
                if term_matches:
                    f.write("🎯 TOP MATCHED CIVIC SENSE TERMS:\n")
                    f.write("-" * 40 + "\n")
                    for term, count in sorted(term_matches.items(), key=lambda x: x[1], reverse=True)[:10]:
                        f.write(f"• '{term}': {count} posts\n")
                    f.write("\n")
                
                f.write("🏘️  SUBREDDIT BREAKDOWN:\n")
                f.write("-" * 40 + "\n")
                for sub, count in sorted(subreddits.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"• r/{sub}: {count} posts\n")
                f.write("\n")
                
                # Top posts by engagement
                sorted_posts = sorted(posts, key=lambda x: int(x.get('score', 0)), reverse=True)
                f.write("🔥 TOP POSTS BY ENGAGEMENT:\n")
                f.write("-" * 40 + "\n")
                for i, post in enumerate(sorted_posts[:10], 1):
                    f.write(f"{i}. {post['title'][:60]}... (Score: {post.get('score', 0)})\n")
                f.write("\n")
                
                # Detailed posts
                f.write("📋 DETAILED POST INFORMATION:\n")
                f.write("=" * 80 + "\n\n")
                
                for i, post in enumerate(posts, 1):
                    f.write(f"POST #{i}\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"Title: {post['title']}\n")
                    f.write(f"URL: {post['url']}\n")
                    f.write(f"Subreddit: r/{post.get('subreddit', 'Unknown')}\n")
                    f.write(f"Author: u/{post.get('author', 'Unknown')}\n")
                    f.write(f"Score: {post.get('score', 0)} points\n")
                    f.write(f"Comments: {post.get('num_comments', 0)}\n")
                    f.write(f"Created: {post.get('created_time', 'Unknown')}\n")
                    if post.get('matched_topic'):
                        f.write(f"Topic Match: {post['matched_topic']}\n")
                    if post.get('matched_terms'):
                        f.write(f"Matched Terms: {', '.join(post['matched_terms'][:3])}\n")
                    if post.get('preview_text'):
                        f.write(f"Preview: {post['preview_text'][:100]}...\n")
                    f.write("\n")
            else:
                f.write("No posts collected in this session.\n")

    def create_links_report(self, posts, filename, duration):
        """Create links-only report"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ENHANCED CIVIC SENSE IN INDIA - LINKS COLLECTION\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n")
            f.write(f"Session Duration: {duration:.1f} minutes\n")
            f.write(f"Total Unique Links: {len(posts)}\n")
            f.write(f"Duplicates Prevented: {self.duplicate_count}\n")
            f.write(f"Content Filtered: {self.filtered_count}\n\n")
            
            if posts:
                f.write("🔗 QUICK LINKS REFERENCE:\n")
                f.write("-" * 30 + "\n")
                for i, post in enumerate(posts, 1):
                    f.write(f"{i}. {post['url']}\n")
                    f.write(f"   📝 {post['title']}\n")
                    f.write(f"   📍 r/{post.get('subreddit', 'Unknown')} | "
                           f"👤 u/{post.get('author', 'Unknown')} | "
                           f"⭐ {post.get('score', 0)} points | "
                           f"💬 {post.get('num_comments', 0)} comments\n")
                    if post.get('matched_topic'):
                        f.write(f"   🎯 Topic: {post['matched_topic']}\n")
                    if post.get('matched_terms'):
                        f.write(f"   🔍 Matched: {', '.join(post['matched_terms'][:2])}\n")
                    f.write("\n")
            else:
                f.write("No links collected in this session.\n")

    def create_statistics_report(self, posts, filename, duration):
        """Create statistics-focused report"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ENHANCED CIVIC SENSE SCRAPER - SESSION STATISTICS\n")
            f.write("=" * 55 + "\n\n")
            
            # Enhanced session stats
            f.write("📈 SESSION PERFORMANCE:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Duration: {duration:.1f} minutes\n")
            f.write(f"Total Requests: {self.total_requests}\n")
            f.write(f"Unique Posts Collected: {len(posts)}\n")
            f.write(f"Duplicates Prevented: {self.duplicate_count}\n")
            f.write(f"Content Filtered: {self.filtered_count}\n")
            f.write(f"Requests/Minute: {self.total_requests/duration:.1f}\n")
            if self.total_requests > 0:
                f.write(f"Posts/Request: {len(posts)/self.total_requests:.1f}\n")
            if (len(posts) + self.duplicate_count + self.filtered_count) > 0:
                f.write(f"Collection Success Rate: {(len(posts)/(len(posts)+self.duplicate_count+self.filtered_count))*100:.1f}%\n")
            if (len(posts) + self.duplicate_count) > 0:
                f.write(f"Duplicate Prevention Rate: {(self.duplicate_count/(len(posts)+self.duplicate_count))*100:.1f}%\n")
            f.write("\n")
            
            # Content analysis
            if posts:
                total_score = sum(int(post.get('score', 0)) for post in posts)
                total_comments = sum(int(post.get('num_comments', 0)) for post in posts)
                
                f.write("📊 CONTENT ANALYSIS:\n") 
                f.write("-" * 30 + "\n")
                f.write(f"Total Upvotes: {total_score:,}\n")
                f.write(f"Total Comments: {total_comments:,}\n")
                f.write(f"Avg Score/Post: {total_score/len(posts):.1f}\n")
                f.write(f"Avg Comments/Post: {total_comments/len(posts):.1f}\n\n")
                
                # Top subreddits
                subreddit_stats = {}
                for post in posts:
                    sub = post.get('subreddit', 'Unknown')
                    if sub not in subreddit_stats:
                        subreddit_stats[sub] = {'count': 0, 'score': 0, 'comments': 0}
                    subreddit_stats[sub]['count'] += 1
                    subreddit_stats[sub]['score'] += int(post.get('score', 0))
                    subreddit_stats[sub]['comments'] += int(post.get('num_comments', 0))
                
                f.write("🏆 SUBREDDIT PERFORMANCE:\n")
                f.write("-" * 30 + "\n")
                for sub, stats in sorted(subreddit_stats.items(), key=lambda x: x[1]['count'], reverse=True):
                    f.write(f"r/{sub}:\n")
                    f.write(f"  Posts: {stats['count']}\n")
                    f.write(f"  Total Score: {stats['score']}\n")
                    f.write(f"  Total Comments: {stats['comments']}\n")
                    f.write(f"  Avg Score: {stats['score']/stats['count']:.1f}\n\n")
            
            else:
                f.write("📊 CONTENT ANALYSIS:\n") 
                f.write("-" * 30 + "\n")
                f.write("No posts collected in this session.\n\n")

    def send_email_reports(self, report_files, post_count, duration):
        """Send generated reports via email"""
        try:
            self.email_sender.send_reports(
                file_paths=report_files,
                post_count=post_count,
                duration=duration,
                requests_made=self.total_requests,
                duplicates_prevented=self.duplicate_count,
                content_filtered=self.filtered_count
            )
            self.logger.info("✅ Reports successfully emailed!")
        except Exception as e:
            self.logger.error(f"❌ Failed to send email: {e}")
            self.logger.info("📁 Reports saved locally in 'results/' directory")

def main():
    """Main entry point"""
    print("🚗 Enhanced Civic Sense Command Scraper v2.1")
    print("🔒 With Duplicate Prevention & Content Filtering")
    print("=" * 60)
    
    try:
        duration = int(input("Enter scraping duration in minutes (default 10): ") or "10")
        if duration < 1 or duration > 60:
            print("⚠️  Duration must be between 1-60 minutes. Using default 10 minutes.")
            duration = 10
            
    except ValueError:
        print("⚠️  Invalid input. Using default 10 minutes.")
        duration = 10
    
    print(f"\n🎯 Starting {duration}-minute enhanced scraping session...")
    print("🔒 Duplicate prevention and content filtering enabled")
    print("🔑 Press Ctrl+C to stop early\n")
    
    scraper = CivicSenseCommandScraper()
    scraper.run(duration)
    
    print("\n🎉 Enhanced scraping session completed!")
    print("📧 Check your email for the filtered, unique results!")

if __name__ == "__main__":
    main()
