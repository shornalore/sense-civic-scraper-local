# 🚗 Civic Sense Command Scraper

A specialized Reddit scraper focused on collecting discussions about civic sense, road rage, and bad driving behavior in India. Runs for a specified duration (default 10 minutes) and emails comprehensive reports.

## ✨ Features

- ⏱️ **Command-based execution** - Run manually when needed
- 🎯 **Targeted scraping** - Focuses on civic sense and traffic topics in India
- 🚫 **Anti-bot detection** - Advanced techniques to avoid being blocked
- 📧 **Email delivery** - Automatic email reports with attachments
- 📊 **Comprehensive reports** - Multiple report formats (detailed, links, statistics)
- 🔄 **Duplicate prevention** - Avoids collecting same posts multiple times
- 📈 **Real-time monitoring** - Progress tracking and performance metrics

## 🚀 Quick Start

1. **Clone/Download the project**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure environment**: Copy `.env.example` to `.env` and fill in your details
4. **Run the scraper**: `python civic_sense_scraper.py`

## 📧 Email Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App-Specific Password (16 characters)
3. Use this password in your `.env` file (not your regular Gmail password)

## 🎯 What It Scrapes

**Topics:**
- Civic sense in India
- Road rage incidents
- Bad driving behavior
- Traffic violations
- Road safety discussions

**Sources:**
- r/india, r/bangalore, r/mumbai, r/delhi
- r/AskIndia, r/CarsIndia, r/indianbikes
- Reddit-wide searches for civic sense keywords

## 🛡️ Anti-Detection Features

- Random delays between requests (2-5 seconds)
- Rotating user agents and headers
- Session rotation every 15-20 requests
- Realistic browser behavior simulation
- Rate limiting compliance (~1 request per 2-3 seconds)

## 📊 Report Types

1. **Comprehensive Report** - Detailed analysis with statistics and full post data
2. **Links Collection** - Quick reference with URLs and metadata
3. **Session Statistics** - Performance metrics and content analysis

## ⚙️ Configuration

Edit `config.py` to customize:
- Target subreddits
- Search queries
- Topic classification
- Timing settings
- Anti-detection parameters

## 🔧 Usage Examples

-Run with default 10 minutes

-python civic_sense_scraper.py
-Run for custom duration (will prompt for input)

-python civic_sense_scraper.py
-Enter: 15 (for 15 minutes)
-Stop early with Ctrl+C


## 📈 Expected Results

**10-minute session typically collects:**
- 50-150 unique posts
- 200-300 total requests
- 3 comprehensive report files
- Automatic email delivery

## 🚨 Important Notes

- **Respect Reddit's Terms of Service**
- **Use reasonable delays** (don't spam requests)
- **Monitor your usage** (check logs for any issues)
- **Keep email credentials secure**

## 🛠️ Troubleshooting

**Email not sending?**
- Check Gmail app password (16 characters)
- Verify 2FA is enabled
- Check SMTP settings in `.env`

**No posts collected?**
- Check internet connection
- Review search queries in `config.py`
- Check logs for error messages

**Getting blocked?**
- Increase delays in `config.py`
- Reduce scraping duration
- Check user agent rotation

---
Made with ❤️ for better civic sense awareness in India
