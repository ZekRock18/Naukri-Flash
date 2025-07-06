# 🚀 Naukri Flash - AI Job Application Agent

**Automated Job Application Agent** that auto-fills job applications, customizes resumes, and tracks submissions using AI-powered analysis.

## 🎯 Team Information

**Team Name:** Hackstreet Boys

**Team Members:**
- Prakhar Gupta
- Praver Agarwal
- Aashi Tiwari
- Priyansh Bhatia

**Project Theme:** Automated Job Application Agent

## 🎯 Overview

Naukri Flash is an intelligent job application automation tool that helps job seekers, students, and professionals streamline their job hunting process. The system uses AI to analyze resumes, match candidates with relevant job opportunities, and automate the application process.

### 🔥 Key Features

- **📄 Smart Resume Analysis**: AI-powered resume parsing and professional insights
- **🎯 ATS Score Calculation**: Comprehensive ATS compatibility scoring with detailed feedback
- **🔍 Intelligent Job Matching**: Automated job search using resume keywords
- **📧 Bulk Application System**: Apply to multiple jobs with one click
- **📊 Real-time Job Scraping**: Live job data from multiple sources
- **🤖 AI-Powered Insights**: Career recommendations and skill gap analysis
- **📈 Professional Dashboard**: Modern dark-themed UI with interactive features

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit with Custom CSS |
| **Backend** | Python 3.8+ |
| **AI/ML** | Groq API (LLaMA), Google Jobs API |
| **Resume Analysis** | pypdf, spaCy, python-docx |
| **Web Scraping** | Selenium, Playwright |
| **Data Processing** | Pandas, NumPy |
| **Email Automation** | SMTP, MIMEMultipart |
| **Search APIs** | SerpAPI, Google Search |

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome/Chromium browser (for web scraping)
- Gmail account (for email automation)
- API Keys for:
  - Groq API
  - SerpAPI

## 📖 Usage

### 1. Resume Analysis
- Upload PDF resume(s) via the web interface
- Get comprehensive AI analysis including:
  - Skill assessment
  - Industry recommendations
  - ATS compatibility score
  - Improvement suggestions

### 2. Job Matching
- System extracts keywords from your resume
- Searches for relevant job opportunities
- Filters results by company, location, and role
- Calculates match scores for each position

### 3. Bulk Applications
- Select multiple job positions
- Click "Apply to All" to send applications
- System emails your resume with job details
- Tracks all applications automatically

### 4. Advanced Features
- **Filter Options**: Company, location, salary range
- **Match Scoring**: AI-calculated compatibility scores
- **Real-time Updates**: Fresh job listings every search
- **Professional Reports**: Detailed analysis exports

## 🎨 Features in Detail

### Resume Analysis Engine
```python
# AI-powered resume insights
- Comprehensive skill assessment
- Industry-specific recommendations
- Career progression suggestions
- Market competitiveness analysis
- ATS optimization tips
```

### Job Matching Algorithm
```python
# Intelligent job matching
- Keyword extraction from resume
- Semantic similarity matching
- Real-time job data scraping
- Custom scoring algorithm
- Multi-source job aggregation
```

### Email Automation System
```python
# Automated application emails
- Resume attachment handling
- Professional email templates
- Batch application processing
- Application tracking
- CSV export functionality
```

## 📊 Project Structure

```
naukri-flash/
├── app.py                  # Main Streamlit application
├── scrape.py              # Web scraping modules
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── README.md             # Project documentation
```

## 🔍 Core Modules

### 1. Resume Parser
- **Function**: `extract_text_from_pdf()`
- **Purpose**: Extract and clean text from PDF resumes
- **Features**: Multi-page support, error handling

### 2. AI Analysis Engine
- **Function**: `analyze_resume()`
- **Purpose**: Generate professional insights
- **Features**: Skill assessment, career recommendations

### 3. ATS Scorer
- **Function**: `calculate_ats_score()`
- **Purpose**: Evaluate resume ATS compatibility
- **Features**: Detailed breakdown, improvement tips

### 4. Job Search Engine
- **Function**: `search_jobs_with_serpapi()`
- **Purpose**: Find relevant job opportunities
- **Features**: Multi-source search, real-time data

### 5. Email Automation
- **Function**: `send_application_email()`
- **Purpose**: Automate job applications
- **Features**: Batch processing, attachment handling

<div align="center">
  <p><strong>Made with ❤️ by Hackstreet Boys</strong></p>
  <p>🚀 <em>Making job hunting smarter, faster, and more efficient!</em></p>
</div>
