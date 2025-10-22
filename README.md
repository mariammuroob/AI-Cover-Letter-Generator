

<img width="1353" height="632" alt="image" src="https://github.com/user-attachments/assets/658dea79-e849-43d7-945b-48473f00a001" />

<img width="1358" height="638" alt="image" src="https://github.com/user-attachments/assets/88bf8e41-4903-4495-b66b-b6ebfd699b32" />


View Project:


```markdown
AI Cover Letter Generator

An intelligent AI-powered application that creates personalized, professional cover letters in seconds. Provide a job URL and the app automatically analyzes requirements to generate tailored cover letters matching your skills and experience.

✨ Features

- 🔍 Smart Job Analysis - Automatically extracts key information from job postings
- 🎯 Portfolio Matching - Finds your most relevant projects based on job requirements  
- 📝 AI-Powered Writing - Generates professional, personalized cover letters using Groq's LLM
- 💾 Multiple Export Formats - Download as TXT or DOC files
- ⚡ Real-Time Processing - Fast generation using Groq's inference engine
- 🔒 Privacy Focused - Your data stays local, no third-party sharing

 🚀 Installation

1. Clone the repository
   ```bash
   git clone https://github.com/mariammuroob/AI-Cover-Letter-Generator.git
   cd AI-Cover-Letter-Generator
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   # Create .env file and add your Groq API key
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

5. Set up portfolio (optional)
   - Update `my_portfolio.csv` with your projects
   - Format: `Techstack,Links` (e.g., `"Python, Django, React","https://github.com/yourproject"`)

6. Run the application
   ```bash
   streamlit run app.py
   ```

## 📋 Usage

1. **Enter Job URL** - Paste the job posting URL in the sidebar
2. **Fill Personal Details** - Add your name, email, and phone number
3. **Generate** - Click "Generate Cover Letter" and wait for processing
4. **Review & Customize** - Edit the generated letter as needed
5. **Download** - Export in your preferred format

### Supported Job URLs
- Company career pages (Google, Microsoft, etc.)
- LinkedIn job postings
- Indeed job listings
- AngelList startup jobs

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: LangChain, Groq API (Llama 3 70B)
- **Data Processing**: Pandas, ChromaDB
- **Web Scraping**: LangChain WebBaseLoader
- **Vector Database**: ChromaDB for portfolio matching



