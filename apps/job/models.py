from django.db import models
from apps.company.models import Company


class Job(models.Model):
    """Job model - stores job listings from Japanese recruitment sites"""
    
    JOB_TYPE_CHOICES = [
        ('fulltime', 'Full-time'),
        ('contract', 'Contract'),
        ('parttime', 'Part-time'),
        ('intern', 'Intern'),
    ]
    
    REMOTE_CHOICES = [
        ('full_remote', 'Full Remote'),
        ('hybrid', 'Hybrid'),
        ('onsite', 'On-site'),
        ('unknown', 'Unknown'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255, verbose_name='Job Title')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='fulltime')
    salary = models.CharField(max_length=100, verbose_name='Salary', blank=True, null=True)
    salary_min = models.IntegerField(verbose_name='Salary Min (JPY)', blank=True, null=True)
    salary_max = models.IntegerField(verbose_name='Salary Max (JPY)', blank=True, null=True)
    benefits = models.TextField(verbose_name='Benefits', blank=True, null=True)
    vacation_days = models.CharField(max_length=50, verbose_name='Vacation Days', blank=True, null=True)
    remote = models.CharField(max_length=20, choices=REMOTE_CHOICES, default='unknown')
    tech_stack = models.JSONField(verbose_name='Tech Stack', default=list, blank=True)
    description = models.TextField(verbose_name='Job Description', blank=True, null=True)
    requirements = models.TextField(verbose_name='Requirements', blank=True, null=True)
    source_url = models.URLField(verbose_name='Source URL')
    source_name = models.CharField(max_length=50, verbose_name='Source Site')
    is_ai_related = models.BooleanField(default=False, verbose_name='AI Related')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.name} - {self.title}"

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name,
            'title': self.title,
            'job_type': self.job_type,
            'salary': self.salary,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'benefits': self.benefits,
            'vacation_days': self.vacation_days,
            'remote': self.remote,
            'tech_stack': self.tech_stack,
            'description': self.description,
            'requirements': self.requirements,
            'source_url': self.source_url,
            'source_name': self.source_name,
            'is_ai_related': self.is_ai_related,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AIJob(models.Model):
    """AI Job model - stores AI-specific job information"""
    
    AI_TYPE_CHOICES = [
        ('llm_engineer', 'LLM Engineer'),
        ('ml_engineer', 'Machine Learning Engineer'),
        ('dl_engineer', 'Deep Learning Engineer'),
        ('ai_agent_engineer', 'AI Agent Engineer'),
        ('data_scientist', 'Data Scientist'),
        ('cv_engineer', 'Computer Vision Engineer'),
        ('nlp_engineer', 'NLP Engineer'),
        ('ai_researcher', 'AI Researcher'),
        ('generative_ai', 'Generative AI Engineer'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='ai_jobs')
    ai_type = models.CharField(max_length=50, choices=AI_TYPE_CHOICES)
    ai_tech_stack = models.JSONField(verbose_name='AI Tech Stack', default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_jobs'
        verbose_name = 'AI Job'
        verbose_name_plural = 'AI Jobs'

    def __str__(self):
        return f"{self.job.title} - {self.get_ai_type_display()}"
