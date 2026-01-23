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
# Install GPU-compatible PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Then install remaining dependencies
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
celery -A app.celery worker --concurrency=1 --loglevel=info

# For Windows
celery -A app.celery worker --concurrency=1 --loglevel=info --pool=solo

```

#### Firing the Frontend
```
cd frontend
npm i
npm run dev
```

### Some Screenshots showing the working

<img width="1904" height="900" alt="Dashboard-OP" src="https://github.com/user-attachments/assets/3a6ce658-76ef-41cf-adc0-75a0e7317b34" />
<img width="1913" height="913" alt="Dashboard1" src="https://github.com/user-attachments/assets/0faae98f-d5d3-4dea-8c9a-43074ddf9a5f" />
<img width="1913" height="913" alt="Dashboard1 (1)" src="https://github.com/user-attachments/assets/ee4b2122-528e-40fb-a001-5963d1332f24" />
<img width="1347" height="827" alt="Summary_english" src="https://github.com/user-attachments/assets/26095b24-3826-4b15-9eee-504785901870" />
<img width="921" height="591" alt="Summary_Hindi" src="https://github.com/user-attachments/assets/fbfd987a-b4d7-4609-ab04-6a547978f15f" />
<img width="1914" height="877" alt="Summary_Screen" src="https://github.com/user-attachments/assets/52bcfbe5-7e81-4c71-a6a6-d91653c09f51" />

