# 🔍 Stage 2 - Intelligence Query Engine

[![Django](https://img.shields.io/badge/Django-6.0.4-092E20?logo=django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.17.1-a30000?logo=django)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?logo=railway)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Overview

The **Intelligence Query Engine** is a sophisticated demographic data API that transforms how clients interact with profile data. This system goes beyond basic CRUD operations by providing:

- **Advanced Filtering** - Combine multiple filters including age ranges, gender, country, and confidence scores
- **Smart Sorting** - Sort by age, creation date, or probability scores in ascending/descending order
- **Efficient Pagination** - Navigate through large datasets with configurable page sizes
- **Natural Language Search** - Query profiles using plain English (e.g., "young males from Nigeria")

Built for **Insighta Labs**, this API enables marketing teams, product analysts, and growth strategists to slice and query demographic data intuitively.

## 🚀 Live API

| Environment | URL |
|-------------|-----|
| **Production** | `https://hng14backendpythontaskoneb-production.up.railway.app` |
| **API Base** | `https://hng14backendpythontaskoneb-production.up.railway.app/api` |
| **Documentation** | `https://hng14backendpythontaskoneb-production.up.railway.app/` |

## 📊 Database Schema

```sql
profiles table
├── id                      UUID (Primary Key, v7)
├── name                    VARCHAR(100) UNIQUE
├── gender                  VARCHAR(20) INDEXED
├── gender_probability      FLOAT
├── age                     INTEGER INDEXED
├── age_group               VARCHAR(20) INDEXED
├── country_id              VARCHAR(2) INDEXED
├── country_name            VARCHAR(100)
├── country_probability     FLOAT
└── created_at              TIMESTAMP (auto-generated)

```

## 📡 API Endpoints
1. Get All Profiles (Advanced Query)
```
GET /api/profiles/
Returns paginated, filtered, and sorted profile data.

Query Parameters
Parameter	Type	Description	Example
gender	string	Filter by gender	male, female
age_group	string	Filter by age group	child, teenager, adult, senior
country_id	string	Filter by country code	NG, KE, ZA
min_age	integer	Minimum age	18
max_age	integer	Maximum age	65
min_gender_probability	float	Minimum gender confidence	0.8
min_country_probability	float	Minimum country confidence	0.7
sort_by	string	Field to sort by	age, created_at, gender_probability
order	string	Sort direction	asc, desc
page	integer	Page number (default: 1)	2
limit	integer	Items per page (default: 10, max: 50)	20
Example Request

```bash
curl "https://your-app.railway.app/api/profiles/?gender=male&country_id=NG&min_age=25&max_age=40&sort_by=age&order=desc&page=1&limit=10"
Success Response (200 OK)
```
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 2026,
  "data": [
    {
      "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
      "name": "emmanuel",
      "gender": "male",
      "age": 34,
      "age_group": "adult",
      "country_id": "NG",
      "country_name": "Nigeria"
    }
  ]
}
```
2. Natural Language Search
```
GET /api/profiles/search/

Converts plain English queries into structured filters using rule-based parsing.

Query Parameters
Parameter	Type	Description
q	string	Natural language query (required)
page	integer	Page number (default: 1)
limit	integer	Items per page (default: 10, max: 50)
Example Requests
bash
# Search for young males from Nigeria
curl "https://your-app.railway.app/api/profiles/search/?q=young%20males%20from%20nigeria"

# Search for females above 30
curl "https://your-app.railway.app/api/profiles/search/?q=females%20above%2030"

# Search for adult males from Kenya
curl "https://your-app.railway.app/api/profiles/search/?q=adult%20males%20from%20kenya"
Success Response (200 OK)

```json
{
  "status": "success",
  "query": "young males from nigeria",
  "interpreted_as": {
    "gender": "male",
    "min_age": 16,
    "max_age": 24,
    "country_id": "NG"
  },
  "page": 1,
  "limit": 10,
  "total": 42,
  "data": [...]
}
```
3. Get Single Profile
GET /api/profiles/{id}/

Retrieves a complete profile by its UUID.

Example Request
bash
curl "https://your-app.railway.app/api/profiles/550e8400-e29b-41d4-a716-446655440000/"
Success Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "emmanuel",
    "gender": "male",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 34,
    "age_group": "adult",
    "country_id": "NG",
    "country_name": "Nigeria",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}
```
4. Delete Profile
DELETE /api/profiles/{id}/

Permanently removes a profile from the database.

Example Request
```bash
curl -X DELETE "https://your-app.railway.app/api/profiles/550e8400-e29b-41d4-a716-446655440000/"
Response: 204 No Content
```

## 🔧 Natural Language Parsing Approach
How It Works
The natural language parser uses rule-based pattern matching (no AI/LLMs) to extract structured filters from plain English text. The system follows a deterministic pipeline:

```text
Input Query → Tokenization → Pattern Matching → Filter Extraction → API Parameters
Supported Patterns & Mappings
Gender Detection
Keywords	Maps To
male, males, man, men, boy, boys	gender=male
female, females, woman, women, girl, girls	gender=female
Age Group Detection
Keywords	Maps To
child, children, kid, kids	age_group=child
teenager, teenagers, teen, teens	age_group=teenager
adult, adults	age_group=adult
senior, seniors, elderly, old	age_group=senior
Descriptive Age Ranges
Keyword	Age Range
young, youth	16-24
middle aged	40-60
Numeric Pattern Extraction
Pattern	Example	Maps To
above/over X	"above 30"	min_age=30
below/under X	"under 25"	max_age=25
between X and Y	"between 20 and 30"	min_age=20, max_age=30
age/aged X	"age 35"	min_age=35, max_age=35
Country Detection
Supports 20+ African countries with common name mappings:

Country Name	ISO Code
nigeria	NG
kenya	KE
south africa	ZA
ghana	GH
egypt	EG
morocco	MA
angola	AO
ethiopia	ET
tanzania	TZ
uganda	UG
*(and 10+ more)*	
Example Parsing Demonstrations
User Query	Parsed Filters
"young males from nigeria"	gender=male, min_age=16, max_age=24, country_id=NG
"females above 30"	gender=female, min_age=30
"adult males from kenya"	gender=male, age_group=adult, country_id=KE
"teenagers between 15 and 18"	age_group=teenager, min_age=15, max_age=18
"seniors from ghana"	age_group=senior, country_id=GH
Parser Limitations
The current implementation has the following limitations:

Limitation	Explanation
No Boolean Logic	Cannot handle AND/OR/NOT combinations (e.g., "males OR females")
Single Country Only	Queries with multiple countries only use the first detected
No Negation	Cannot process "not from Nigeria" or "excluding seniors"
No Comparative Terms	Cannot interpret "older than average" or "younger than most"
Fixed Age Ranges	Descriptive terms like "young" have fixed ranges (16-24)
No Complex Phrases	Nested or compound queries may not parse correctly
Case Sensitivity	All keywords are case-insensitive but require exact spelling
No Synonyms	"bloke" for male or "lass" for female are not recognized
Future Enhancements (Not Implemented)
Support for complex boolean logic using parentheses
Dynamic age range detection based on dataset statistics
Fuzzy matching for country names
Support for relative terms ("older than", "younger than")
Multi-country and multi-gender queries
```
## 📦 Age Group Classification
Age Range	Age Group	Description
0 – 12	child	Early developmental years
13 – 19	teenager	Adolescent years
20 – 59	adult	Prime working age
60+	senior	Retirement age
⚠️ Error Responses
All errors follow a consistent structure:

```json
{
  "status": "error",
  "message": "<error description>"
}
Status Code	Meaning	Example Message
400	Bad Request	"Missing or empty query parameter"
400	Unable to Interpret	"Unable to interpret query"
404	Not Found	"Profile not found"
422	Unprocessable Entity	"Invalid sort_by field"
500	Server Error	"Internal server error"
```
## 🛠️ Technology Stack
Component	Technology	Version
Framework	Django	6.0.4
API Framework	Django REST Framework	3.17.1
Database	PostgreSQL (Neon) / SQLite	-
HTTP Client	Requests	2.33.1
CORS	django-cors-headers	4.9.0
Server	Gunicorn	21.2.0
Deployment	Railway	-
Language	Python	3.11

## 📂 Project Structure

hng-stage2-backend/
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── profiles_api/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── profiles/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── nlp_parser.py          # Natural language parsing logic
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py    # Database seeding utility
│   └── templates/
│       └── docs.html  # Interactive API documentation
│      
└── seed_profiles.json           # 2026 profile dataset


## 🚀 Local Development Setup
Prerequisites
Python 3.11 or higher
pip package manager
Virtual environment (recommended)
Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/FavieCodes/Hng14_backend_python_task_oneb.git
cd Hng14_backend_python_task_oneb

# 2. Create and activate virtual environment
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations profiles
python manage.py migrate

# 5. Seed the database (requires seed_profiles.json)
python manage.py seed_data

# 6. Start the development server
python manage.py runserver
Environment Variables
Create a .env file for local development:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```
## 🧪 Testing the API
Using cURL
```bash
# Get all profiles with filters
curl "http://localhost:8000/api/profiles/?gender=male&country_id=NG&min_age=25&sort_by=age&order=desc&limit=5"
```

# Natural language search
```curl "http://localhost:8000/api/profiles/search/?q=young%20males%20from%20nigeria"
```
# Get single profile
```curl "http://localhost:8000/api/profiles/{profile-id}/"
```
# Delete profile
```curl -X DELETE "http://localhost:8000/api/profiles/{profile-id}/"
Using the Interactive Documentation
Visit http://localhost:8000/ in your browser for the full interactive API documentation with built-in testing capabilities.
```
## 🌐 Deployment
Deployed on Railway
This API is deployed on Railway for production. Key deployment features:
Auto-scaling: Handles variable traffic loads
PostgreSQL database: Persistent data storage via Neon
HTTPS: Automatic SSL certificate management
Continuous deployment: Automatic redeployment on GitHub pushes
Deployment Steps (for maintainers)
```bash
# Install Railway CLI
npm install -g @railway/cli
# Login to Railway
railway login
# Link to existing project
railway link
# Deploy
railway up
```
## 📊 Performance Considerations
Feature	Optimization
Database Indexes	Indexed on gender, age_group, country_id, age, gender_probability, country_probability
Pagination	Maximum 50 items per request to prevent large payloads
Query Efficiency	All filters use indexed fields where possible
Natural Language	Rule-based (O(1) complexity), no external API calls

## 🔒 CORS Configuration
The API includes CORS headers for cross-origin requests:
```text
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```
## 🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author
Imo Udoh - HNG Cohort 14 Backend Track
GitHub: @FavieCodes
Email: udoh.imo.emmanuel@gmail.com

## 🙏 Acknowledgments
HNG Internship - Project requirements and mentorship
Genderize.io - Gender prediction API
Agify.io - Age prediction API
Nationalize.io - Nationality prediction API
Railway - Hosting and deployment platform
Neon - PostgreSQL database hosting

## 📞 Support
For issues or questions:
GitHub Issues: Create an issue
Documentation: Visit the interactive API docs at the base URL