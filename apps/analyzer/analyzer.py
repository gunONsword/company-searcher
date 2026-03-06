"""
AI Job Analyzer Module
Analyzes job listings to identify AI-related positions
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


# AI Job Type Keywords Mapping
AI_JOB_KEYWORDS = {
    'llm_engineer': [
        'llm', 'large language model', 'language model',
        'gpt', 'chatgpt', 'claude', 'gemini',
        'transformer', 'decoder', 'llama', 'mistral',
        'text generation', 'prompt engineering',
    ],
    'ml_engineer': [
        'machine learning', 'ml engineer', 'ml',
        'データサイエンティスト', 'machine learning engineer',
        'mlops', 'ml ops',
    ],
    'dl_engineer': [
        'deep learning', '深層学習', 'dl engineer',
        'neural network', 'ニューラルネットワーク',
    ],
    'ai_agent_engineer': [
        'ai agent', 'ai エージェント', 'agent',
        'autonomous', 'autonomous agent', 'gpt agent',
        'langchain', 'autogen', 'crewai',
    ],
    'data_scientist': [
        'data scientist', 'データサイエンティスト',
        'data analysis', 'データ分析', 'データアナリスト',
        'bi', 'business intelligence',
    ],
    'cv_engineer': [
        'computer vision', '画像認識', 'cv engineer',
        'image recognition', 'object detection', 'yolo',
        'cnn', 'vision transformer', 'vit',
        'ocr', 'face recognition', '物体検出',
    ],
    'nlp_engineer': [
        'nlp', 'natural language processing', '自然言語処理',
        'text mining', 'テキストマイニング', 'sentiment',
        'named entity', 'ner', 'word embedding',
    ],
    'ai_researcher': [
        'ai researcher', 'ai 研究者', 'researcher',
        'research engineer', '研究', 'algorithm',
        'paper', 'arxiv', 'academic',
    ],
    'generative_ai': [
        'generative ai', '生成ai', 'gen ai',
        'stable diffusion', 'midjourney', '画像生成',
        'text to image', 'diffusion', 'gans',
        'audio generation', 'video generation',
    ],
}

# Tech stack keywords
AI_TECH_STACK = {
    'pytorch': ['pytorch', 'py torch'],
    'tensorflow': ['tensorflow', 'tf'],
    'keras': ['keras'],
    'langchain': ['langchain', 'lang chain'],
    'huggingface': ['huggingface', 'hugging face', 'transformers'],
    'openai': ['openai', 'gpt-', 'chatgpt', 'api openai'],
    'anthropic': ['anthropic', 'claude'],
    'googleai': ['google ai', 'gemini', 'palm', 'bard'],
    'aws': ['aws', 'amazon web services', 'sagemaker', 'bedrock'],
    'azure': ['azure', 'azure ai', 'azure openai'],
    'gcp': ['gcp', 'google cloud', 'vertex ai', 'palm api'],
    'pinecone': ['pinecone'],
    'weaviate': ['weaviate'],
    'milvus': ['milvus'],
    'qdrant': ['qdrant'],
    'redis': ['redis'],
    'postgres': ['postgresql', 'postgres'],
    'mongodb': ['mongodb'],
    'docker': ['docker', 'container'],
    'kubernetes': ['kubernetes', 'k8s', 'eks', 'gke'],
    'mlflow': ['mlflow'],
    'kubeflow': ['kubeflow'],
    'optuna': ['optuna'],
    'scikit': ['scikit-learn', 'sklearn'],
    'pandas': ['pandas'],
    'numpy': ['numpy'],
    'scipy': ['scipy'],
    'opencv': ['opencv'],
    'pillow': ['pillow', 'pil'],
    'scikit-image': ['scikit-image'],
}


class AIJobAnalyzer:
    """Analyzer for AI-related job positions"""
    
    def __init__(self):
        self.ai_job_keywords = AI_JOB_KEYWORDS
        self.ai_tech_stack = AI_TECH_STACK
    
    def analyze_job(self, job_data: Dict[str, Any]) -> Tuple[bool, Optional[str], List[str]]:
        """
        Analyze if a job is AI-related
        
        Returns: (is_ai_related, ai_type, ai_tech_stack)
        """
        title = (job_data.get('title') or '').lower()
        description = (job_data.get('description') or '').lower()
        tech_stack = job_data.get('tech_stack', [])
        
        # Combine all text for analysis
        full_text = f"{title} {description} {' '.join(tech_stack)}"
        
        # Check for AI job type
        ai_type = None
        for job_type, keywords in self.ai_job_keywords.items():
            for keyword in keywords:
                if keyword.lower() in full_text:
                    ai_type = job_type
                    break
            if ai_type:
                break
        
        if not ai_type:
            # Also check for general AI keywords
            general_ai_keywords = ['ai', 'artificial intelligence', '人工智能', '人工智能']
            if any(kw in full_text for kw in general_ai_keywords):
                ai_type = 'ml_engineer'  # Default to ML engineer
        
        if not ai_type:
            return False, None, []
        
        # Extract AI tech stack
        ai_tech = self._extract_ai_tech_stack(full_text)
        
        return True, ai_type, ai_tech
    
    def _extract_ai_tech_stack(self, text: str) -> List[str]:
        """Extract AI-related tech stack from text"""
        found_tech = []
        text_lower = text.lower()
        
        for tech, keywords in self.ai_tech_stack.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_tech.append(tech)
                    break
        
        return list(set(found_tech))
    
    def analyze_company(self, company_data: Dict[str, Any], jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze company's AI job status
        
        Returns: {
            'total_jobs': int,
            'ai_jobs': int,
            'ai_job_types': dict,
            'ai_tech_stack': list,
            'ai_score': float,
            'salary_stats': dict,
        }
        """
        total_jobs = len(jobs)
        ai_jobs = []
        
        for job in jobs:
            is_ai, ai_type, ai_tech = self.analyze_job(job)
            if is_ai:
                ai_jobs.append({
                    'job': job,
                    'ai_type': ai_type,
                    'ai_tech_stack': ai_tech,
                })
        
        # Count AI job types
        ai_job_types = {}
        all_ai_tech = set()
        
        for ai_job in ai_jobs:
            job_type = ai_job['ai_type']
            ai_job_types[job_type] = ai_job_types.get(job_type, 0) + 1
            all_ai_tech.update(ai_job['ai_tech_stack'])
        
        # Calculate AI score
        ai_score = self._calculate_ai_score(len(ai_jobs), total_jobs, list(all_ai_tech))
        
        # Salary statistics for AI jobs
        salary_stats = self._calculate_salary_stats(ai_jobs)
        
        return {
            'total_jobs': total_jobs,
            'ai_jobs': len(ai_jobs),
            'ai_job_types': ai_job_types,
            'ai_tech_stack': list(all_ai_tech),
            'ai_score': ai_score,
            'salary_stats': salary_stats,
        }
    
    def _calculate_ai_score(self, ai_job_count: int, total_jobs: int, tech_stack: List[str]) -> float:
        """Calculate AI score (0-100)"""
        if total_jobs == 0:
            return 0.0
        
        # Base score from AI job ratio
        ratio = ai_job_count / total_jobs
        ratio_score = ratio * 50
        
        # Tech stack bonus
        tech_bonus = min(len(tech_stack) * 5, 30)
        
        # Job count bonus (companies with more AI jobs score higher)
        count_bonus = min(ai_job_count * 2, 20)
        
        total_score = ratio_score + tech_bonus + count_bonus
        
        return round(total_score, 1)
    
    def _calculate_salary_stats(self, ai_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate salary statistics for AI jobs"""
        salaries = []
        
        for ai_job in ai_jobs:
            job = ai_job['job']
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            
            if salary_min:
                salaries.append(salary_min)
            if salary_max:
                salaries.append(salary_max)
        
        if not salaries:
            return {'min': None, 'max': None, 'avg': None}
        
        return {
            'min': min(salaries),
            'max': max(salaries),
            'avg': sum(salaries) // len(salaries),
        }


# Convenience function
def analyze_job(job_data: Dict[str, Any]) -> Tuple[bool, Optional[str], List[str]]:
    """Analyze if a job is AI-related"""
    analyzer = AIJobAnalyzer()
    return analyzer.analyze_job(job_data)


def analyze_company(company_data: Dict[str, Any], jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze company's AI job status"""
    analyzer = AIJobAnalyzer()
    return analyzer.analyze_company(company_data, jobs)


# Language support
AI_JOB_TYPE_NAMES = {
    'llm_engineer': {
        'en': 'LLM Engineer',
        'ja': 'LLMエンジニア',
        'zh': 'LLM工程师',
    },
    'ml_engineer': {
        'en': 'Machine Learning Engineer',
        'ja': '機械学習エンジニア',
        'zh': '机器学习工程师',
    },
    'dl_engineer': {
        'en': 'Deep Learning Engineer',
        'ja': '深層学習エンジニア',
        'zh': '深度学习工程师',
    },
    'ai_agent_engineer': {
        'en': 'AI Agent Engineer',
        'ja': 'AIエージェントエンジニア',
        'zh': 'AI智能体工程师',
    },
    'data_scientist': {
        'en': 'Data Scientist',
        'ja': 'データサイエンティスト',
        'zh': '数据科学家',
    },
    'cv_engineer': {
        'en': 'Computer Vision Engineer',
        'ja': 'コンピュータビジョンエンジニア',
        'zh': '计算机视觉工程师',
    },
    'nlp_engineer': {
        'en': 'NLP Engineer',
        'ja': 'NLPエンジニア',
        'zh': 'NLP工程师',
    },
    'ai_researcher': {
        'en': 'AI Researcher',
        'ja': 'AI研究者',
        'zh': 'AI研究员',
    },
    'generative_ai': {
        'en': 'Generative AI Engineer',
        'ja': '生成AIエンジニア',
        'zh': '生成式AI工程师',
    },
}


def get_ai_type_name(ai_type: str, lang: str = 'en') -> str:
    """Get localized AI job type name"""
    if ai_type in AI_JOB_TYPE_NAMES:
        return AI_JOB_TYPE_NAMES[ai_type].get(lang, AI_JOB_TYPE_NAMES[ai_type]['en'])
    return ai_type
