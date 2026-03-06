"""
HTML Parser Module
Parses HTML content from Japanese company and job websites
"""

import re
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CompanyParser:
    """Parser for Japanese company information"""
    
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        """Parse company information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Determine site type and parse accordingly
        domain = urlparse(url).netloc
        
        if 'wantedly' in domain:
            return self._parse_wantedly(soup, url)
        elif 'green-japan' in domain:
            return self._parse_green_japan(soup, url)
        elif 'openwork' in domain:
            return self._parse_openwork(soup, url)
        elif 'indeed' in domain:
            return self._parse_indeed(soup, url)
        else:
            return self._parse_generic_company(soup, url)
    
    def _parse_wantedly(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse Wantedly company page"""
        data = {'source': 'wantedly', 'source_url': url}
        
        # Company name
        name_elem = soup.find('h1') or soup.find(class_=re.compile(r'company.?name'))
        if name_elem:
            data['name'] = name_elem.get_text(strip=True)
        
        # Business description
        desc_elem = soup.find(class_=re.compile(r'description|business'))
        if desc_elem:
            data['business'] = desc_elem.get_text(strip=True)[:500]
        
        return data
    
    def _parse_green_japan(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse Green Japan company page"""
        data = {'source': 'green-japan', 'source_url': url}
        
        name_elem = soup.find('h1') or soup.find(class_=re.compile(r'company.?name'))
        if name_elem:
            data['name'] = name_elem.get_text(strip=True)
        
        return data
    
    def _parse_openwork(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse OpenWork company page"""
        data = {'source': 'openwork', 'source_url': url}
        
        name_elem = soup.find('h1') or soup.find(class_=re.compile(r'company.?name'))
        if name_elem:
            data['name'] = name_elem.get_text(strip=True)
        
        return data
    
    def _parse_indeed(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse Indeed job/company page"""
        data = {'source': 'indeed', 'source_url': url}
        
        title_elem = soup.find('h1') or soup.find(class_=re.compile(r'job.?title'))
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        return data
    
    def _parse_generic_company(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse generic company page"""
        data = {'source': 'generic', 'source_url': url}
        text = soup.get_text()
        
        # Company name
        name_elem = soup.find('h1') or soup.find('title')
        if name_elem:
            data['name'] = name_elem.get_text(strip=True)
        
        # Extract established year
        founded_match = re.search(r'設立[年:：]\s*(\d{4})', text)
        if founded_match:
            data['founded'] = int(founded_match.group(1))
        
        # Extract capital
        capital_match = re.search(r'資本[金:：]\s*([\d,]+)\s*万円?', text)
        if capital_match:
            data['capital'] = capital_match.group(1) + '万円'
        
        # Extract employees
        emp_match = re.search(r'従業員?[数:：]\s*([\d,]+)', text)
        if emp_match:
            data['employees'] = emp_match.group(1) + '人'
        
        # Extract headquarter
        hq_match = re.search(r'本社[所在地:：]\s*(.+?)(?:\n|$)', text)
        if hq_match:
            data['headquarter'] = hq_match.group(1).strip()[:200]
        
        return data


class JobParser:
    """Parser for Japanese job listings"""
    
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        """Parse job information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        domain = urlparse(url).netloc
        
        data = {
            'source_url': url,
            'source_name': domain,
            'title': None,
            'company': None,
            'salary': None,
            'salary_min': None,
            'salary_max': None,
            'benefits': None,
            'vacation_days': None,
            'remote': 'unknown',
            'tech_stack': [],
            'description': None,
            'requirements': None,
            'job_type': 'fulltime',
        }
        
        # Extract based on source
        if 'wantedly' in domain:
            data.update(self._parse_wantedly_job(soup, url))
        elif 'green-japan' in domain:
            data.update(self._parse_green_japan_job(soup, url))
        elif 'indeed' in domain:
            data.update(self._parse_indeed_job(soup, url))
        elif 'doda' in domain:
            data.update(self._parse_doda_job(soup, url))
        else:
            data.update(self._parse_generic_job(soup, url))
        
        return data
    
    def _parse_wantedly_job(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse Wantedly job listing"""
        data = {}
        
        title_elem = soup.find('h1') or soup.find(class_=re.compile(r'job.?title'))
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        # Extract salary
        salary_elem = soup.find(class_=re.compile(r'salary|給与'))
        if salary_elem:
            salary_text = salary_elem.get_text(strip=True)
            data['salary'] = salary_text
            data.update(self._parse_salary(salary_text))
        
        # Extract tech stack
        tech_section = soup.find_all(class_=re.compile(r'tech|技術'))
        tech_stack = []
        for section in tech_section:
            tech_stack.extend(section.get_text(strip=True).split(','))
        data['tech_stack'] = [t.strip() for t in tech_stack if t.strip()]
        
        return data
    
    def _parse_green_japan_job(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse Green Japan job listing"""
        data = {}
        
        title_elem = soup.find('h1') or soup.find(class_=re.compile(r'job.?title'))
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        return data
    
    def _parse_indeed_job(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse Indeed job listing"""
        data = {}
        
        title_elem = soup.find('h1') or soup.find(class_=re.compile(r'job.?title'))
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        salary_elem = soup.find(class_=re.compile(r'salary'))
        if salary_elem:
            salary_text = salary_elem.get_text(strip=True)
            data['salary'] = salary_text
            data.update(self._parse_salary(salary_text))
        
        return data
    
    def _parse_doda_job(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse Doda job listing"""
        data = {}
        
        title_elem = soup.find('h1') or soup.find(class_=re.compile(r'job.?title'))
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        return data
    
    def _parse_generic_job(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse generic job listing"""
        data = {}
        text = soup.get_text()
        
        # Job title
        title_elem = soup.find('h1')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        # Salary
        salary_match = re.search(r'給与[：:]\s*(.+?)(?:\n|,|$)', text)
        if salary_match:
            salary_text = salary_match.group(1).strip()
            data['salary'] = salary_text
            data.update(self._parse_salary(salary_text))
        
        # Benefits
        benefits_match = re.search(r'福利厚生[：:]\s*(.+?)(?:\n|$)', text)
        if benefits_match:
            data['benefits'] = benefits_match.group(1).strip()[:500]
        
        # Vacation
        vacation_match = re.search(r'休日[・:]+\s*(.+?)(?:\n|$)', text)
        if vacation_match:
            data['vacation_days'] = vacation_match.group(1).strip()
        
        # Remote work
        if '完全リモート' in text:
            data['remote'] = 'full_remote'
        elif 'リモート' in text or 'remote' in text.lower():
            if 'ハイブリッド' in text:
                data['remote'] = 'hybrid'
            else:
                data['remote'] = 'hybrid'
        
        # Job type
        if 'intern' in text.lower() or 'インター' in text:
            data['job_type'] = 'intern'
        elif '契約' in text or 'contract' in text.lower():
            data['job_type'] = 'contract'
        elif 'パート' in text or 'part' in text.lower():
            data['job_type'] = 'parttime'
        
        # Tech stack
        tech_keywords = [
            'Python', 'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
            'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'Go', 'Rust', 'Java',
            'Ruby', 'PHP', 'Swift', 'Kotlin', 'C++', 'C#', 'SQL', 'NoSQL',
            'PyTorch', 'TensorFlow', 'Keras', 'Scikit-learn', 'LangChain',
            'LLM', 'GPT', 'OpenAI', 'Hugging Face', 'Machine Learning', 
            'Deep Learning', 'NLP', 'AI', 'Generative AI',
           ', 'Computer Vision 'Pinecone', 'Weaviate', 'Vector DB', 'Redis', 'Elasticsearch',
        ]
        
        tech_stack = [tech for tech in tech_keywords if tech in text]
        data['tech_stack'] = tech_stack
        
        # Description
        desc_elem = soup.find('div', class_=re.compile(r'description|content|detail'))
        if desc_elem:
            data['description'] = desc_elem.get_text(strip=True)[:2000]
        
        return data
    
    def _parse_salary(self, salary_text: str) -> Dict[str, Any]:
        """Parse salary text to extract min/max values"""
        result = {'salary_min': None, 'salary_max': None}
        
        # Match patterns like "400万円〜600万円" or "400,000円〜600,000円"
        match = re.search(r'([\d,]+)\s*[万円円]', salary_text)
        if match:
            try:
                value = int(match.group(1).replace(',', ''))
                # Determine if it's in 万円 or 千円
                if '万円' in salary_text:
                    result['salary_min'] = value * 10000
                    result['salary_max'] = value * 10000
                else:  # 千円
                    result['salary_min'] = value * 1000
                    result['salary_max'] = value * 1000
            except ValueError:
                pass
        
        # Try to find range
        range_match = re.search(r'([\d,]+)\s*[万円円]\s*〜\s*([\d,]+)\s*[万円円]', salary_text)
        if range_match:
            try:
                min_val = int(range_match.group(1).replace(',', ''))
                max_val = int(range_match.group(2).replace(',', ''))
                
                if '万円' in salary_text:
                    result['salary_min'] = min_val * 10000
                    result['salary_max'] = max_val * 10000
                else:
                    result['salary_min'] = min_val * 1000
                    result['salary_max'] = max_val * 1000
            except ValueError:
                pass
        
        return result


def parse_company(html: str, url: str) -> Dict[str, Any]:
    """Convenience function to parse company info"""
    parser = CompanyParser()
    return parser.parse(html, url)


def parse_job(html: str, url: str) -> Dict[str, Any]:
    """Convenience function to parse job info"""
    parser = JobParser()
    return parser.parse(html, url)
