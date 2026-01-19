# txt2xmind

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/txt2xmind/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/txt2xmind/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A powerful tool to convert indented text files into XMind mind maps. Supports both command-line interface and web application with optional AI-powered text structuring.

## Features

- **Text to XMind Conversion**: Convert indented text into professional XMind mind maps
- **Multiple Layouts**: Support for right, map, tree, and org chart layouts
- **Web Interface**: User-friendly Vue.js-based web application
- **AI Integration**: Optional OpenAI API integration for automatic text structuring
- **Unlimited Hierarchy**: Support for deeply nested structures
- **Docker Support**: Easy deployment with Docker and docker-compose
- **CI/CD Ready**: Automated testing and deployment with GitHub Actions

## Quick Start

### Using Docker (Recommended)

```bash
# Pull the image from GitHub Container Registry
docker pull ghcr.io/YOUR_USERNAME/txt2xmind:latest

# Run the container
docker run -d -p 8000:8000 ghcr.io/YOUR_USERNAME/txt2xmind:latest

# Or use docker-compose
docker-compose up -d
```

Visit `http://localhost:8000` in your browser.

### Local Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/txt2xmind.git
cd txt2xmind

# Install dependencies
pip install -r requirements.txt

# Run the web application
python web_app.py
```

Visit `http://localhost:8000` in your browser.

### Command Line Usage

```bash
# Basic usage
python generate_xmind.py input.txt

# With custom layout
python generate_xmind.py input.txt --layout map
```

## Input Format

Create a text file with indented structure (2 spaces or 1 tab per level):

```
Project Plan
  Phase 1: Planning
    Define Requirements
    Create Timeline
  Phase 2: Development
    Backend Development
    Frontend Development
  Phase 3: Testing
    Unit Tests
    Integration Tests
```

## API Documentation

### POST /api/generate

Generate XMind file from text.

**Request Body:**
```json
{
  "text": "Root\n  Child 1\n  Child 2",
  "layout": "right",
  "api_key": "optional-openai-key",
  "base_url": "optional-api-base-url",
  "model": "gpt-3.5-turbo"
}
```

**Response:**
```json
{
  "download_url": "/static/mindmap_20240119120000.xmind",
  "structured_text": "Root\n  Child 1\n  Child 2"
}
```

**Layout Options:**
- `right`: Right-aligned logic diagram (default)
- `map`: Center radial mind map
- `tree`: Tree diagram
- `org`: Organization chart (downward)

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Code quality checks
flake8 .
pylint generate_xmind.py web_app.py
```

### Project Structure

```
txt2xmind/
├── generate_xmind.py      # Core XMind generation logic
├── web_app.py             # FastAPI web application
├── static/
│   └── index.html         # Vue.js frontend
├── tests/                 # Test suite
│   ├── test_generate_xmind.py
│   └── test_web_app.py
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── .github/
    └── workflows/        # GitHub Actions workflows
```

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **CI/CD Pipeline**: Runs tests and builds Docker images on push to main
- **Manual Deployment**: Allows manual deployment to different environments

### Setting Up CI/CD

1. Create a repository on GitHub
2. Push your code to the repository
3. GitHub Actions will automatically run tests and build Docker images
4. Docker images are published to GitHub Container Registry (ghcr.io)

### Repository Settings

Ensure the following settings in your GitHub repository:

1. Go to Settings → Actions → General
2. Set "Workflow permissions" to "Read and write permissions"
3. Enable "Allow GitHub Actions to create and approve pull requests"

## Docker Deployment

### Build Locally

```bash
# Build the image
docker build -t txt2xmind:local .

# Run the container
docker run -d -p 8000:8000 txt2xmind:local
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

- `PYTHONUNBUFFERED`: Set to 1 for unbuffered Python output
- `OPENAI_API_KEY`: (Optional) Default OpenAI API key for AI features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [Vue.js](https://vuejs.org/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- XMind format specification

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/YOUR_USERNAME/txt2xmind/issues) on GitHub.
