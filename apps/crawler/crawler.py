"""
Company Crawler Module
Crawls Japanese company websites and recruitment sites
"""

import asyncio
import re
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings

logger = logging.getLogger(__name__)


class CompanyCrawler:
    """Crawler for Japanese company information"""
    
    # Japanese recruitment sites
    JOB_SITES = [
        'wantedly.com',
        'green-japan.com', 
        'openwork.jp',
        'linkedin.com',
        'indeed.co.jp',
        'doda.jp',
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        })
        self.timeout = getattr(settings, 'CRAWLER_TIMEOUT', 30)
    
    def search_company(self, company_name: str) -> Dict[str, Any]:
        """Search for company information"""
        results = {
            'company_info': {},
            'jobs': [],
            'job_urls': [],
        }
        
        # Search for company website
        company_info = self._search_company_website(company_name)
        results['company_info'] = company_info
        
        # Search for jobs
        if company_info.get('domain'):
            job_urls = self._search_job_listings(company_name, company_info['domain'])
            results['job_urls'] = job_urls
        
        return results
    
    def _search_company_website(self, company_name: str) -> Dict[str, Any]:
        """Search for company website using search engine"""
        company_info = {
            'name': company_name,
            'domain': None,
            'business': None,
            'founded': None,
            'capital': None,
            'employees': None,
            'headquarter': None,
            'description': None,
        }
        
        # Use DuckDuckGo or Google to search for the company
        search_queries = [
            f"{company_name} 会社概要",
            f"{company_name} 企業情報",
            f"{company_name} About Company",
            f"{company_name} 採用情報",
        ]
        
        for query in search_queries:
            try:
                # Simple search simulation - in production, use search API
                domain = self._guess_company_domain(company_name)
                if domain:
                    company_info['domain'] = domain
                    # Try to get company info from their website
                    info = self._crawl_company_page(domain)
                    if info:
                        company_info.update(info)
                    break
            except Exception as e:
                logger.error(f"Error searching for {company_name}: {e}")
                continue
        
        return company_info
    
    def _guess_company_domain(self, company_name: str) -> Optional[str]:
        """Guess company domain from name"""
        # Common Japanese company domain patterns
        name_lower = company_name.lower().replace(' ', '')
        
        # Known domains for major companies
        known_domains = {
            'preferred networks': 'preferred.jp',
            'mercari': 'mercari.com',
            'rakuten': 'rakuten.co.jp',
            'cyberagent': 'cyberagent.co.jp',
            'line': 'linecorp.com',
            'google': 'google.com',
            'amazon': 'amazon.co.jp',
            'microsoft': 'microsoft.com',
            'apple': 'apple.com',
        }
        
        for key, domain in known_domains.items():
            if key in name_lower:
                return domain
        
        # Default pattern
        return f"{name_lower}.co.jp"
    
    def _crawl_company_page(self, domain: str) -> Dict[str, Any]:
        """Crawl company information page"""
        info = {}
        
        # Try common paths for company info
        paths = ['/company', '/about', '/概要', '/企業情報', '/会社概要']
        
        for path in paths:
            url = f"https://{domain}{path}"
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    info = self._parse_company_info(soup, url)
                    if info:
                        break
            except Exception as e:
                logger.debug(f"Failed to crawl {url}: {e}")
                continue
        
        return info
    
    def _parse_company_info(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse company information from HTML"""
        info = {}
        
        # Extract text content
        text = soup.get_text()
        
        # Extract founded year
        founded_match = re.search(r'設立[年:：]\s*(\d{4})', text)
        if founded_match:
            info['founded'] = int(founded_match.group(1))
        
        # Extract capital
        capital_match = re.search(r'資本[金:：]\s*([\d,]+)\s*万円?', text)
        if capital_match:
            info['capital'] = capital_match.group(1) + '万円'
        
        # Extract employees
        employee_match = re.search(r'従業員?[数:：]\s*([\d,]+)', text)
        if employee_match:
            info['employees'] = employee_match.group(1) + '人'
        
        # Extract headquarter
        hq_match = re.search(r'本社[所在地:：]\s*(.+?)(?:\n|$)', text)
        if hq_match:
            info['headquarter'] = hq_match.group(1).strip()
        
        return info
    
    def _search_job_listings(self, company_name: str, domain: str) -> List[str]:
        """Search for job listing URLs"""
        job_urls = []
        
        # In production, this would search each job site
        # For now, return placeholder URLs
        
        return job_urls
    
    def crawl_job_page(self, url: str) -> Dict[str, Any]:
        """Crawl a job listing page"""
        job_data = {
            'title': None,
            'company': None,
            'salary': None,
            'benefits': None,
            'vacation_days': None,
            'remote': 'unknown',
            'tech_stack': [],
            'description': None,
            'requirements': None,
            'source_url': url,
        }
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_data = self._parse_job_page(soup, url)
        except Exception as e:
            logger.error(f"Failed to crawl job page {url}: {e}")
        
        return job_data
    
    def _parse_job_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse job listing page"""
        job_data = {}
        text = soup.get_text()
        
        # Extract job title
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            job_data['title'] = title_tag.get_text(strip=True)
        
        # Extract salary
        salary_match = re.search(r'給与[：:]\s*(.+?)(?:\n|,|$)', text)
        if salary_match:
            job_data['salary'] = salary_match.group(1).strip()
        
        # Extract benefits
        benefits_match = re.search(r'福利厚生[：:]\s*(.+?)(?:\n|$)', text)
        if benefits_match:
            job_data['benefits'] = benefits_match.group(1).strip()
        
        # Extract vacation
        vacation_match = re.search(r'休日[・:]+\s*(.+?)(?:\n|$)', text)
        if vacation_match:
            job_data['vacation_days'] = vacation_match.group(1).strip()
        
        # Extract remote work info
        if 'リモート' in text or 'remote' in text.lower():
            if '完全リモート' in text:
                job_data['remote'] = 'full_remote'
            elif 'ハイブリッド' in text:
                job_data['remote'] = 'hybrid'
            else:
                job_data['remote'] = 'onsite'
        
        # Extract tech stack
        tech_keywords = ['Python', 'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
                        'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'Go', 'Rust',
                        'PyTorch', 'TensorFlow', 'Keras', 'Scikit-learn', 'LangChain',
                        'LLM', 'GPT', 'OpenAI', 'Machine Learning', 'Deep Learning']
        
        tech_stack = [tech for tech in tech_keywords if tech in text]
        job_data['tech_stack'] = tech_stack
        
        # Extract description
        desc_tag = soup.find('div', class_=re.compile(r'description|content|job-detail'))
        if desc_tag:
            job_data['description'] = desc_tag.get_text(strip=True)[:2000]
        
        job_data['source_url'] = url
        job_data['source_name'] = urlparse(url).netloc
        
        return job_data


def search_company(company_name: str) -> Dict[str, Any]:
    """Convenience function to search for company"""
    crawler = CompanyCrawler()
    return crawler.search_company(company_name)


def crawl_job(url: str) -> Dict[str, Any]:
    """Convenience function to crawl a job page"""
    crawler = CompanyCrawler()
    return crawler.crawl_job_page(url)
