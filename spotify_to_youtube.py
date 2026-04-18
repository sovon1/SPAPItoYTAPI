"""
Spotify to YouTube Link Converter

A system that converts Spotify song links to YouTube video links.
"""

import re
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlparse, parse_qs


class SpotifyTrackExtractor:
    """Extract track information from Spotify URLs."""
    
    SPOTIFY_URL_PATTERN = re.compile(
        r'(?:spotify:(track|album|playlist):|https?://(?:open\.spotify\.com/|play\.spotify\.com/)(track|album|playlist)/)([a-zA-Z0-9]+)'
    )
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_track_id(self, url: str) -> Optional[str]:
        """Extract track ID from Spotify URL."""
        match = self.SPOTIFY_URL_PATTERN.search(url)
        if match:
            # The last group is always the ID regardless of URL format
            return match.groups()[-1]
        return None
    
    def get_track_info(self, track_id: str) -> Optional[Dict[str, str]]:
        """
        Get track information (artist and title) from Spotify.
        
        Uses oEmbed API or falls back to open.spotify.com page scraping.
        """
        # Try oEmbed API first
        try:
            oembed_url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/track/{track_id}"
            response = self.session.get(oembed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                title = data.get('title', '')
                if title:
                    return self._parse_title(title)
        except Exception:
            pass
        
        # Fallback: try to fetch the track page
        try:
            track_url = f"https://open.spotify.com/track/{track_id}"
            response = self.session.get(track_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                # Look for meta tags in the HTML
                html = response.text
                
                # Try to find title in meta tags
                title_match = re.search(
                    r'<meta[^>]*name="description"[^>]*content="([^"]*)"',
                    html,
                    re.IGNORECASE
                )
                if title_match:
                    description = title_match.group(1)
                    # Description format: "Song by Artist · Song Title"
                    return self._parse_spotify_description(description)
        except Exception:
            pass
        
        return None
    
    def _parse_title(self, title: str) -> Dict[str, str]:
        """Parse title from oEmbed response."""
        # oEmbed returns "Artist - Song Title"
        if ' - ' in title:
            parts = title.split(' - ', 1)
            return {
                'artist': parts[0].strip(),
                'title': parts[1].strip()
            }
        return {'artist': '', 'title': title.strip()}
    
    def _parse_spotify_description(self, description: str) -> Dict[str, str]:
        """Parse description from Spotify page meta tag."""
        # Format: "Song by Artist · Song Title" or similar
        if '·' in description:
            parts = description.split('·', 1)
            if len(parts) == 2:
                artist_part = parts[0].strip()
                title_part = parts[1].strip()
                
                # Remove "Song by " prefix if present
                if artist_part.startswith('Song by '):
                    artist = artist_part[8:]
                else:
                    artist = artist_part
                
                return {'artist': artist, 'title': title_part}
        
        return {'artist': '', 'title': description}


class YouTubeSearcher:
    """Search for YouTube videos matching track information."""
    
    SEARCH_URL = "https://www.youtube.com/results"
    WATCH_URL = "https://www.youtube.com/watch?v={}"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def search(self, artist: str, title: str) -> Optional[str]:
        """
        Search YouTube for a song and return the video URL.
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            YouTube video URL or None if not found
        """
        query = f"{artist} {title}".strip()
        if not query:
            return None
        
        try:
            params = {'search_query': query}
            response = self.session.get(
                self.SEARCH_URL,
                params=params,
                timeout=10,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                # Extract video ID from results
                video_id = self._extract_first_video_id(response.text)
                if video_id:
                    return self.WATCH_URL.format(video_id)
        except Exception:
            pass
        
        return None
    
    def _extract_first_video_id(self, html: str) -> Optional[str]:
        """Extract the first video ID from YouTube search results."""
        # Pattern for video IDs in YouTube search results
        patterns = [
            r'/watch\?v=([a-zA-Z0-9_-]{11})',
            r'"videoId":"([a-zA-Z0-9_-]{11})"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            if matches:
                # Filter out common false positives
                for video_id in matches:
                    if self._is_valid_video_id(video_id):
                        return video_id
        
        return None
    
    def _is_valid_video_id(self, video_id: str) -> bool:
        """Check if a video ID is valid (not a playlist or other content)."""
        # Filter out known non-video IDs
        invalid_prefixes = ['playlist', 'channel', 'user']
        return not any(video_id.startswith(prefix) for prefix in invalid_prefixes)


class SpotifyToYouTubeConverter:
    """Main converter class that orchestrates the conversion process."""
    
    def __init__(self):
        self.spotify_extractor = SpotifyTrackExtractor()
        self.youtube_searcher = YouTubeSearcher()
    
    def convert(self, spotify_url: str) -> Optional[str]:
        """
        Convert a Spotify track URL to a YouTube video URL.
        
        Args:
            spotify_url: Spotify track URL
            
        Returns:
            YouTube video URL or None if conversion fails
        """
        # Extract track ID
        track_id = self.spotify_extractor.extract_track_id(spotify_url)
        if not track_id:
            print(f"Error: Could not extract track ID from URL: {spotify_url}")
            return None
        
        # Get track information
        track_info = self.spotify_extractor.get_track_info(track_id)
        if not track_info:
            print(f"Error: Could not retrieve track information for ID: {track_id}")
            return None
        
        artist = track_info['artist']
        title = track_info['title']
        
        print(f"Found track: {artist} - {title}")
        
        # Search YouTube
        youtube_url = self.youtube_searcher.search(artist, title)
        if not youtube_url:
            print("Error: Could not find matching video on YouTube")
            return None
        
        return youtube_url


def convert_spotify_to_youtube(spotify_url: str) -> Optional[str]:
    """
    Convenience function to convert a Spotify URL to YouTube URL.
    
    Args:
        spotify_url: Spotify track URL
        
    Returns:
        YouTube video URL or None if conversion fails
    """
    converter = SpotifyToYouTubeConverter()
    return converter.convert(spotify_url)


if __name__ == "__main__":
    # Example usage
    test_url = input("Enter Spotify track URL: ")
    result = convert_spotify_to_youtube(test_url)
    if result:
        print(f"\nYouTube URL: {result}")
    else:
        print("\nConversion failed.")
