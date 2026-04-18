# Spotify to YouTube Link Converter

A Python system that converts Spotify song links to YouTube video links.

## Features

- Extracts track information from Spotify URLs (open.spotify.com, spotify: URIs)
- Searches YouTube for matching videos
- Returns the most relevant YouTube video URL
- Comprehensive test suite included

## Installation

```bash
pip install requests
```

## Usage

### As a Module

```python
from spotify_to_youtube import convert_spotify_to_youtube

spotify_url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
youtube_url = convert_spotify_to_youtube(spotify_url)

if youtube_url:
    print(f"YouTube URL: {youtube_url}")
else:
    print("Conversion failed")
```

### Command Line

```bash
python spotify_to_youtube.py
```

Then enter your Spotify track URL when prompted.

### Using the Converter Class

```python
from spotify_to_youtube import SpotifyToYouTubeConverter

converter = SpotifyToYouTubeConverter()
result = converter.convert("https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp")
print(result)  # https://www.youtube.com/watch?v=...
```

## Supported URL Formats

- `https://open.spotify.com/track/{id}`
- `https://play.spotify.com/track/{id}`
- `spotify:track:{id}`

## Running Tests

```bash
python -m unittest test_spotify_to_youtube -v
```

## How It Works

1. **Extract Track ID**: Parses the Spotify URL to extract the track ID
2. **Get Track Info**: Uses Spotify's oEmbed API or page scraping to get artist and title
3. **Search YouTube**: Searches YouTube for the song using the artist and title
4. **Return Result**: Returns the first matching YouTube video URL

## Limitations

- Requires internet connection
- May not work if Spotify or YouTube changes their API/page structure
- Search results depend on YouTube's search algorithm

## License

MIT License
