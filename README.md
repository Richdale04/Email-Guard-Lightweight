# Email Guard Backend

A lightweight FastAPI backend for email phishing detection, optimized for deployment on Render.

## Features

- **Primary ML Detection**: Uses the `phishing-detection-py` package for ML-based URL analysis
- **Rule-based Fallback**: Comprehensive fallback analysis using pattern matching
- **Authentication**: JWT-based authentication system
- **Scan History**: Track and retrieve previous scan results
- **Lightweight**: Optimized for cloud deployment with minimal dependencies

## API Endpoints

### Authentication
- `POST /auth/token` - Authenticate with token and get JWT
- `POST /auth/logout` - Logout and clear authentication cookie

### Email Scanning
- `POST /scan/email` - Scan email text for phishing/spam detection
- `GET /history` - Get scan history for authenticated user

### Health Check
- `GET /health` - Health check endpoint

## Response Format

All scan endpoints return results in the same format for frontend compatibility:

```json
{
  "results": [
    {
      "model_source": "PyPI",
      "model_name": "phishing-detection-py",
      "decision": "phishing|safe|spam|error",
      "confidence": 0.85,
      "description": "Analysis description"
    }
  ],
  "timestamp": "2024-01-01T12:00:00",
  "email_snippet": "Email content preview..."
}
```

## Deployment on Render

1. **Connect Repository**: Link your GitHub repository to Render
2. **Create Web Service**: Use the `render.yaml` configuration
3. **Environment Variables**: Set any required environment variables
4. **Deploy**: Render will automatically build and deploy your service

### Build Configuration
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start_backend.py`
- **Python Version**: 3.9.16

## Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python start_backend.py
   ```

3. **Access the API**: http://localhost:8000

## Project Structure

```
Email-Guard-Backend/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── scan.py             # Email scanning logic
│   ├── modules/
│   │   ├── authenticate.py # Authentication module
│   │   └── verify.py       # Input validation
│   └── requirements.txt    # Backend dependencies
├── ai/
│   └── email_guard.py      # AI analysis engine
├── start_backend.py        # Render startup script
├── render.yaml            # Render configuration
└── requirements.txt       # Root dependencies
```

## Dependencies

### Core Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `phishing-detection-py` - ML-based phishing detection
- `python-jose` - JWT handling
- `passlib` - Password hashing

### Removed Dependencies
- `transformers` - Heavy ML models
- `torch` - PyTorch framework
- `pandas`, `numpy` - Data processing
- `scikit-learn` - Machine learning
- `redis` - Caching (not needed for lightweight version)

## Authentication

The system uses a simple token-based authentication:

1. Users authenticate with a token via `/auth/token`
2. A JWT is created and stored in an HTTP-only cookie
3. Subsequent requests use the JWT for authentication
4. Tokens are stored in `backend/db/users.csv`

## Sample Tokens

For testing, the system includes sample tokens:
- `sample_token_1` (user1, user role)
- `sample_token_2` (user2, admin role)

## License

This project is licensed under the terms specified in the LICENSE file. 