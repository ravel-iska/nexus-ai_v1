# ═══════════════════════════════════════════════════════════════
# SOCIAL SCRAPER — Instagram, TikTok, Twitter/X, YouTube, Facebook
# Anti-detection scraping with data extraction
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import logging
import asyncio
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.scraper.social")


@dataclass
class ScrapedPost:
    platform: str
    post_id: str
    author: str
    text: str
    media_urls: list[str] = field(default_factory=list)
    likes: int = 0
    comments: int = 0
    shares: int = 0
    timestamp: str = ""
    hashtags: list[str] = field(default_factory=list)
    url: str = ""


class InstagramScraper:
    """Scrape Instagram posts, stories, reels using instaloader."""

    def __init__(self):
        self._loader = None
        logger.info("📸 Instagram Scraper initialized")

    async def init(self):
        try:
            import instaloader
            self._loader = instaloader.Instaloader(
                download_pictures=False, download_videos=False,
                download_video_thumbnails=False, download_geotags=False,
                download_comments=False, save_metadata=False,
                compress_json=False, quiet=True,
            )
        except ImportError:
            logger.error("❌ instaloader not installed")

    async def get_profile(self, username: str) -> dict:
        await self.init()
        import instaloader
        try:
            profile = instaloader.Profile.from_username(self._loader.context, username)
            return {
                "username": profile.username, "full_name": profile.full_name,
                "bio": profile.biography, "followers": profile.followers,
                "following": profile.followees, "posts_count": profile.mediacount,
                "is_private": profile.is_private, "is_verified": profile.is_verified,
                "profile_pic": profile.profile_pic_url,
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_posts(self, username: str, limit: int = 10) -> list[ScrapedPost]:
        await self.init()
        import instaloader
        posts = []
        try:
            profile = instaloader.Profile.from_username(self._loader.context, username)
            for i, post in enumerate(profile.get_posts()):
                if i >= limit:
                    break
                posts.append(ScrapedPost(
                    platform="instagram", post_id=post.shortcode, author=username,
                    text=post.caption or "", media_urls=[post.url],
                    likes=post.likes, comments=post.comments,
                    timestamp=post.date_utc.isoformat(),
                    hashtags=list(post.caption_hashtags),
                    url=f"https://instagram.com/p/{post.shortcode}/",
                ))
        except Exception as e:
            logger.error(f"❌ IG scrape error: {e}")
        return posts


class TikTokScraper:
    """Scrape TikTok videos and profiles."""

    def __init__(self):
        logger.info("🎵 TikTok Scraper initialized")

    async def get_user_videos(self, username: str, limit: int = 10) -> list[ScrapedPost]:
        try:
            from TikTokApi import TikTokApi
            async with TikTokApi() as api:
                user = api.user(username)
                videos = []
                async for video in user.videos(count=limit):
                    data = video.as_dict
                    videos.append(ScrapedPost(
                        platform="tiktok", post_id=data.get("id", ""),
                        author=username, text=data.get("desc", ""),
                        likes=data.get("stats", {}).get("diggCount", 0),
                        comments=data.get("stats", {}).get("commentCount", 0),
                        shares=data.get("stats", {}).get("shareCount", 0),
                        url=f"https://tiktok.com/@{username}/video/{data.get('id')}",
                    ))
                return videos
        except Exception as e:
            logger.error(f"❌ TikTok scrape error: {e}")
            return []


class TwitterScraper:
    """Scrape Twitter/X using tweepy."""

    def __init__(self, bearer_token: str = ""):
        self.bearer_token = bearer_token
        self._client = None
        logger.info("🐦 Twitter/X Scraper initialized")

    async def init(self):
        try:
            import tweepy
            self._client = tweepy.Client(bearer_token=self.bearer_token)
        except ImportError:
            logger.error("❌ tweepy not installed")

    async def search_tweets(self, query: str, limit: int = 10) -> list[ScrapedPost]:
        await self.init()
        if not self._client:
            return []
        try:
            tweets = self._client.search_recent_tweets(
                query=query, max_results=min(limit, 100),
                tweet_fields=["created_at", "public_metrics", "entities"],
            )
            results = []
            for tweet in (tweets.data or []):
                metrics = tweet.public_metrics or {}
                hashtags = [t["tag"] for t in (tweet.entities or {}).get("hashtags", [])]
                results.append(ScrapedPost(
                    platform="twitter", post_id=str(tweet.id),
                    author="", text=tweet.text,
                    likes=metrics.get("like_count", 0),
                    comments=metrics.get("reply_count", 0),
                    shares=metrics.get("retweet_count", 0),
                    timestamp=tweet.created_at.isoformat() if tweet.created_at else "",
                    hashtags=hashtags,
                ))
            return results
        except Exception as e:
            logger.error(f"❌ Twitter search error: {e}")
            return []


class YouTubeScraper:
    """Scrape YouTube video metadata and comments."""

    def __init__(self):
        logger.info("📺 YouTube Scraper initialized")

    async def search_videos(self, query: str, limit: int = 5) -> list[dict]:
        try:
            import yt_dlp
            ydl_opts = {"quiet": True, "extract_flat": True, "force_generic_extractor": False}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
                entries = result.get("entries", [])
                return [
                    {
                        "title": e.get("title", ""), "url": e.get("url", ""),
                        "duration": e.get("duration"), "view_count": e.get("view_count"),
                        "uploader": e.get("uploader", ""),
                    }
                    for e in entries
                ]
        except Exception as e:
            logger.error(f"❌ YT search error: {e}")
            return []


class SocialScraperHub:
    """Central hub for all social media scrapers."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.instagram = InstagramScraper()
        self.tiktok = TikTokScraper()
        self.twitter = TwitterScraper(self.config.get("twitter_bearer_token", ""))
        self.youtube = YouTubeScraper()
        logger.info("🌐 Social Scraper Hub initialized")

    async def scrape(self, platform: str, target: str, limit: int = 10) -> list:
        platform = platform.lower()
        if platform in ("ig", "instagram"):
            return await self.instagram.get_posts(target, limit)
        elif platform in ("tiktok", "tt"):
            return await self.tiktok.get_user_videos(target, limit)
        elif platform in ("twitter", "x"):
            return await self.twitter.search_tweets(target, limit)
        elif platform in ("youtube", "yt"):
            return await self.youtube.search_videos(target, limit)
        else:
            return [{"error": f"Platform '{platform}' tidak didukung"}]
