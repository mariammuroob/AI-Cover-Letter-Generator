import streamlit as st
import pandas as pd
import uuid
import os
import re
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import chromadb
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Set up the page
st.set_page_config(
    page_title="AI Cover Letter Generator", 
    page_icon="📝", 
    layout="wide"
)

# Title and description
st.title("📝 AI Cover Letter Generator")
st.markdown("Create personalized cover letters in seconds using AI!")

# Initialize LLM with robust error handling
@st.cache_resource
def load_llm():
    """Initialize the LLM with multiple fallback methods for API key"""
    try:
        api_key = None
        
        # Method 1: Check environment variables
        api_key = os.getenv('GROQ_API_KEY')
        
        # Method 2: Check Streamlit secrets
        if not api_key:
            try:
                if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                    api_key = st.secrets['GROQ_API_KEY']
            except:
                pass
        
        # Method 3: Manual input in sidebar
        if not api_key:
            with st.sidebar:
                st.warning("🔑 GROQ API Key Required")
                api_key = st.text_input(
                    "Enter your GROQ API Key:",
                    type="password",
                    help="Get your API key from https://console.groq.com",
                    key="api_key_input"
                )
        
        if not api_key:
            st.error("""
            ## ❌ API Key Required
            
            To use this app, you need a GROQ API key:
            
            1. **Get a free API key:** Visit [https://console.groq.com](https://console.groq.com)
            2. **Add it to the sidebar** OR create a `.env` file with:
               ```
               GROQ_API_KEY=your_key_here
               ```
            3. **Restart the app** after adding the key
            
            The key should start with `gsk_` and be about 40 characters long.
            """)
            return None
        
        # Validate API key format
        if not api_key.startswith('gsk_') or len(api_key) < 20:
            st.error(f"""
            ❌ Invalid API Key Format
            
            Your key should:
            - Start with `gsk_`
            - Be about 40 characters long
            - You provided: `{api_key[:10]}...`
            
            Please check your key and try again.
            """)
            return None
        
        # Initialize the model
        llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            timeout=30
        )
        
        # Test the connection with a simple call
        with st.sidebar:
            with st.spinner("Testing API connection..."):
                try:
                    test_response = llm.invoke("Say 'Connected' in one word")
                    st.success("✅ API Connected Successfully!")
                except Exception as e:
                    st.error(f"❌ API Connection Failed: {str(e)}")
                    return None
        
        return llm
        
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        return None

# Setup portfolio database
@st.cache_resource
def setup_vector_db():
    """Setup ChromaDB for portfolio with error handling"""
    try:
        # Check if portfolio file exists
        if not os.path.exists("my_portfolio.csv"):
            st.sidebar.warning("📝 Portfolio file not found. Create 'my_portfolio.csv' for better matches.")
            return None
        
        # Read and validate CSV
        df = pd.read_csv("my_portfolio.csv")
        
        # Check required columns
        required_columns = ['Techstack', 'Links']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.sidebar.warning(f"⚠️ Portfolio missing columns: {', '.join(missing_columns)}")
            return None
        
        # Clean the data
        df = df.dropna(subset=['Techstack'])
        df['Techstack'] = df['Techstack'].astype(str)
        df['Links'] = df['Links'].fillna('').astype(str)
        
        if len(df) == 0:
            st.sidebar.warning("⚠️ No valid portfolio data found")
            return None
        
        # Setup ChromaDB
        client = chromadb.PersistentClient(path='vectorstore')
        collection = client.get_or_create_collection(
            name="portfolio",
            metadata={"description": "Portfolio projects and tech stacks"}
        )
        
        # Add data if collection is empty
        if collection.count() == 0:
            for idx, row in df.iterrows():
                if row['Techstack'].strip():  # Only add non-empty tech stacks
                    collection.add(
                        documents=row['Techstack'],
                        metadatas={"links": row['Links']},
                        ids=[f"project_{idx}_{uuid.uuid4().hex[:8]}"]
                    )
            st.sidebar.success(f"✅ Loaded {len(df)} portfolio items")
        
        return collection
        
    except Exception as e:
        st.sidebar.warning(f"⚠️ Portfolio setup skipped: {str(e)}")
        return None

# Sidebar for inputs
with st.sidebar:
    st.header("🔧 Settings")
    
    # API Key status
    st.subheader("🔑 API Status")
    
    # Job URL input
    job_url = st.text_input(
        "**Job URL:**",
        placeholder="https://company.com/careers/job-id",
        help="Paste the full URL of the job posting"
    )
    
    # Personal information
    st.subheader("👤 Your Information")
    your_name = st.text_input("**Your Name**", placeholder="John Doe")
    your_email = st.text_input("**Your Email**", placeholder="john@example.com")
    your_phone = st.text_input("**Your Phone**", placeholder="+1-234-567-8900")
    
    # Generate button
    generate_button = st.button(
        "🚀 Generate Cover Letter", 
        type="primary", 
        use_container_width=True
    )
    
    # Instructions
    st.markdown("---")
    st.subheader("ℹ️ How to Use")
    st.markdown("""
    1. **Enter** job posting URL
    2. **Fill** your personal details  
    3. **Click** Generate Cover Letter
    4. **Review** & customize the result
    5. **Download** and use!
    """)

# Initialize components
llm = load_llm()
portfolio_collection = setup_vector_db()

# Safe filename generator
def create_safe_filename(job_info, default="cover_letter"):
    """Create a safe filename from job info"""
    if job_info and isinstance(job_info, dict) and 'role' in job_info:
        role = job_info['role']
        if role and isinstance(role, str):
            # Remove special characters and replace spaces
            safe_name = re.sub(r'[^\w\s-]', '', role)
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            return f"cover_letter_{safe_name}"
    return default

# Main processing function
def generate_cover_letter(job_url, your_name, your_email, your_phone):
    """Generate cover letter from job URL"""
    try:
        # Step 1: Load and analyze job description
        with st.spinner("🌐 Analyzing job description..."):
            loader = WebBaseLoader(job_url)
            documents = loader.load()
            
            if not documents or not documents[0].page_content.strip():
                st.error("❌ No content found on this webpage. Please check the URL.")
                return None, None, None
                
            page_content = documents[0].page_content[:8000]  # Limit size

        # Step 2: Extract job information
        with st.spinner("🔍 Extracting job details..."):
            extract_prompt = PromptTemplate.from_template("""
            Analyze this job posting and extract key information. Return ONLY valid JSON:
            
            {{
                "role": "job title",
                "company": "company name", 
                "experience": "required experience level",
                "skills": "key skills and technologies required",
                "description": "brief job description",
                "requirements": "main requirements and qualifications"
            }}
            
            JOB POSTING:
            {page_data}
            
            JSON:
            """)
            
            chain_extract = extract_prompt | llm 
            extraction_result = chain_extract.invoke({'page_data': page_content})
            
            # Parse JSON response
            json_parser = JsonOutputParser()
            job_info = json_parser.parse(extraction_result.content)
            
            # Validate all required fields
            for field in ['role', 'company', 'experience', 'skills', 'description', 'requirements']:
                job_info[field] = job_info.get(field, "Not specified")

        # Display extracted job info
        st.subheader("📋 Job Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Role:** {job_info['role']}")
            st.info(f"**Company:** {job_info['company']}")
            st.info(f"**Experience:** {job_info['experience']}")
        
        with col2:
            st.info(f"**Skills:** {job_info['skills']}")
        
        st.text_area("**Description:**", job_info['description'], height=100, key="desc")
        st.text_area("**Requirements:**", job_info['requirements'], height=100, key="reqs")

        # Step 3: Find relevant portfolio items
        relevant_links = []
        with st.spinner("🔗 Finding relevant portfolio projects..."):
            if portfolio_collection and job_info.get('skills'):
                try:
                    skills_query = str(job_info['skills'])[:500]  # Limit query size
                    results = portfolio_collection.query(
                        query_texts=[skills_query],
                        n_results=2
                    )
                    
                    if results and 'metadatas' in results:
                        for metadata_list in results['metadatas']:
                            for item in metadata_list:
                                if item.get('links') and item['links'].strip():
                                    relevant_links.append(item['links'])
                    
                    if relevant_links:
                        st.success(f"✅ Found {len(relevant_links)} relevant portfolio projects!")
                    else:
                        st.info("ℹ️ No specific portfolio matches found")
                        
                except Exception as e:
                    st.warning(f"⚠️ Portfolio search skipped: {str(e)}")

        # Step 4: Generate cover letter
        with st.spinner("📝 Generating personalized cover letter..."):
            cover_letter_prompt = PromptTemplate.from_template("""
            JOB DETAILS:
            - Position: {role} at {company}
            - Requirements: {requirements}
            - Key Skills: {skills}
            - Description: {description}
            
            APPLICANT:
            - Name: {applicant_name}
            - Email: {applicant_email}
            - Phone: {applicant_phone}
            
            PORTFOLIO LINKS: {portfolio_links}
            
            INSTRUCTIONS:
            Write a professional, personalized cover letter that:
            1. Uses proper business letter format
            2. Addresses the specific role and company
            3. Matches applicant skills to job requirements
            4. Mentions relevant portfolio projects if available
            5. Shows enthusiasm for the company
            6. Includes call to action
            7. Is 300-400 words, professional tone
            
            COVER LETTER:
            """)
            
            chain_letter = cover_letter_prompt | llm
            letter_result = chain_letter.invoke({
                "role": job_info['role'],
                "company": job_info['company'],
                "requirements": job_info['requirements'],
                "skills": job_info['skills'],
                "description": job_info['description'],
                "applicant_name": your_name,
                "applicant_email": your_email,
                "applicant_phone": your_phone,
                "portfolio_links": relevant_links if relevant_links else "No specific portfolio links provided"
            })
        
        return letter_result.content, job_info, relevant_links
        
    except Exception as e:
        st.error(f"❌ Error generating cover letter: {str(e)}")
        return None, None, None

# Main application logic
if generate_button:
    if not llm:
        st.error("❌ Please configure your API key first")
    elif not job_url:
        st.warning("⚠️ Please enter a job URL")
    elif not your_name:
        st.warning("⚠️ Please enter your name")
    elif not job_url.startswith(('http://', 'https://')):
        st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
    else:
        cover_letter, job_info, portfolio_links = generate_cover_letter(
            job_url, your_name, your_email, your_phone
        )
        
        if cover_letter:
            st.subheader("📄 Your Personalized Cover Letter")
            
            # Display editable cover letter
            edited_letter = st.text_area(
                "Cover Letter Content",
                cover_letter,
                height=400,
                key="cover_letter_display"
            )
            
            # Action buttons
            st.subheader("💾 Download Options")
            col1, col2, col3 = st.columns(3)
            
            safe_filename = create_safe_filename(job_info)
            
            with col1:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.code(edited_letter)
                    st.success("✅ Copied to clipboard!")
            
            with col2:
                st.download_button(
                    label="📄 Download as TXT",
                    data=edited_letter,
                    file_name=f"{safe_filename}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                st.download_button(
                    label="💾 Download as DOC",
                    data=edited_letter,
                    file_name=f"{safe_filename}.doc",
                    mime="application/msword",
                    use_container_width=True
                )

else:
    # Welcome screen
    st.markdown("""
    ## 🚀 Welcome to AI Cover Letter Generator!
    
    Create **personalized, professional cover letters** in seconds using AI.
    
    ### ✨ Features:
    - **🔍 Smart Job Analysis** - Automatically extracts key requirements
    - **🎯 Portfolio Matching** - Finds your most relevant projects
    - **📝 AI-Powered Writing** - Generates tailored cover letters
    - **💾 Easy Export** - Download in multiple formats
    
    ### 📋 What You'll Need:
    1. **GROQ API Key** (free from [console.groq.com](https://console.groq.com))
    2. **Job Posting URL** (company career pages work best)
    3. **Your Basic Information** (name, email, phone)
    4. **Portfolio CSV** (optional, for better matches)
    
    ### 🎯 Getting Best Results:
    - Use **direct job posting URLs**
    - Ensure your **portfolio CSV is updated**
    - **Review and customize** the generated letter
    - **Company career pages** work better than job boards
    
    *Ready to create your perfect cover letter? Fill out the sidebar and click Generate!*
    """)

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit, LangChain, and Groq | "
    "[Get API Key](https://console.groq.com)"
)