AI Cover Letter Generator

<img width="1353" height="632" alt="image" src="https://github.com/user-attachments/assets/658dea79-e849-43d7-945b-48473f00a001" />
<img width="1358" height="638" alt="image" src="https://github.com/user-attachments/assets/88bf8e41-4903-4495-b66b-b6ebfd699b32" />
An intelligent, AI-powered cover letter generator that creates personalized, professional cover letters in seconds. Simply provide a job URL and watch as the app analyzes requirements and generates a tailored cover letter that matches your skills and experience.

🔍 Smart Job Analysis - Automatically extracts key information from job postings
🎯 Portfolio Matching - Finds your most relevant projects based on job requirements
📝 AI-Powered Writing - Generates professional, personalized cover letters using Groq's LLM
💾 Multiple Export Formats - Download as TXT or DOC files
⚡ Real-Time Processing- Fast generation using Groq's inference engine
🔒 Privacy Focused - Your data stays local, no third-party sharing

Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mariammuroob/AI-Cover-Letter-Generator.git
   cd AI-Cover-Letter-Generator
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Set up environment variables

bash
# Create .env file and add your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
Set up portfolio (optional)

Update my_portfolio.csv with your projects

Format: Techstack,Links (e.g., "Python, Django, React","https://github.com/yourproject")

Run the application

bash
streamlit run app.py

📋 Usage
Enter Job URL - Paste the job posting URL in the sidebar

Fill Personal Details - Add your name, email, and phone number

Generate - Click "Generate Cover Letter" and wait for AI magic

Review & Customize - Edit the generated letter as needed

Download - Export in your preferred format

Example Job URLs That Work Well:
Company career pages (Google, Microsoft, etc.)

LinkedIn job postings

Indeed job listings

AngelList startup jobs

🛠️ Technology Stack
Frontend: Streamlit

AI/ML: LangChain, Groq API (Llama 3 70B)

Data Processing: Pandas, ChromaDB

Web Scraping: LangChain WebBaseLoader

Vector Database: ChromaDB for portfolio matching
