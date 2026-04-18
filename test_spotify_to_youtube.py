"""
Test suite for Spotify to YouTube converter.
"""

import unittest
from unittest.mock import Mock, patch
from spotify_to_youtube import (
    SpotifyTrackExtractor,
    YouTubeSearcher,
    SpotifyToYouTubeConverter,
    convert_spotify_to_youtube
)


class TestSpotifyTrackExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = SpotifyTrackExtractor()
    
    def test_extract_track_id_from_open_url(self):
        """Test extracting track ID from open.spotify.com URL."""
        url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
        track_id = self.extractor.extract_track_id(url)
        self.assertEqual(track_id, "3n3Ppam7vgaVa1iaRUc9Lp")
    
    def test_extract_track_id_from_short_url(self):
        """Test extracting track ID from spotify: URI."""
        url = "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp"
        track_id = self.extractor.extract_track_id(url)
        self.assertEqual(track_id, "3n3Ppam7vgaVa1iaRUc9Lp")
    
    def test_extract_track_id_invalid_url(self):
        """Test with invalid URL returns None."""
        url = "https://example.com/invalid"
        track_id = self.extractor.extract_track_id(url)
        self.assertIsNone(track_id)
    
    def test_parse_title_with_artist(self):
        """Test parsing title with artist name."""
        title = "Mr. Brightside - The Killers"
        result = self.extractor._parse_title(title)
        self.assertEqual(result['artist'], 'Mr. Brightside')
        self.assertEqual(result['title'], 'The Killers')
    
    def test_parse_title_without_artist(self):
        """Test parsing title without separator."""
        title = "Some Song Title"
        result = self.extractor._parse_title(title)
        self.assertEqual(result['artist'], '')
        self.assertEqual(result['title'], 'Some Song Title')


class TestYouTubeSearcher(unittest.TestCase):
    
    def setUp(self):
        self.searcher = YouTubeSearcher()
    
    def test_is_valid_video_id(self):
        """Test video ID validation."""
        self.assertTrue(self.searcher._is_valid_video_id('dQw4w9WgXcQ'))
        self.assertTrue(self.searcher._is_valid_video_id('abc123XYZ89'))
        self.assertFalse(self.searcher._is_valid_video_id('playlist123'))
        self.assertFalse(self.searcher._is_valid_video_id('channel123'))
    
    @patch('requests.Session.get')
    def test_search_returns_url(self, mock_get):
        """Test that search returns a YouTube URL."""
        # Mock response with a video ID
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '/watch?v=dQw4w9WgXcQ'
        mock_get.return_value = mock_response
        
        result = self.searcher.search('Artist', 'Title')
        self.assertEqual(result, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    
    @patch('requests.Session.get')
    def test_search_returns_none_on_error(self, mock_get):
        """Test that search returns None on error."""
        mock_get.side_effect = Exception("Network error")
        
        result = self.searcher.search('Artist', 'Title')
        self.assertIsNone(result)


class TestSpotifyToYouTubeConverter(unittest.TestCase):
    
    def setUp(self):
        self.converter = SpotifyToYouTubeConverter()
    
    @patch.object(SpotifyTrackExtractor, 'extract_track_id')
    @patch.object(SpotifyTrackExtractor, 'get_track_info')
    @patch.object(YouTubeSearcher, 'search')
    def test_convert_success(self, mock_search, mock_get_info, mock_extract_id):
        """Test successful conversion."""
        mock_extract_id.return_value = 'track123'
        mock_get_info.return_value = {'artist': 'The Killers', 'title': 'Mr. Brightside'}
        mock_search.return_value = 'https://www.youtube.com/watch?v=abc123'
        
        result = self.converter.convert('https://open.spotify.com/track/track123')
        
        self.assertEqual(result, 'https://www.youtube.com/watch?v=abc123')
        mock_extract_id.assert_called_once()
        mock_get_info.assert_called_once()
        mock_search.assert_called_once()
    
    @patch.object(SpotifyTrackExtractor, 'extract_track_id')
    def test_convert_invalid_url(self, mock_extract_id):
        """Test conversion with invalid URL."""
        mock_extract_id.return_value = None
        
        result = self.converter.convert('https://invalid-url.com')
        
        self.assertIsNone(result)
        mock_extract_id.assert_called_once()
    
    @patch.object(SpotifyTrackExtractor, 'extract_track_id')
    @patch.object(SpotifyTrackExtractor, 'get_track_info')
    def test_convert_no_track_info(self, mock_get_info, mock_extract_id):
        """Test conversion when track info is not available."""
        mock_extract_id.return_value = 'track123'
        mock_get_info.return_value = None
        
        result = self.converter.convert('https://open.spotify.com/track/track123')
        
        self.assertIsNone(result)


class TestConvenienceFunction(unittest.TestCase):
    
    @patch('spotify_to_youtube.SpotifyToYouTubeConverter')
    def test_convert_spotify_to_youtube(self, mock_converter_class):
        """Test the convenience function."""
        mock_converter = Mock()
        mock_converter.convert.return_value = 'https://youtube.com/watch?v=test'
        mock_converter_class.return_value = mock_converter
        
        result = convert_spotify_to_youtube('https://open.spotify.com/track/test')
        
        self.assertEqual(result, 'https://youtube.com/watch?v=test')
        mock_converter.convert.assert_called_once()


if __name__ == '__main__':
    unittest.main()
