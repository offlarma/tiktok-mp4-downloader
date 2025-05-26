# Tik To Mp4

A simple web application to download TikTok videos without watermark using FastAPI and yt-dlp.

## Features

- 🎥 Download TikTok videos without watermark
- 🚀 Fast and reliable using yt-dlp
- 📱 Mobile-friendly responsive design
- 🔒 Safe URL validation
- 🧹 Automatic cleanup of temporary files
- ⚡ Built with FastAPI for high performance

## Requirements

- Python 3.8+
- pip

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:

```bash
uvicorn main:app --reload
```

2. Open your browser and go to: `http://localhost:8000`

3. Paste a TikTok video URL and click "Download Video"

## API Endpoints

- `GET /` - Serves the main HTML interface
- `GET /download?url=<tiktok_url>` - Downloads the video file
- `GET /health` - Health check endpoint

## Deployment

This app is ready to be deployed on platforms like:

- **Render**: Add a `render.yaml` file
- **Railway**: Works out of the box
- **Heroku**: Add a `Procfile`
- **VPS**: Use gunicorn or uvicorn

### Example Procfile for Heroku:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Example for production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Security Considerations

For production deployment, consider adding:

- Rate limiting
- Input validation
- CORS configuration
- Authentication (if needed)
- Logging and monitoring

## License

This project is for educational purposes. Please respect TikTok's terms of service and content creators' rights.

## Troubleshooting

If you encounter issues:

1. Make sure you have the latest version of yt-dlp
2. Check that the TikTok URL is valid and accessible
3. Ensure you have sufficient disk space for temporary files
4. Check the console for error messages

## Contributing

Feel free to submit issues and enhancement requests! 