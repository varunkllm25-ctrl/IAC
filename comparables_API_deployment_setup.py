# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
sentence-transformers==2.2.2
sqlite3  # Built into Python
python-multipart==0.0.6
aiofiles==0.23.2

# Optional vector database dependencies
# chromadb==0.4.18
# pinecone-client==2.2.4
# weaviate-client==3.25.3

# Development dependencies
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# docker-compose.yml
"""
version: '3.8'

services:
  zillow-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./web:/usr/share/nginx/html
    depends_on:
      - zillow-api
    restart: unless-stopped
"""

# Dockerfile
"""
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# nginx.conf
"""
events {
    worker_connections 1024;
}

http {
    upstream api {
        server zillow-api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # Serve static files
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Proxy docs
        location /docs {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /redoc {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
"""

# setup.py
from setuptools import setup, find_packages

setup(
    name="zillow-comparables-api",
    version="1.0.0",
    description="AI-powered comparable property sales analysis API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/zillow-comparables-api",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
        "scikit-learn>=1.3.0",
        "sentence-transformers>=2.2.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "httpx>=0.25.2",
        ],
        "vector-db": [
            "chromadb>=0.4.18",
            "pinecone-client>=2.2.4",
            "weaviate-client>=3.25.3",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

# test_api.py
import pytest
import httpx
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_property():
    """Test adding a new property"""
    test_property = {
        "address": "123 Test Street",
        "city": "McKinney",
        "state": "TX",
        "zip_code": "75070",
        "price": 450000,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "square_feet": 2200,
        "property_type": "Single Family"
    }
    
    response = client.post("/api/properties", json=test_property)
    assert response.status_code == 200
    data = response.json()
    assert "zpid" in data
    assert "message" in data

# README.md content
README_CONTENT = '''
# 🏠 Zillow Comparables API

AI-powered comparable property sales analysis using vector embeddings and machine learning.

## Features

- **🧠 AI-Powered Comparables**: Vector similarity search using 422-dimensional property embeddings
- **📊 Market Analysis**: Real-time market trends and statistics
- **🎯 Precision Matching**: Multi-factor similarity scoring (location, features, price, market conditions)
- **⚡ Fast API**: High-performance FastAPI backend with async support
- **🌐 Modern Web UI**: Interactive React-based frontend with charts and visualizations
- **📱 Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/zillow-comparables-api.git
cd zillow-comparables-api

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access the application
open http://localhost:8000
```

## API Endpoints

### 🔍 Find Comparables
```http
POST /api/comparables
```

Find comparable properties using AI-powered vector similarity.

**Request Body:**
```json
{
  "target_property": {
    "address": "1530 Independence Pkwy",
    "city": "McKinney",
    "state": "TX",
    "zip_code": "75072",
    "price": 485000,
    "bedrooms": 4,
    "bathrooms": 3.0,
    "square_feet": 2850,
    "property_type": "Single Family"
  },
  "max_age_days": 180,
  "top_k": 10,
  "min_similarity": 0.5
}
```

### 🏘️ Search Properties
```http
GET /api/properties?city=McKinney&state=TX&max_age_days=180
```

Search properties by location with optional filters.

### 📈 Market Trends
```http
GET /api/market-trends/McKinney/TX?days=90
```

Get market statistics and trends for a specific area.

### ➕ Add Property
```http
POST /api/properties
```

Add new property data to the database.

## Architecture

### Backend (FastAPI)
- **Vector Embeddings**: 422-dimensional property fingerprints
- **Multi-Modal Features**: 
  - Numerical (40%): Price, bedrooms, square footage, etc.
  - Categorical (30%): Property type, neighborhood, school district
  - Location (20%): GPS + distances from major cities
  - Text (10%): Rich property descriptions
- **SQLite Database**: Property storage with embedded vectors
- **Real-time Analysis**: Instant similarity calculations

### Frontend (Vanilla JS + HTML/CSS)
- **Modern UI**: Glassmorphism design with smooth animations
- **Interactive Charts**: Price comparisons and market trends
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: Live search results and notifications

## Embedding System

The AI system creates a unique "fingerprint" for each property:

1. **Numerical Features** (11 dimensions): Price, bedrooms, bathrooms, square feet, lot size, year built, days on market, price per sq ft, garage spaces, stories, listing views

2. **Categorical Features** (~25 dimensions): One-hot encoded property type, neighborhood, school district, market trend

3. **Binary Features** (4 dimensions): Pool, fireplace, updated kitchen, updated bathrooms

4. **Location Features** (7 dimensions): Latitude, longitude, distances from major TX cities (Dallas, Austin, Houston, San Antonio, Fort Worth)

5. **Text Features** (384 dimensions): Sentence transformer embeddings of rich property descriptions

## Deployment Options

### Production Deployment

**AWS/Cloud:**
```bash
# Using AWS ECS/Fargate
aws ecs create-cluster --cluster-name zillow-api
aws ecs create-service --cluster zillow-api --service-name api --task-definition zillow-api:1

# Using Heroku
heroku create zillow-comparables-api
git push heroku main
```

**Self-hosted:**
```bash
# With SSL certificate
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

```bash
# .env file
ENV=production
LOG_LEVEL=info
DATABASE_URL=sqlite:///./data/properties.db
CORS_ORIGINS=["https://yourdomain.com"]

# Optional: Vector Database Configuration
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

## Performance & Scalability

- **Vector Search**: Sub-100ms similarity calculations
- **Database**: SQLite for development, PostgreSQL/MySQL for production
- **Caching**: Redis integration ready
- **Load Balancing**: Nginx reverse proxy included
- **Monitoring**: Built-in health checks and logging

## Integration Examples

### Python Client
```python
import requests

# Find comparables
response = requests.post('http://localhost:8000/api/comparables', json={
    'target_property': {
        'address': '1530 Independence Pkwy',
        'city': 'McKinney',
        'state': 'TX',
        'price': 485000,
        'bedrooms': 4,
        'bathrooms': 3.0,
        'square_feet': 2850
    }
})

comparables = response.json()
```

### JavaScript/React
```javascript
const findComparables = async (property) => {
  const response = await fetch('/api/comparables', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_property: property })
  });
  return response.json();
};
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/comparables" \
     -H "Content-Type: application/json" \
     -d '{"target_property":{"address":"1530 Independence Pkwy","city":"McKinney","state":"TX","price":485000}}'
```

## Development

### Running Tests
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint
flake8 .
mypy .
```

### Adding New Features

1. **New Embedding Features**: Add to `ZillowEmbeddingGenerator` class
2. **API Endpoints**: Add to `main.py` with proper Pydantic models
3. **UI Components**: Update `index.html` with new forms/displays
4. **Database Schema**: Modify `PropertyDatabase.init_database()`

## Use Cases

### Real Estate Professionals
- **Instant CMA**: Comparative Market Analysis in seconds
- **Client Presentations**: Visual comparables with similarity scores
- **Market Insights**: Trend analysis and pricing guidance

### Property Investors
- **Deal Analysis**: Quick ROI calculations using true comparables
- **Market Research**: Identify undervalued properties
- **Portfolio Management**: Track property values over time

### Home Buyers/Sellers
- **Fair Pricing**: Understand market value using AI analysis
- **Negotiation Power**: Data-driven comparable evidence
- **Market Timing**: Identify optimal buying/selling windows

### Fintech/PropTech
- **Automated Valuation**: Integrate into lending platforms
- **Risk Assessment**: Property value verification
- **Market APIs**: Power other real estate applications

## Roadmap

- [ ] **Enhanced ML Models**: XGBoost/Random Forest for price prediction
- [ ] **Image Analysis**: Property photo similarity using computer vision
- [ ] **Market Predictions**: Time series forecasting for price trends
- [ ] **Mobile Apps**: Native iOS/Android applications
- [ ] **Advanced Filters**: School ratings, crime data, walkability scores
- [ ] **Bulk Processing**: Batch analysis for large portfolios
- [ ] **Real-time Data**: Integration with live MLS feeds

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@zillowcomparables.com
- 💬 Slack: [Join our community](https://join.slack.com/your-workspace)
- 📖 Documentation: [API Docs](http://localhost:8000/docs)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/zillow-comparables-api/issues)

---

Built with ❤️ using FastAPI, React, and AI/ML technologies.
'''

# Create a simple startup script
STARTUP_SCRIPT = '''#!/bin/bash

echo "🏠 Starting Zillow Comparables API..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Using Docker deployment..."
    docker-compose up -d
    echo "✅ Application started successfully!"
    echo "🌐 Web UI: http://localhost"
    echo "📚 API Docs: http://localhost/docs"
else
    echo "🐍 Using Python deployment..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Start the application
    echo "Starting API server..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    
    echo "✅ Application started successfully!"
    echo "🌐 Web UI: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
fi

echo ""
echo "🎉 Zillow Comparables API is ready!"
echo "Try searching for: 1530 Independence Pkwy, McKinney TX 75072"
'''

# Save all content to files
def create_project_files():
    """Create all project files for deployment"""
    files = {
        'README.md': README_CONTENT,
        'startup.sh': STARTUP_SCRIPT,
    }
    
    print("📁 Project Structure:")
    print("zillow-comparables-api/")
    print("├── main.py                 # FastAPI application")
    print("├── zillow_embedding_system.py  # AI embedding system")
    print("├── index.html             # Web UI")
    print("├── requirements.txt       # Python dependencies")
    print("├── Dockerfile            # Docker configuration")
    print("├── docker-compose.yml    # Multi-container setup")
    print("├── nginx.conf           # Reverse proxy config")
    print("├── test_api.py          # API tests")
    print("├── setup.py             # Package setup")
    print("├── README.md            # Documentation")
    print("├── startup.sh           # Quick start script")
    print("└── data/                # SQLite database storage")
    
    return files

if __name__ == "__main__":
    create_project_files()_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_search_properties():
    """Test property search endpoint"""
    response = client.get("/api/properties?city=McKinney&state=TX")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_find_comparables():
    """Test comparables search endpoint"""
    test_request = {
        "target_property": {
            "address": "1530 Independence Pkwy",
            "city": "McKinney",
            "state": "TX",
            "zip_code": "75072",
            "price": 485000,
            "bedrooms": 4,
            "bathrooms": 3.0,
            "square_feet": 2850,
            "property_type": "Single Family"
        },
        "max_age_days": 180,
        "top_k": 5,
        "min_similarity": 0.5
    }
    
    response = client.post("/api/comparables", json=test_request)
    assert response.status_code == 200
    data = response.json()
    assert "target_property" in data
    assert "comparables" in data
    assert "market_stats" in data

def test_market_trends():
    """Test market trends endpoint"""
    response = client.get("/api/market-trends/McKinney/TX")
    assert response.status_code == 200
    data = response.json()
    assert "avg_price" in data
    assert "total_sales" in data

def test