from django.db import models


class Company(models.Model):
    """Company model - stores Japanese company information"""
    
    name = models.CharField(max_length=255, verbose_name='Company Name')
    domain = models.CharField(max_length=255, verbose_name='Domain', blank=True, null=True)
    business = models.TextField(verbose_name='Business Field', blank=True, null=True)
    founded = models.IntegerField(verbose_name='Established Year', blank=True, null=True)
    capital = models.CharField(max_length=100, verbose_name='Capital', blank=True, null=True)
    employees = models.CharField(max_length=100, verbose_name='Employee Count', blank=True, null=True)
    headquarter = models.CharField(max_length=255, verbose_name='Headquarter', blank=True, null=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    logo_url = models.URLField(verbose_name='Logo URL', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'business': self.business,
            'founded': self.founded,
            'capital': self.capital,
            'employees': self.employees,
            'headquarter': self.headquarter,
            'description': self.description,
            'logo_url': self.logo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
