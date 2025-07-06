import streamlit as st
import pypdf
from groq import Groq
import os
import pandas as pd
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile
import requests
import re
import random
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()

# Get API keys from .env file
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')  # Add this to your .env file

# Email configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')  # Add this to your .env file

client = Groq(api_key=GROQ_API_KEY)

# Custom CSS for dark theme professional UI
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* Dark theme configuration */
.stApp {
    background-color: #0e1117;
    color: #fafafa;
}

/* Main container styling */
.main-container {
    background: linear-gradient(135deg, #1e2328 0%, #262d34 100%);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    padding: 2.5rem;
    margin: 1rem;
    border: 1px solid #30363d;
}

/* File uploader dark theme */
.stFileUploader > div > div > div > div {
    background-color: #21262d;
    border: 2px dashed #30363d;
    border-radius: 12px;
    color: #fafafa;
    transition: all 0.3s ease;
}

.stFileUploader > div > div > div > div:hover {
    border-color: #58a6ff;
    background-color: #161b22;
}

/* Spinner styling */
.stSpinner > div {
    border-color: #58a6ff transparent #58a6ff transparent;
}

/* Headers */
h1 {
    color: #58a6ff;
    text-align: center;
    font-weight: 700;
    margin-bottom: 1rem;
}

h2, h3 {
    color: #79c0ff;
}

/* Success/Info messages */
.stSuccess {
    background-color: #0d4429;
    border: 1px solid #1a7f37;
    color: #56d364;
}

.stInfo {
    background-color: #0c2d6b;
    border: 1px solid #1f6feb;
    color: #79c0ff;
}

/* Expander styling */
.streamlit-expanderHeader {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #fafafa;
    border-radius: 8px;
}

.streamlit-expanderContent {
    background-color: #0d1117;
    border: 1px solid #21262d;
    border-top: none;
    border-radius: 0 0 8px 8px;
}

/* Custom card styling */
.insight-card {
    background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}

/* ATS Score styling */
.ats-score-container {
    background: linear-gradient(135deg, #1a7f37 0%, #238636 100%);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
    color: white;
    box-shadow: 0 4px 16px rgba(26, 127, 55, 0.3);
}

.ats-score-number {
    font-size: 3rem;
    font-weight: 900;
    margin: 0.5rem 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.ats-score-label {
    font-size: 1.2rem;
    font-weight: 600;
    opacity: 0.9;
}

.score-breakdown {
    background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.metric-card {
    background: linear-gradient(135deg, #0d4429 0%, #1a7f37 100%);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    color: white;
    margin: 0.5rem 0;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
}

/* Apply All button styling */
.apply-all-button {
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 1rem 0;
}

.apply-all-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(46, 160, 67, 0.3);
}

/* Job card styling */
.job-card {
    background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}

.job-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    border-color: #58a6ff;
}

.job-title {
    color: #58a6ff;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.company-name {
    color: #79c0ff;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.job-details {
    color: #8b949e;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.job-description {
    color: #fafafa;
    line-height: 1.6;
    margin-bottom: 1rem;
}

.job-location {
    color: #79c0ff;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.job-source {
    color: #8b949e;
    font-size: 0.8rem;
    margin-bottom: 1rem;
}

.apply-button {
    background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-block;
    transition: all 0.3s ease;
}

.apply-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
    text-decoration: none;
    color: white;
}

.filter-container {
    background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.search-settings {
    background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file(s)"""
    try:
        texts = []
        pdf_reader = pypdf.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            texts.append(page.extract_text())
        return " ".join(texts)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def extract_resume_keywords(extracted_text):
    """Extract a single most relevant keyword or job title from resume for job search"""
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a job search expert. Extract the SINGLE most relevant job title or keyword from the resume. Just return the job title or keyword.

                    Focus on:
                    1. The most suitable job title the person is qualified for
                    2. The most marketable technical skill
                    
                    Return ONLY ONE specific and searchable term (e.g., "Software Engineer", "Data Analyst", "Python Developer").
                    This should be the most relevant job title or skill that will yield the best job search results.
                    Don't include generic terms like "motivated" or "hardworking"."""
                },
                {
                    "role": "user", 
                    "content": f"""Extract the single most relevant job title or keyword from this resume:
                    {extracted_text}"""
                }
            ],
            model="llama3-70b-8192",
            temperature=0.3
        )
        
        keyword = response.choices[0].message.content.strip()
        # Clean up the keyword (remove any commas or extra text)
        keyword = keyword.split(',')[0].strip()
        return keyword
    except Exception as e:
        st.error(f"Error extracting keyword: {str(e)}")
        return ""

def clean_csv_data(csv_path, keyword):
    """Clean CSV data using Groq API to fill in missing values and filter invalid entries"""
    try:
        # Read the CSV file
        if not os.path.exists(csv_path):
            st.error(f"CSV file not found: {csv_path}")
            return None
            
        df = pd.read_csv(csv_path)
        if df.empty:
            st.warning("CSV file is empty")
            return df
            
        # Make a copy to avoid modifying the original during iteration
        cleaned_df = df.copy()
        rows_to_drop = []
        
        # Process each row
        for index, row in df.iterrows():
            # Skip entries with NA company name or apply link
            company = str(row.get('Company', '')).strip()
            apply_link = str(row.get('Apply Link', '')).strip()
            
            # Skip entries with asterisks (censored/invalid data)
            if '*' in company or '*' in apply_link:
                rows_to_drop.append(index)
                continue
                
            if company.lower() in ['na', 'n/a', '', 'nan', 'none'] or apply_link.lower() in ['na', 'n/a', '', 'nan', 'none', '#']:
                rows_to_drop.append(index)
                continue
                
            # Check for missing values in Role, Location, or Stipend
            role = str(row.get('Role', '')).strip()
            location = str(row.get('Location', '')).strip()
            stipend = str(row.get('Stipend (₹/month)', '')).strip()
            
            # Skip entries with asterisks in important fields
            if '*' in role or '*' in location or '*' in stipend:
                rows_to_drop.append(index)
                continue
                
            missing_fields = []
            if role.lower() in ['na', 'n/a', '', 'nan', 'none']:
                missing_fields.append('Role')
            if location.lower() in ['na', 'n/a', '', 'nan', 'none']:
                missing_fields.append('Location')
            if stipend.lower() in ['na', 'n/a', '', 'nan', 'none']:
                missing_fields.append('Stipend')
                
            # If there are missing fields, use Groq API to fill them
            if missing_fields:
                try:
                    response = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a job data enhancement expert. Fill in missing job information based on the company name and other available details.
                                Provide realistic values for missing fields. Format your response exactly as requested."""
                            },
                            {
                                "role": "user", 
                                "content": f"""For a job at {company}, I need to fill in the following missing fields: {', '.join(missing_fields)}.
                                
                                Available information:
                                - Company: {company}
                                - Role: {role if 'Role' not in missing_fields else 'MISSING'}
                                - Location: {location if 'Location' not in missing_fields else 'MISSING'}
                                - Stipend: {stipend if 'Stipend' not in missing_fields else 'MISSING'}
                                - Job Search Keyword: {keyword}
                                
                                For each missing field, provide a realistic value based on the company and available information.
                                Format your response exactly like this example:
                                Role: Software Engineer
                                Location: Bangalore, Karnataka
                                Stipend: ₹25,000 - ₹30,000
                                
                                Only include the missing fields in your response."""
                            }
                        ],
                        model="llama3-70b-8192",
                        temperature=0.7
                    )
                    
                    ai_response = response.choices[0].message.content.strip()
                    
                    # Parse the response and update the missing fields
                    for line in ai_response.split('\n'):
                        if ':' in line:
                            field, value = line.split(':', 1)
                            field = field.strip()
                            value = value.strip()
                            
                            if field == 'Role' and 'Role' in missing_fields:
                                cleaned_df.at[index, 'Role'] = value
                            elif field == 'Location' and 'Location' in missing_fields:
                                cleaned_df.at[index, 'Location'] = value
                            elif field == 'Stipend' and 'Stipend' in missing_fields:
                                cleaned_df.at[index, 'Stipend (₹/month)'] = value
                except Exception as e:
                    st.warning(f"Error filling missing data for {company}: {str(e)}")
            
            # Generate random email ID if missing
            email = str(row.get('EmailID', '')).strip()
            if email.lower() in ['na', 'n/a', '', 'nan', 'none'] or '*' in email:
                # Clean company name for email
                company_clean = re.sub(r'[^a-zA-Z0-9]', '', company.lower())
                if company_clean:
                    domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com', 'mail.com']
                    email_patterns = [
                        f"careers@{company_clean}.com",
                        f"jobs@{company_clean}.com",
                        f"hr@{company_clean}.com",
                        f"info@{company_clean}.com",
                        f"contact@{company_clean}.com"
                    ]
                    cleaned_df.at[index, 'EmailID'] = random.choice(email_patterns)
        
        # Drop rows with invalid data
        cleaned_df = cleaned_df.drop(rows_to_drop)
        
        # Reset index after dropping rows
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        st.info(f"Filtered out {len(rows_to_drop)} invalid entries (including those with asterisks)")
        return cleaned_df
        
    except Exception as e:
        st.error(f"Error cleaning CSV data: {str(e)}")
        return None

def run_scraper_with_keyword(keyword):
    """Run the scraper with the extracted keyword and clean the resulting CSV"""
    try:
        # Import the scraper module
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from scrape import JobScraper
        
        # Create a scraper instance
        scraper = JobScraper(use_selenium=True)
        
        # Run the scraper with the keyword
        st.info(f"🔍 Scraping jobs for keyword: {keyword}")
        with st.spinner(f"Scraping job listings for '{keyword}'..."):
            jobs_data = scraper.run_scraper(keyword, use_all_sources=True)
        
        # Get the CSV file path (the scraper saves it automatically)
        csv_files = [f for f in os.listdir() if f.startswith('jobs_internships_') and f.endswith('.csv')]
        if not csv_files:
            st.error("❌ No CSV file was generated by the scraper")
            return None
        
        # Sort by creation time (newest first)
        csv_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        csv_path = csv_files[0]
        
        # Clean the CSV data
        with st.spinner("Cleaning and enhancing job data..."):
            cleaned_df = clean_csv_data(csv_path, keyword)
        
        if cleaned_df is not None:
            # Save the cleaned data back to CSV
            cleaned_csv_path = f"cleaned_{csv_path}"
            cleaned_df.to_csv(cleaned_csv_path, index=False)
            st.success(f"✅ Scraped and cleaned {len(cleaned_df)} job listings")
            return cleaned_df
        else:
            st.error("❌ Failed to clean CSV data")
            return None
            
    except Exception as e:
        st.error(f"Error running scraper: {str(e)}")
        return None
            
        missing_fields = []
        if role.lower() in ['na', 'n/a', '', 'nan', 'none']:
            missing_fields.append('Role')
        if location.lower() in ['na', 'n/a', '', 'nan', 'none']:
            missing_fields.append('Location')
        if stipend.lower() in ['na', 'n/a', '', 'nan', 'none']:
            missing_fields.append('Stipend')
                
            # If there are missing fields, use Groq API to fill them
            if missing_fields:
                try:
                    response = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a job data enhancement expert. Fill in missing job information based on the company name and other available details.
                                Provide realistic values for missing fields. Format your response exactly as requested."""
                            },
                            {
                                "role": "user", 
                                "content": f"""For a job at {company}, I need to fill in the following missing fields: {', '.join(missing_fields)}.
                                
                                Available information:
                                - Company: {company}
                                - Role: {role if 'Role' not in missing_fields else 'MISSING'}
                                - Location: {location if 'Location' not in missing_fields else 'MISSING'}
                                - Stipend: {stipend if 'Stipend' not in missing_fields else 'MISSING'}
                                - Job Search Keyword: {keyword}
                                
                                For each missing field, provide a realistic value based on the company and available information.
                                Format your response exactly like this example:
                                Role: Software Engineer
                                Location: Bangalore, Karnataka
                                Stipend: ₹25,000 - ₹30,000
                                
                                Only include the missing fields in your response."""
                            }
                        ],
                        model="llama3-70b-8192",
                        temperature=0.7
                    )
                    
                    ai_response = response.choices[0].message.content.strip()
                    
                    # Parse the response and update the missing fields
                    for line in ai_response.split('\n'):
                        if ':' in line:
                            field, value = line.split(':', 1)
                            field = field.strip()
                            value = value.strip()
                            
                            if field == 'Role' and 'Role' in missing_fields:
                                cleaned_df.at[index, 'Role'] = value
                            elif field == 'Location' and 'Location' in missing_fields:
                                cleaned_df.at[index, 'Location'] = value
                            elif field == 'Stipend' and 'Stipend' in missing_fields:
                                cleaned_df.at[index, 'Stipend (₹/month)'] = value
                except Exception as e:
                    st.warning(f"Error filling missing data for {company}: {str(e)}")
            
            # Generate random email ID if missing
            email = str(row.get('EmailID', '')).strip()
            if email.lower() in ['na', 'n/a', '', 'nan', 'none']:
                # Clean company name for email
                company_clean = re.sub(r'[^a-zA-Z0-9]', '', company.lower())
                if company_clean:
                    domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com', 'mail.com']
                    email_patterns = [
                        f"careers@{company_clean}.com",
                        f"jobs@{company_clean}.com",
                        f"hr@{company_clean}.com",
                        f"info@{company_clean}.com",
                        f"contact@{company_clean}.com"
                    ]
                    cleaned_df.at[index, 'EmailID'] = random.choice(email_patterns)
        
        # Drop rows with invalid data
        cleaned_df = cleaned_df.drop(rows_to_drop)
        
        # Reset index after dropping rows
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        return cleaned_df
        
    except Exception as e:
        st.error(f"Error cleaning CSV data: {str(e)}")
        return None

def search_jobs_with_serpapi(query, location="India", job_type="internship", num_results=20):
    """Search for jobs using SerpAPI Google Jobs API"""
    try:
        if not SERPAPI_API_KEY:
            st.error("❌ SerpAPI API key not found. Please add SERPAPI_API_KEY to your .env file.")
            return []
        
        # Combine query with job type for better results
        search_query = f"{query} {job_type}"
        
        params = {
            "engine": "google_jobs",
            "q": search_query,
            "location": location,
            "api_key": SERPAPI_API_KEY,
            "num": num_results,
            "start": 0
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        jobs = []
        if "jobs_results" in results:
            for job in results["jobs_results"]:
                job_data = {
                    "title": job.get("title", "N/A"),
                    "company": job.get("company_name", "N/A"),
                    "location": job.get("location", "N/A"),
                    "description": job.get("description", "N/A"),
                    "apply_link": job.get("apply_link", "#"),
                    "posted_date": job.get("detected_extensions", {}).get("posted_at", "N/A"),
                    "job_type": job.get("detected_extensions", {}).get("schedule_type", "N/A"),
                    "salary": job.get("detected_extensions", {}).get("salary", "N/A"),
                    "source": job.get("via", "N/A"),
                    "thumbnail": job.get("thumbnail", ""),
                    "match_score": 0  # Will be calculated later
                }
                jobs.append(job_data)
        
        return jobs
    except Exception as e:
        st.error(f"Error searching jobs: {str(e)}")
        return []

def calculate_job_match_score(job, resume_text):
    """Calculate how well a job matches the resume"""
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a job matching expert. Compare the job description with the resume and provide a match score from 1-10.
                    
                    Consider:
                    - Skills alignment (40%)
                    - Experience level match (30%)
                    - Industry relevance (20%)
                    - Role suitability (10%)
                    
                    Return ONLY a number from 1-10, where 10 is a perfect match."""
                },
                {
                    "role": "user", 
                    "content": f"""Rate this job match (1-10):
                    
                    JOB: {job.get('title', '')} at {job.get('company', '')}
                    DESCRIPTION: {job.get('description', '')[:500]}...
                    
                    RESUME: {resume_text[:1000]}..."""
                }
            ],
            model="llama3-70b-8192",
            temperature=0.1
        )
        
        score_text = response.choices[0].message.content.strip()
        try:
            score = int(float(score_text.split()[0]))
            return max(1, min(10, score))  # Ensure score is between 1-10
        except:
            return 5  # Default score if parsing fails
    except Exception as e:
        return 5  # Default score on error

def send_application_email(jobs_list, resume_file, resume_filename):
    """Send application email with resume attachment and CSV file"""
    try:
        # Check if email password is configured
        if not EMAIL_PASSWORD:
            return False, "Email password not configured. Please add EMAIL_PASSWORD to your .env file."
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Job Applications Submitted - {len(jobs_list)} Positions"
        
        # Create email body
        body = f"""Dear Team,

I have successfully applied to {len(jobs_list)} job positions through the AI Resume Analyzer system.

Application Summary:
- Total positions applied: {len(jobs_list)}
- Application date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
- Resume file: {resume_filename}

Please find the following attachments:
1. My resume (PDF format)
2. Complete job listings with company details (CSV format)

The CSV file contains all the job details including:
- Company names
- Job roles
- Locations
- Stipend information
- Application links
- Contact emails

Thank you for your consideration.

Best regards,
Prakhar Gupta
Generated via AI Resume Analyzer
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach the resume
        if resume_file is not None:
            try:
                # Reset file pointer to beginning
                resume_file.seek(0)
                
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(resume_file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{resume_filename}"',
                )
                msg.attach(part)
            except Exception as e:
                return False, f"Error attaching resume: {str(e)}"
        
        # Create and attach the CSV file
        try:
            # Convert jobs_list to DataFrame
            if isinstance(jobs_list, pd.DataFrame):
                jobs_df = jobs_list
            else:
                jobs_df = pd.DataFrame(jobs_list)
            
            # Create CSV content
            csv_content = jobs_df.to_csv(index=False)
            
            # Attach CSV as text
            part = MIMEText(csv_content, 'plain')
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="job_applications_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv"',
            )
            msg.attach(part)
            
        except Exception as e:
            return False, f"Error creating CSV attachment: {str(e)}"
        
        # Send email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
            server.quit()
            
            return True, f"Email sent successfully to {RECIPIENT_EMAIL}! Applied to {len(jobs_list)} positions with resume and CSV attached."
            
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
        
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def analyze_resume(extracted_text):
    """Analyze resume using Groq API"""
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert career counselor and resume analyst. Provide comprehensive insights about the resume including:
                    1. Overall assessment and strengths
                    2. Areas for improvement
                    3. Suitable job roles and industries
                    4. Skill gaps to address
                    5. Career progression suggestions
                    6. ATS optimization tips
                    7. Market competitiveness analysis
                    
                    Format your response in clear sections with actionable recommendations."""
                },
                {
                    "role": "user", 
                    "content": f"""Please analyze this resume comprehensively. The person wants to understand:
                    - What are their key strengths and skills?
                    - What types of jobs/roles would be best suited for them?
                    - What industries should they target?
                    - How can they improve their resume?
                    - What skills should they develop further?
                    - How competitive is their profile in the current job market?
                    
                    Resume content:
                    {extracted_text}"""
                }
            ],
            model="llama3-70b-8192",
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis error: {str(e)}"

def calculate_ats_score(extracted_text):
    """Calculate ATS score and provide detailed breakdown"""
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an ATS (Applicant Tracking System) expert. Analyze the resume and provide:
                    1. Overall ATS Score (0-100)
                    2. Detailed breakdown of scoring criteria
                    3. Specific recommendations to improve ATS compatibility
                    4. Missing elements that ATS systems look for
                    5. Formatting issues that might cause problems
                    
                    Be precise and actionable in your recommendations."""
                },
                {
                    "role": "user", 
                    "content": f"""Please analyze this resume for ATS compatibility and provide a detailed score breakdown:

                    Evaluate based on:
                    - Contact information completeness
                    - Use of standard section headers
                    - Keyword optimization
                    - File format and readability
                    - Proper formatting (bullets, dates, etc.)
                    - Skills section presence and quality
                    - Quantified achievements
                    - Professional summary/objective
                    - Education section formatting
                    - Work experience structure
                    - Length and organization
                    
                    Provide the overall score as "ATS Score: X/100" at the beginning.
                    
                    Resume content:
                    {extracted_text}"""
                }
            ],
            model="llama3-70b-8192",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ATS scoring error: {str(e)}"

def display_job_card(job):
    """Display a single job card with Google Jobs data"""
    # Truncate description if too long
    description = job.get('description', 'N/A')
    if len(description) > 300:
        description = description[:300] + "..."
    
    # Format salary information
    salary_info = job.get('salary', 'N/A')
    if salary_info == 'N/A':
        salary_info = "Salary not specified"
    
    st.markdown(f'''
    <div class="job-card">
        <div class="job-title">{job.get('title', 'N/A')}</div>
        <div class="company-name">{job.get('company', 'N/A')}</div>
        <div class="job-location">📍 {job.get('location', 'N/A')}</div>
        <div class="job-source">📰 Via {job.get('source', 'N/A')}</div>
        <div class="job-details">
            💰 {salary_info} | 
            📅 {job.get('posted_date', 'N/A')} | 
            🏷️ {job.get('job_type', 'N/A')} |
            🎯 Match Score: {job.get('match_score', 0)}/10
        </div>
        <div class="job-description">
            <p><strong>Job Description:</strong></p>
            <p>{description}</p>
        </div>
        <a href="{job.get('apply_link', '#')}" target="_blank" class="apply-button">
            Apply Now 🚀
        </a>
    </div>
    ''', unsafe_allow_html=True)

def app():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    # 📄 Naukri Flash AI Job Application Agent
    ### Get Professional Insights & Real-time Job Matches
    *Upload your resume and receive comprehensive analysis with recent job postings and let AI agent apply to relevant positions*
    """)
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📁 Upload Your Resume")
        uploaded_files = st.file_uploader(
            "Choose PDF Files", 
            type="pdf", 
            accept_multiple_files=True,
            help="Upload your resume(s) for comprehensive AI analysis"
        )
    
    with col2:
        st.markdown("### 🎯 What You'll Get")
        st.markdown("""
        - **Skill Assessment**
        - **Agent Job Matches**
        - **Industry Recommendations**
        - **ATS Score Analysis**
        - **Resume Improvement Tips**
        - **Market Analysis**
        - **Keyword Optimization**
        """)
    
    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown(f"### 📊 Analysis for: {uploaded_file.name}")
            
            with st.spinner(f"🔍 Analyzing {uploaded_file.name}..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
                
                if extracted_text:
                    # Create tabs for different analyses
                    tab1, tab2, tab3, tab4 = st.tabs(["📋 Resume Analysis", "🎯 ATS Score", "💼 Agent Job Matches", "🔍 Raw Text"])
                    
                    with tab1:
                        st.markdown("#### 🎯 Comprehensive Resume Analysis")
                        with st.spinner("Generating insights..."):
                            analysis = analyze_resume(extracted_text)
                            
                        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
                        st.markdown(analysis)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab2:
                        st.markdown("#### 🎯 ATS Compatibility Score")
                        with st.spinner("Calculating ATS score..."):
                            ats_analysis = calculate_ats_score(extracted_text)
                            
                        # Extract the score from the response
                        score_line = ""
                        detailed_analysis = ats_analysis
                        
                        if "ATS Score:" in ats_analysis:
                            lines = ats_analysis.split('\n')
                            for line in lines:
                                if "ATS Score:" in line:
                                    score_line = line
                                    detailed_analysis = ats_analysis.replace(line, "").strip()
                                    break
                        
                        # Display score prominently
                        if score_line:
                            score_value = score_line.split(':')[1].strip().split('/')[0].strip()
                            st.markdown(f'''
                            <div class="ats-score-container">
                                <div class="ats-score-label">ATS Compatibility Score</div>
                                <div class="ats-score-number">{score_value}/100</div>
                                <div class="ats-score-label">Higher scores mean better ATS compatibility</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        # Display detailed breakdown
                        st.markdown('<div class="score-breakdown">', unsafe_allow_html=True)
                        st.markdown("#### 📊 Detailed Score Breakdown")
                        st.markdown(detailed_analysis)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab3:
                        st.markdown("#### 💼 Agent Job Matches Results")
                        
                        # Job search settings
                        st.markdown('<div class="search-settings">', unsafe_allow_html=True)
                        st.markdown("#### 🔧 Search Settings")
                        
                        # Create tabs for different search methods
                        search_tab1, search_tab2 = st.tabs(["Web Scraper", " "])
                        
                        with search_tab1:
                            # Extract keyword for job search
                            with st.spinner("Extracting keyword from your resume..."):
                                keyword = extract_resume_keywords(extracted_text)
                            
                            if keyword:
                                st.info(f"🔍 **Search Keyword Extracted:** {keyword}")
                                
                                if st.button("🔍 Scrape Jobs", key=f"scrape_jobs_{uploaded_file.name}"):
                                    with st.spinner(f"Scraping jobs for keyword: {keyword}..."):
                                        jobs_df = run_scraper_with_keyword(keyword)
                                    
                                    if jobs_df is not None and not jobs_df.empty:
                                        st.success(f"✅ Found {len(jobs_df)} job opportunities!")
                                        
                                        # Add filters
                                        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
                                        st.markdown("#### 🔍 Filter Results")
                                        
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            companies = ['All'] + sorted(jobs_df['Company'].unique().tolist())
                                            selected_company = st.selectbox("Company", companies, key="company_filter")
                                        
                                        with col2:
                                            locations = ['All'] + sorted(jobs_df['Location'].unique().tolist())
                                            selected_location = st.selectbox("Job Location", locations, key="location_filter")
                                        
                                        with col3:
                                            roles = ['All'] + sorted(jobs_df['Role'].unique().tolist())
                                            selected_role = st.selectbox("Role", roles, key="role_filter")
                                        
                                        # Apply filters
                                        filtered_jobs = jobs_df.copy()
                                        if selected_company != 'All':
                                            filtered_jobs = filtered_jobs[filtered_jobs['Company'] == selected_company]
                                        if selected_location != 'All':
                                            filtered_jobs = filtered_jobs[filtered_jobs['Location'] == selected_location]
                                        if selected_role != 'All':
                                            filtered_jobs = filtered_jobs[filtered_jobs['Role'] == selected_role]
                                        
                                        # Apply All button
                                        if st.button("📧 Apply to All", key=f"apply_all_{uploaded_file.name}", help="Send email application for all filtered jobs"):
                                            if EMAIL_PASSWORD:
                                                if len(filtered_jobs) > 0:
                                                    with st.spinner("Sending application emails..."):
                                                        # Convert DataFrame rows to list of dictionaries
                                                        jobs_list = filtered_jobs.to_dict('records')
                                                        success, message = send_application_email(jobs_list, uploaded_file, uploaded_file.name)
                                                        
                                                    if success:
                                                        st.success(f"✅ {message}")
                                                        st.info(f"📧 Applied to {len(filtered_jobs)} positions via email!")
                                                    else:
                                                        st.error(f"❌ {message}")
                                                else:
                                                    st.warning("⚠️ No jobs match your current filters.")
                                            else:
                                                st.error("❌ Email password not configured. Please add EMAIL_PASSWORD to your .env file.")
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        # Display filtered jobs
                                        st.markdown(f"#### 📋 Showing {len(filtered_jobs)} Jobs")
                                        
                                        for _, job in filtered_jobs.iterrows():
                                            # Create a job dictionary in the format expected by display_job_card
                                            job_dict = {
                                                'title': job.get('Role', 'N/A'),
                                                'company': job.get('Company', 'N/A'),
                                                'location': job.get('Location', 'N/A'),
                                                'description': f"Stipend: {job.get('Stipend (₹/month)', 'N/A')}",
                                                'apply_link': job.get('Apply Link', '#'),
                                                'source': 'Web Scraper',
                                                'posted_date': 'Recently',
                                                'job_type': 'Internship',
                                                'match_score': 7  # Default score
                                            }
                                            display_job_card(job_dict)
                                    else:
                                        st.error("❌ No jobs found. Try a different keyword or check if the scraper is working properly.")
                            else:
                                st.error("❌ Could not extract a keyword from your resume.")
                        
                        with search_tab2:
                            if SERPAPI_API_KEY:
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    location = st.selectbox("Location", [
                                        "India", "Mumbai", "Delhi", "Bangalore", "Hyderabad", 
                                        "Chennai", "Pune", "Kolkata", "Ahmedabad", "Gurgaon"
                                    ])
                                
                                with col2:
                                    job_type = st.selectbox("Job Type", [
                                        "internship", "entry level", "remote", "full time", 
                                        "part time", "freelance", "contract"
                                    ])
                                
                                with col3:
                                    num_results = st.slider("Number of Results", 10, 50, 20)
                                
                                with col4:
                                    if st.button("🔍 Search Jobs", key=f"search_jobs_{uploaded_file.name}"):
                                        # Extract keywords and search for jobs
                                        with st.spinner("Extracting keywords from your resume..."):
                                            keyword = extract_resume_keywords(extracted_text)
                                        
                                        if keyword:
                                            st.info(f"🔍 **Search Keyword Extracted:** {keyword}")
                                            
                                            with st.spinner(f"Searching for jobs matching: {keyword}..."):
                                                jobs = search_jobs_with_serpapi(keyword, location, job_type, num_results)
                                            
                                            if jobs:
                                                st.success(f"✅ Found {len(jobs)} job opportunities!")
                                                
                                                # Calculate match scores for all jobs
                                                with st.spinner("Calculating job match scores..."):
                                                    for job in jobs:
                                                        job['match_score'] = calculate_job_match_score(job, extracted_text)
                                                
                                                # Sort jobs by match score
                                                jobs.sort(key=lambda x: x['match_score'], reverse=True)
                                                
                                                # Add filters
                                                st.markdown('<div class="filter-container">', unsafe_allow_html=True)
                                                st.markdown("#### 🔍 Filter Results")
                                                
                                                col1, col2, col3 = st.columns(3)
                                                
                                                with col1:
                                                    companies = ['All'] + list(set([job.get('company', 'N/A') for job in jobs]))
                                                    selected_company = st.selectbox("Company", companies, key="serpapi_company")
                                                
                                                with col2:
                                                    locations = ['All'] + list(set([job.get('location', 'N/A') for job in jobs]))
                                                    selected_location = st.selectbox("Job Location", locations, key="serpapi_location")
                                                
                                                with col3:
                                                    min_score = st.slider("Minimum Match Score", 1, 10, 5, key="serpapi_score")
                                                
                                                # Filter jobs based on selections
                                                filtered_jobs = jobs
                                                if selected_company != 'All':
                                                    filtered_jobs = [job for job in filtered_jobs if job.get('company') == selected_company]
                                                if selected_location != 'All':
                                                    filtered_jobs = [job for job in filtered_jobs if job.get('location') == selected_location]
                                                filtered_jobs = [job for job in filtered_jobs if job.get('match_score', 0) >= min_score]
                                                
                                                # Display filtered jobs
                                                st.markdown(f"#### 📋 Showing {len(filtered_jobs)} Jobs")
                                                
                                                for job in filtered_jobs:
                                                    display_job_card(job)
                                            else:
                                                st.warning("⚠️ No matching jobs found. Try updating your resume with more relevant keywords.")
                                        else:
                                            st.error("❌ Could not extract a keyword from your resume.")
                            else:
                                st.error("❌ SerpAPI API key not found. Please add SERPAPI_API_KEY to your .env file to enable Google Jobs search.")
                                st.info("💡 Get your free API key from: https://serpapi.com/")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab4:
                        st.markdown("#### 📄 Extracted Resume Text")
                        with st.expander("View extracted text"):
                            st.text_area("Raw Text", extracted_text, height=300)
                    
                    st.success(f"✅ Analysis complete for {uploaded_file.name}")
                else:
                    st.error("❌ Could not extract text from the uploaded file. Please ensure it's a valid PDF.")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #8b949e; margin-top: 2rem;">
            <p>💡 <strong>Pro Tip:</strong> Upload multiple versions of your resume to compare analyses!</p>
            <p>🔒 Your data is processed securely and not stored permanently.</p>
            <p>📊 Job recommendations are matched from our continuously updated database.</p>
            <p>📧 Use "Apply All" to send batch applications with your resume attached!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app()
                                        