"""
Search Views
Web views for company search UI
"""

from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django import forms
from django.contrib import messages

from apps.search.service import search_company_service, get_company_report_service


class SearchForm(forms.Form):
    """Search form for company name"""
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter company name (e.g., Preferred Networks, Mercari)',
        })
    )
    language = forms.ChoiceField(
        choices=[
            ('zh', '中文'),
            ('ja', '日本語'),
            ('en', 'English'),
        ],
        initial='zh',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class SearchView(FormView):
    """Main search page"""
    template_name = 'search/index.html'
    form_class = SearchForm
    
    def form_valid(self, form):
        company_name = form.cleaned_data['company_name']
        language = form.cleaned_data['language']
        
        try:
            result = search_company_service(company_name, language)
            return render(self.request, 'search/result.html', {
                'result': result,
                'company_name': company_name,
            })
        except Exception as e:
            messages.error(self.request, f'Search failed: {str(e)}')
            return render(self.request, 'search/index.html', {
                'form': form
            })


class HomeView(TemplateView):
    """Home page"""
    template_name = 'search/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context


def company_detail(request, company_id):
    """Company detail page"""
    language = request.GET.get('language', 'zh')
    
    result = get_company_report_service(company_id, language)
    
    if result is None:
        messages.error(request, 'Company not found')
        return render(request, 'search/index.html', {'form': SearchForm()})
    
    return render(request, 'search/result.html', {
        'result': result,
    })
