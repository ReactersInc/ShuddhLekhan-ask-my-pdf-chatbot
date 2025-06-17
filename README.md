# ask-my-pdf-chatbot
AskMyPDF is an AI-based PDF summarizer and chatbot powered by Google's Gemini via LangChain. Users can upload PDFs, automatically generate summaries, and interact with the document through natural language questions. Perfect for students, researchers, or professionals who want quick insights and deep document understanding.


## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone git@github.com:ReactersInc/ask-my-pdf-chatbot.git
```
### 2. Initializing the Repository
```
cd backend
```

#### Setting Up the Virtual enviroment (Linux/Windows/MacOS)
```
python3 -m venv venv
```
```
# For Linux/Mac
source venv/bin/activate  
```
```
#For Windows:
venv\Scripts\activate
```

#### Installing Python Dependencies

```
cd backend
pip install -r requirements.txt
```

### 3. Booting Up The Software

#### Start Redis Server (for Celery Broker)
```
# For Linux/Mac
redis-server
```
#### Firing the backend
```
cd backend
python3 app.py

# Adjust the concurrency based on your System Specs
celery -A app.celery worker --concurrency=2 --loglevel=info

# For Windows
celery -A app.celery worker --concurrency=1 --loglevel=info --pool=solo

```

#### Firing the Frontend
```
cd frontend
npm i
npm run dev
```
