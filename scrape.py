import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import warnings
warnings.filterwarnings('ignore')

class JobScraper:
    def __init__(self, use_selenium=True):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.jobs_data = []
        self.use_selenium = use_selenium
        self.driver = None
        self.target_count = 50  # Target number of jobs to scrape
        
        # Dummy data for replacements
        self.dummy_locations = [
            "Bangalore, Karnataka", "Mumbai, Maharashtra", "Delhi, NCR", 
            "Hyderabad, Telangana", "Pune, Maharashtra", "Chennai, Tamil Nadu",
            "Kolkata, West Bengal", "Ahmedabad, Gujarat", "Noida, Uttar Pradesh",
            "Gurgaon, Haryana", "Jaipur, Rajasthan", "Kochi, Kerala"
        ]
        
        self.dummy_stipends = [
            "₹10,000 - ₹15,000", "₹15,000 - ₹20,000", "₹20,000 - ₹25,000",
            "₹25,000 - ₹30,000", "₹30,000 - ₹35,000", "₹35,000 - ₹40,000",
            "₹8,000 - ₹12,000", "₹12,000 - ₹18,000", "₹18,000 - ₹25,000"
        ]
        
        self.dummy_roles = [
            "Software Developer", "Data Analyst", "Web Developer", 
            "Python Developer", "Full Stack Developer", "Backend Developer",
            "Frontend Developer", "Data Scientist", "Machine Learning Engineer",
            "Software Engineer", "Junior Developer", "Associate Developer"
        ]
        
        if use_selenium:
            self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Selenium WebDriver initialized successfully")
        except Exception as e:
            print(f"Selenium setup failed: {e}")
            print("Falling back to requests-only mode")
            self.use_selenium = False
    
    def generate_email(self, company_name):
        """Generate a dummy email ID based on company name"""
        if not company_name or company_name.lower() in ['n/a', 'na', '']:
            return "careers@company.com"
            
        # Clean company name
        company_clean = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        
        # Common email patterns
        patterns = [
            f"careers@{company_clean}.com",
            f"jobs@{company_clean}.com",
            f"hr@{company_clean}.com",
            f"recruitment@{company_clean}.com",
            f"hiring@{company_clean}.com"
        ]
        
        return random.choice(patterns)
    
    def clean_text(self, text):
        """Clean and normalize text data"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def is_valid_job_data(self, company, role, apply_link):
        """Check if job data is valid (company and apply_link must not be N/A)"""
        invalid_values = ['n/a', 'na', '', 'null', 'none', 'not specified', 'not available']
        
        # Company name must be valid
        if not company or company.lower().strip() in invalid_values:
            return False
        
        # Apply link must be valid
        if not apply_link or apply_link.lower().strip() in invalid_values:
            return False
        
        return True
    
    def fill_dummy_data(self, location, stipend, role, keywords):
        """Fill dummy data for missing fields"""
        # Fill location with dummy data
        if not location or location.lower().strip() in ['n/a', 'na', '', 'null', 'none']:
            location = random.choice(self.dummy_locations)
        
        # Fill stipend with dummy data
        if not stipend or stipend.lower().strip() in ['n/a', 'na', '', 'null', 'none']:
            stipend = random.choice(self.dummy_stipends)
        
        # Fill role with dummy data based on keywords
        if not role or role.lower().strip() in ['n/a', 'na', '', 'null', 'none']:
            # Try to match role with keywords
            keywords_lower = keywords.lower()
            if 'python' in keywords_lower:
                role = "Python Developer"
            elif 'data' in keywords_lower:
                role = "Data Analyst"
            elif 'web' in keywords_lower:
                role = "Web Developer"
            elif 'full' in keywords_lower and 'stack' in keywords_lower:
                role = "Full Stack Developer"
            else:
                role = random.choice(self.dummy_roles)
        
        return location, stipend, role
    
    def scrape_internshala_selenium(self, keywords, max_pages=5):
        """Scrape Internshala using Selenium for dynamic content"""
        print(f"Scraping Internshala with Selenium for keywords: {keywords}")
        
        if not self.use_selenium:
            print("Selenium not available, skipping Internshala")
            return
        
        jobs_found = 0
        
        try:
            for page in range(1, max_pages + 1):
                if jobs_found >= self.target_count // 4:  # Limit per source
                    break
                    
                url = f"https://internshala.com/internships/keywords-{keywords}/page-{page}"
                
                self.driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Wait for internship cards to load
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "internship_meta"))
                    )
                except:
                    print(f"No internship cards found on page {page}")
                    continue
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Find internship cards
                internship_cards = soup.find_all('div', class_='internship_meta')
                print(f"Found {len(internship_cards)} internship cards on page {page}")
                
                for card in internship_cards:
                    if jobs_found >= self.target_count // 4:
                        break
                        
                    try:
                        # Extract company name
                        company_elem = card.find('p', class_='company-name')
                        if not company_elem:
                            company_elem = card.find('a', class_='link_display_like_text')
                        company = self.clean_text(company_elem.text) if company_elem else ""
                        
                        # Extract role
                        role_elem = card.find('h3', class_='heading_4_5')
                        if not role_elem:
                            role_elem = card.find('p', class_='profile')
                        role = self.clean_text(role_elem.text) if role_elem else ""
                        
                        # Extract location
                        location_elem = card.find('p', class_='location-names')
                        if not location_elem:
                            location_elem = card.find('a', {'id': re.compile(r'location_names_')})
                        location = self.clean_text(location_elem.text) if location_elem else ""
                        
                        # Extract stipend
                        stipend_elem = card.find('span', class_='stipend')
                        if not stipend_elem:
                            stipend_elem = card.find('p', class_='stipend')
                        stipend = self.clean_text(stipend_elem.text) if stipend_elem else ""
                        
                        # Extract apply link
                        apply_elem = card.find('a', class_='view_detail_button')
                        if not apply_elem:
                            apply_elem = card.find('a', {'href': re.compile(r'/internship/detail/')})
                        
                        apply_link = ""
                        if apply_elem and apply_elem.get('href'):
                            apply_link = urljoin("https://internshala.com", apply_elem['href'])
                        
                        # Check if valid job data (company and apply_link must not be N/A)
                        if not self.is_valid_job_data(company, role, apply_link):
                            continue
                        
                        # Fill dummy data for missing fields
                        location, stipend, role = self.fill_dummy_data(location, stipend, role, keywords)
                        
                        # Generate email
                        email = self.generate_email(company)
                        
                        self.jobs_data.append({
                            'Company': company,
                            'Role': role,
                            'Location': location,
                            'Stipend (₹/month)': stipend,
                            'Apply Link': apply_link,
                            'EmailID': email
                        })
                        
                        jobs_found += 1
                        
                    except Exception as e:
                        print(f"Error extracting internship data: {e}")
                        continue
                
                print(f"Scraped {jobs_found} valid internships from Internshala so far")
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            print(f"Error scraping Internshala: {e}")
    
    def scrape_naukri_improved(self, keywords, max_pages=5):
        """Improved Naukri scraper with better selectors and validation"""
        print(f"Scraping Naukri for keywords: {keywords}")
        
        session = requests.Session()
        session.headers.update(self.headers)
        
        jobs_found = 0
        
        for page in range(1, max_pages + 1):
            if jobs_found >= self.target_count // 4:  # Limit per source
                break
                
            try:
                # Updated Naukri URL format
                url = f"https://www.naukri.com/{keywords}-jobs?k={keywords}&l=&page={page}"
                
                response = session.get(url)
                if response.status_code != 200:
                    print(f"Failed to fetch page {page} from Naukri (Status: {response.status_code})")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Multiple selectors for job cards
                job_cards = soup.find_all('article', class_='jobTuple') or \
                           soup.find_all('div', class_='jobTuple') or \
                           soup.find_all('div', class_='row') or \
                           soup.find_all('div', {'data-job-id': True})
                
                print(f"Found {len(job_cards)} job cards on page {page}")
                
                for card in job_cards:
                    if jobs_found >= self.target_count // 4:
                        break
                        
                    try:
                        # Extract company name - multiple selectors
                        company_elem = card.find('a', class_='subTitle') or \
                                     card.find('span', class_='companyName') or \
                                     card.find('div', class_='companyName') or \
                                     card.find('a', class_='companyName')
                        company = self.clean_text(company_elem.text) if company_elem else ""
                        
                        # Extract role - multiple selectors
                        role_elem = card.find('a', class_='title') or \
                                   card.find('h3', class_='title') or \
                                   card.find('a', class_='jobTitle') or \
                                   card.find('div', class_='title')
                        role = self.clean_text(role_elem.text) if role_elem else ""
                        
                        # Extract location - multiple selectors
                        location_elem = card.find('span', class_='locationsContainer') or \
                                       card.find('div', class_='location') or \
                                       card.find('span', class_='location')
                        location = self.clean_text(location_elem.text) if location_elem else ""
                        
                        # Extract salary - multiple selectors
                        salary_elem = card.find('span', class_='salary') or \
                                     card.find('div', class_='salary') or \
                                     card.find('span', class_='salaryRange')
                        stipend = self.clean_text(salary_elem.text) if salary_elem else ""
                        
                        # Extract apply link - multiple selectors
                        apply_elem = card.find('a', class_='title') or \
                                    card.find('a', class_='jobTitle') or \
                                    card.find('a', {'href': re.compile(r'/job-listings-')})
                        
                        apply_link = ""
                        if apply_elem and apply_elem.get('href'):
                            href = apply_elem['href']
                            if href.startswith('http'):
                                apply_link = href
                            else:
                                apply_link = urljoin("https://www.naukri.com", href)
                        
                        # Check if valid job data
                        if not self.is_valid_job_data(company, role, apply_link):
                            continue
                        
                        # Fill dummy data for missing fields
                        location, stipend, role = self.fill_dummy_data(location, stipend, role, keywords)
                        
                        # Generate email
                        email = self.generate_email(company)
                        
                        self.jobs_data.append({
                            'Company': company,
                            'Role': role,
                            'Location': location,
                            'Stipend (₹/month)': stipend,
                            'Apply Link': apply_link,
                            'EmailID': email
                        })
                        
                        jobs_found += 1
                        
                    except Exception as e:
                        print(f"Error extracting job data: {e}")
                        continue
                
                print(f"Scraped {jobs_found} valid jobs from Naukri so far")
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Error scraping Naukri page {page}: {e}")
                continue
    
    def scrape_linkedin_jobs(self, keywords, max_results=15):
        """Scrape LinkedIn Jobs with better validation"""
        print(f"Scraping LinkedIn Jobs for keywords: {keywords}")
        
        jobs_found = 0
        
        try:
            # LinkedIn job search URL
            url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location=India&geoId=102713980&f_TPR=r86400&position=1&pageNum=0"
            
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch LinkedIn jobs (Status: {response.status_code})")
                return
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_='base-card') or \
                       soup.find_all('div', class_='job-search-card') or \
                       soup.find_all('li', class_='result-card')
            
            print(f"Found {len(job_cards)} job cards on LinkedIn")
            
            for card in job_cards:
                if jobs_found >= max_results:
                    break
                    
                try:
                    # Extract company name
                    company_elem = card.find('h4', class_='base-search-card__subtitle') or \
                                  card.find('a', class_='hidden-nested-link') or \
                                  card.find('span', class_='job-search-card__subtitle-link')
                    company = self.clean_text(company_elem.text) if company_elem else ""
                    
                    # Extract role
                    role_elem = card.find('h3', class_='base-search-card__title') or \
                               card.find('a', class_='result-card__title-link')
                    role = self.clean_text(role_elem.text) if role_elem else ""
                    
                    # Extract location
                    location_elem = card.find('span', class_='job-search-card__location') or \
                                   card.find('span', class_='job-result-card__location')
                    location = self.clean_text(location_elem.text) if location_elem else ""
                    
                    # Extract apply link
                    apply_elem = card.find('a', class_='base-card__full-link') or \
                                card.find('a', class_='result-card__title-link')
                    
                    apply_link = ""
                    if apply_elem and apply_elem.get('href'):
                        apply_link = apply_elem['href']
                        if not apply_link.startswith('http'):
                            apply_link = urljoin("https://www.linkedin.com", apply_link)
                    
                    # Check if valid job data
                    if not self.is_valid_job_data(company, role, apply_link):
                        continue
                    
                    # LinkedIn doesn't usually show salary in search results
                    stipend = ""
                    
                    # Fill dummy data for missing fields
                    location, stipend, role = self.fill_dummy_data(location, stipend, role, keywords)
                    
                    # Generate email
                    email = self.generate_email(company)
                    
                    self.jobs_data.append({
                        'Company': company,
                        'Role': role,
                        'Location': location,
                        'Stipend (₹/month)': stipend,
                        'Apply Link': apply_link,
                        'EmailID': email
                    })
                    
                    jobs_found += 1
                    
                except Exception as e:
                    print(f"Error extracting LinkedIn job data: {e}")
                    continue
            
            print(f"Scraped {jobs_found} valid jobs from LinkedIn")
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
    
    def scrape_glassdoor_jobs(self, keywords, max_pages=3):
        """Scrape Glassdoor Jobs with better validation"""
        print(f"Scraping Glassdoor for keywords: {keywords}")
        
        session = requests.Session()
        session.headers.update(self.headers)
        
        jobs_found = 0
        
        for page in range(1, max_pages + 1):
            if jobs_found >= self.target_count // 4:  # Limit per source
                break
                
            try:
                url = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={keywords}&locT=N&locId=115&p={page}"
                
                response = session.get(url)
                if response.status_code != 200:
                    print(f"Failed to fetch Glassdoor page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings
                job_cards = soup.find_all('li', class_='react-job-listing') or \
                           soup.find_all('div', class_='jobContainer') or \
                           soup.find_all('article', class_='jobContainer')
                
                print(f"Found {len(job_cards)} job cards on Glassdoor page {page}")
                
                for card in job_cards:
                    if jobs_found >= self.target_count // 4:
                        break
                        
                    try:
                        # Extract company name
                        company_elem = card.find('span', class_='employerName') or \
                                      card.find('div', class_='employerName')
                        company = self.clean_text(company_elem.text) if company_elem else ""
                        
                        # Extract role
                        role_elem = card.find('a', {'data-test': 'job-title'}) or \
                                   card.find('span', class_='jobTitle')
                        role = self.clean_text(role_elem.text) if role_elem else ""
                        
                        # Extract location
                        location_elem = card.find('span', class_='jobLocation') or \
                                       card.find('div', class_='jobLocation')
                        location = self.clean_text(location_elem.text) if location_elem else ""
                        
                        # Extract salary
                        salary_elem = card.find('span', class_='salaryText') or \
                                     card.find('div', class_='salaryEstimate')
                        stipend = self.clean_text(salary_elem.text) if salary_elem else ""
                        
                        # Extract apply link
                        apply_elem = card.find('a', {'data-test': 'job-title'}) or \
                                    card.find('a', class_='jobTitle')
                        
                        apply_link = ""
                        if apply_elem and apply_elem.get('href'):
                            apply_link = urljoin("https://www.glassdoor.co.in", apply_elem['href'])
                        
                        # Check if valid job data
                        if not self.is_valid_job_data(company, role, apply_link):
                            continue
                        
                        # Fill dummy data for missing fields
                        location, stipend, role = self.fill_dummy_data(location, stipend, role, keywords)
                        
                        # Generate email
                        email = self.generate_email(company)
                        
                        self.jobs_data.append({
                            'Company': company,
                            'Role': role,
                            'Location': location,
                            'Stipend (₹/month)': stipend,
                            'Apply Link': apply_link,
                            'EmailID': email
                        })
                        
                        jobs_found += 1
                        
                    except Exception as e:
                        print(f"Error extracting Glassdoor job data: {e}")
                        continue
                
                print(f"Scraped {jobs_found} valid jobs from Glassdoor so far")
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Error scraping Glassdoor page {page}: {e}")
                continue
    
    def remove_duplicates(self):
        """Remove duplicate job entries based on company and role"""
        seen = set()
        unique_jobs = []
        
        for job in self.jobs_data:
            key = (job['Company'].lower(), job['Role'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        original_count = len(self.jobs_data)
        self.jobs_data = unique_jobs
        print(f"Removed {original_count - len(self.jobs_data)} duplicate entries")
    
    def save_to_csv(self, filename=None):
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_internships_{timestamp}.csv"
        
        if not self.jobs_data:
            print("No data to save!")
            return
        
        # Remove duplicates before saving
        self.remove_duplicates()
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Company', 'Role', 'Location', 'Stipend (₹/month)', 'Apply Link', 'EmailID']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for job in self.jobs_data:
                    writer.writerow(job)
            
            print(f"Data saved to {filename}")
            print(f"Total unique jobs/internships found: {len(self.jobs_data)}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def run_scraper(self, keywords, use_all_sources=True):
        """Main function to run the scraper"""
        print(f"Starting enhanced job scraper for keywords: {keywords}")
        print(f"Target: {self.target_count} jobs/internships")
        print("="*60)
        
        # Clear existing data
        self.jobs_data = []
        
        # Scrape different job portals
        if use_all_sources:
            # Scrape Internshala with Selenium
            try:
                self.scrape_internshala_selenium(keywords)
            except Exception as e:
                print(f"Error with Internshala: {e}")
            
            # Scrape Naukri with improved selectors
            try:
                self.scrape_naukri_improved(keywords)
            except Exception as e:
                print(f"Error with Naukri: {e}")
            
            # Scrape LinkedIn Jobs
            try:
                self.scrape_linkedin_jobs(keywords)
            except Exception as e:
                print(f"Error with LinkedIn: {e}")
            
            # Scrape Glassdoor
            try:
                self.scrape_glassdoor_jobs(keywords)
            except Exception as e:
                print(f"Error with Glassdoor: {e}")
        else:
            # Just scrape the most reliable sources
            try:
                self.scrape_naukri_improved(keywords)
            except Exception as e:
                print(f"Error with Naukri: {e}")
            
            try:
                self.scrape_linkedin_jobs(keywords)
            except Exception as e:
                print(f"Error with LinkedIn: {e}")
        
        # Save to CSV
        self.save_to_csv()
        
        # Cleanup
        if self.driver:
            self.driver.quit()
        
        return self.jobs_data
    
    def __del__(self):
        """Cleanup WebDriver"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass

# Example usage
def main():
    print("Enhanced Job & Internship Scraper")
    print("=" * 40)
    
    # Get user input
    keywords = input("Enter keywords to search for (e.g., 'python', 'data science', 'web development'): ").strip()
    
    if not keywords:
        keywords = "python"  # Default keyword
    
    # Ask if user wants to use all sources or just reliable ones
    use_all = input("Use all job sources? (y/n, default=y): ").strip().lower()
    use_all_sources = use_all != 'n'
    
    # Ask if user wants to use Selenium
    use_selenium_input = input("Use Selenium for better scraping? (y/n, default=y): ").strip().lower()
    use_selenium = use_selenium_input != 'n'
    
    print(f"\nSearching for ~50 jobs/internships with keywords: {keywords}")
    print(f"Using all sources: {use_all_sources}")
    print(f"Using Selenium: {use_selenium}")
    
    # Create scraper instance
    scraper = JobScraper(use_selenium=use_selenium)
    
    # Run the scraper
    jobs_data = scraper.run_scraper(keywords, use_all_sources=use_all_sources)
    
    # Display summary
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    print(f"Total jobs/internships found: {len(jobs_data)}")
    
    if jobs_data:
        print(f"\nFirst 5 results:")
        for i, job in enumerate(jobs_data[:5]):
            print(f"\n{i+1}. {job['Company']} - {job['Role']}")
            print(f"   Location: {job['Location']}")
            print(f"   Stipend: {job['Stipend (₹/month)']}")
            print(f"   Apply Link: {job['Apply Link']}")
            print(f"   Email: {job['EmailID']}")
    
    print(f"\nData saved to CSV file!")

if __name__ == "__main__":
    main()