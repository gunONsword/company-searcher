"""
Search Service Module
Main search logic for company and job search
"""

import logging
from typing import Dict, List, Any, Optional

from apps.company.models import Company
from apps.job.models import Job, AIJob
from apps.crawler.crawler import search_company, crawl_job
from apps.analyzer.analyzer import analyze_job, analyze_company, get_ai_type_name

logger = logging.getLogger(__name__)


class SearchService:
    """Main search service for company information"""
    
    def __init__(self):
        self.language = 'zh'  # Default to Chinese
    
    def search_company(self, company_name: str, language: str = 'zh') -> Dict[str, Any]:
        """Search for company and return full report"""
        self.language = language
        
        result = {
            'company_info': {},
            'jobs': [],
            'ai_jobs': [],
            'analysis': {},
            'language': language,
        }
        
        # Step 1: Crawl company information
        crawler_result = search_company(company_name)
        
        # Step 2: Save or update company in database
        company_info = crawler_result.get('company_info', {})
        company = self._save_company(company_info)
        
        # Step 3: Crawl job listings (simulated for now)
        job_urls = crawler_result.get('job_urls', [])
        
        # For demo, create sample jobs
        jobs = self._create_sample_jobs(company)
        
        # Step 4: Analyze jobs for AI relevance
        ai_jobs = []
        for job in jobs:
            is_ai, ai_type, ai_tech = analyze_job(job.to_dict())
            if is_ai:
                ai_job = AIJob.objects.create(
                    job=job,
                    ai_type=ai_type,
                    ai_tech_stack=ai_tech
                )
                ai_jobs.append({
                    'job': job.to_dict(),
                    'ai_type': get_ai_type_name(ai_type, language),
                    'ai_tech_stack': ai_tech,
                })
        
        # Step 5: Generate company analysis
        analysis = analyze_company(
            company.to_dict(),
            [j.to_dict() for j in jobs]
        )
        
        # Convert analysis to local language
        analysis['ai_job_types_localized'] = {
            get_ai_type_name(k, language): v 
            for k, v in analysis.get('ai_job_types', {}).items()
        }
        
        result['company_info'] = company.to_dict()
        result['jobs'] = [j.to_dict() for j in jobs]
        result['ai_jobs'] = ai_jobs
        result['analysis'] = analysis
        
        return result
    
    def _save_company(self, company_info: Dict[str, Any]) -> Company:
        """Save or update company in database"""
        name = company_info.get('name', 'Unknown')
        
        company, created = Company.objects.update_or_create(
            name=name,
            defaults={
                'domain': company_info.get('domain'),
                'business': company_info.get('business'),
                'founded': company_info.get('founded'),
                'capital': company_info.get('capital'),
                'employees': company_info.get('employees'),
                'headquarter': company_info.get('headquarter'),
            }
        )
        
        logger.info(f"{'Created' if created else 'Updated'} company: {company.name}")
        return company
    
    def _create_sample_jobs(self, company: Company) -> List[Job]:
        """Create sample jobs for demonstration"""
        # For demo purposes, create sample AI jobs
        sample_jobs = [
            {
                'title': 'Machine Learning Engineer',
                'job_type': 'fulltime',
                'salary': '600万円〜1200万円',
                'salary_min': 6000000,
                'salary_max': 12000000,
                'benefits': 'ストックオプション, 書籍購入補助, カンファレンス参加支援',
                'vacation_days': '125日',
                'remote': 'hybrid',
                'tech_stack': ['Python', 'PyTorch', 'TensorFlow', 'AWS'],
                'description': '機械学習モデルの設計・実装業務。大規模言語モデルに関する研究也将承',
                'requirements': '3年以上のML開発経験',
                'source_name': 'sample',
                'source_url': 'https://example.com/job/1',
            },
            {
                'title': 'LLM Engineer',
                'job_type': 'fulltime',
                'salary': '800万円〜1500万円',
                'salary_min': 8000000,
                'salary_max': 15000000,
                'benefits': 'RSU, 完全リモート可, 技術カンファレンス参加',
                'vacation_days': '130日',
                'remote': 'full_remote',
                'tech_stack': ['Python', 'LangChain', 'HuggingFace', 'OpenAI API', 'Docker'],
                'description': 'LLMアプリケーションの開発、プロンプトエンジニアリング、RAG実装',
                'requirements': 'LLM経験2年以上',
                'source_name': 'sample',
                'source_url': 'https://example.com/job/2',
            },
            {
                'title': 'Data Scientist',
                'job_type': 'fulltime',
                'salary': '550万円〜1000万円',
                'salary_min': 5500000,
                'salary_max': 10000000,
                'benefits': '賞与年2回, 資格取得補助',
                'vacation_days': '120日',
                'remote': 'onsite',
                'tech_stack': ['Python', 'SQL', 'Pandas', 'Scikit-learn', 'Tableau'],
                'description': 'データ分析・可視化、BIダッシュボード構築',
                'requirements': 'データ分析経験1年以上',
                'source_name': 'sample',
                'source_url': 'https://example.com/job/3',
            },
        ]
        
        jobs = []
        for job_data in sample_jobs:
            job, created = Job.objects.get_or_create(
                company=company,
                title=job_data['title'],
                source_url=job_data['source_url'],
                defaults=job_data
            )
            if created:
                # Check if it's AI related
                is_ai, ai_type, ai_tech = analyze_job(job.to_dict())
                job.is_ai_related = is_ai
                job.save()
                
                if is_ai:
                    AIJob.objects.create(
                        job=job,
                        ai_type=ai_type,
                        ai_tech_stack=ai_tech
                    )
            
            jobs.append(job)
        
        return jobs
    
    def get_company_report(self, company_id: int, language: str = 'zh') -> Optional[Dict[str, Any]]:
        """Get company report by ID"""
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None
        
        self.language = language
        
        jobs = Job.objects.filter(company=company)
        ai_jobs_data = AIJob.objects.filter(job__company=company).select_related('job')
        
        ai_jobs = []
        for ai_job in ai_jobs_data:
            ai_jobs.append({
                'job': ai_job.job.to_dict(),
                'ai_type': get_ai_type_name(ai_job.ai_type, language),
                'ai_tech_stack': ai_job.ai_tech_stack,
            })
        
        analysis = analyze_company(
            company.to_dict(),
            [j.to_dict() for j in jobs]
        )
        
        analysis['ai_job_types_localized'] = {
            get_ai_type_name(k, language): v 
            for k, v in analysis.get('ai_job_types', {}).items()
        }
        
        return {
            'company_info': company.to_dict(),
            'jobs': [j.to_dict() for j in jobs],
            'ai_jobs': ai_jobs,
            'analysis': analysis,
            'language': language,
        }


def search_company_service(company_name: str, language: str = 'zh') -> Dict[str, Any]:
    """Convenience function to search company"""
    service = SearchService()
    return service.search_company(company_name, language)


def get_company_report_service(company_id: int, language: str = 'zh') -> Optional[Dict[str, Any]]:
    """Convenience function to get company report"""
    service = SearchService()
    return service.get_company_report(company_id, language)
