# String Analyzer Service

A Django REST API service that analyzes strings and stores their computed properties including length, palindrome status, character frequency, and more.

## 🚀 Live Demo

**Base URL:** `https://stringanalyzerservice-production.up.railway.app`

## 📋 API Endpoints

### 1. Create/Analyze String
- **POST** `/analyze`
- **Request Body:**
```json
{
  "value": "string to analyze"
}
```
- **Success Response (201):**
```json
{
  "id": "sha256_hash",
  "value": "string to analyze",
  "properties": {
    "length": 16,
    "is_palindrome": false,
    "unique_characters": 12,
    "word_count": 3,
    "sha256_hash": "abc123...",
    "character_frequency_map": {"s": 2, "t": 3, "r": 2}
  },
  "created_at": "2025-08-27T10:00:00Z"
}
```

### 2. Get All Strings with Filtering
- **GET** `/strings`
- **Query Parameters:**
  - `is_palindrome` (boolean)
  - `min_length` (integer)
  - `max_length` (integer) 
  - `word_count` (integer)
  - `contains_character` (single character)

### 3. Get Specific String
- **GET** `/strings/{string_value}`

### 4. Natural Language Filtering
- **GET** `/strings/filter/natural?query=your natural language query`
- **Example Queries:**
  - "all single word palindromic strings"
  - "strings longer than 10 characters"
  - "palindromic strings that contain the first vowel"

### 5. Delete String
- **DELETE** `/strings/{string_value}/delete`

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Deglobeal/String_analyzer_service
cd string_analyzer_service
```

2. **Create virtual environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```
Edit `.env` file:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Start development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:
```
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-dotenv==1.0.0
gunicorn==21.2.0
whitenoise==6.6.0
```

Install with:
```bash
pip install -r requirements.txt
```

## 🌐 Production Deployment

### Environment Variables for Production
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.railway.app,.railway.app
```

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically on git push

## 🧪 Testing the API

### Using curl

**Create a string:**
```bash
curl -X POST https://stringanalyzerservice-production.up.railway.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"value": "hello world"}'
```

**Get all strings:**
```bash
curl https://stringanalyzerservice-production.up.railway.app/strings
```

**Filter strings:**
```bash
curl "https://stringanalyzerservice-production.up.railway.app/strings?is_palindrome=true&min_length=5"
```

**Natural language filter:**
```bash
curl "https://stringanalyzerservice-production.up.railway.app/strings/filter/natural?query=palindromic%20strings"
```

### Using Python requests

```python
import requests

BASE_URL = "https://stringanalyzerservice-production.up.railway.app"

# Create a string
response = requests.post(f"{BASE_URL}/analyze", json={"value": "test string"})
print(response.json())

# Get all strings
response = requests.get(f"{BASE_URL}/strings")
print(response.json())
```

## 📊 String Properties Analyzed

For each string, the service computes and stores:
- **length**: Number of characters
- **is_palindrome**: Boolean (case-insensitive)
- **unique_characters**: Count of distinct characters
- **word_count**: Number of words separated by whitespace
- **sha256_hash**: SHA-256 hash for unique identification
- **character_frequency_map**: Dictionary mapping characters to occurrence counts

## 🐛 Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `409` - Conflict (string already exists)
- `422` - Unprocessable Entity

## 📁 Project Structure

```
string_analyzer_service/
├── strings/
│   ├── models.py          # Database models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── urls.py            # URL routing
│   └── utils.py           # Analysis utilities
├── string_analyzer_service/
│   ├── settings.py        # Django settings
│   └── urls.py           # Project URL configuration
├── manage.py
├── requirements.txt
└── .env.example
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the API documentation above
2. Verify your request format
3. Ensure all required fields are provided
4. Check the response status codes and error messages

For additional help, please open an issue in the GitHub repository.

---

**Developed with ❤️ using Django REST Framework**