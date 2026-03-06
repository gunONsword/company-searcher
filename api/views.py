"""
API Views
REST API views for company search
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.search.service import search_company_service, get_company_report_service


@api_view(['POST'])
def search_company(request):
    """
    POST /api/search_company
    
    Input: { "company_name": "Preferred Networks", "language": "zh" }
    Output: { "company_info": {}, "jobs": [], "ai_jobs": [], "analysis": {} }
    """
    company_name = request.data.get('company_name')
    language = request.data.get('language', 'zh')
    
    if not company_name:
        return Response(
            {'error': 'company_name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = search_company_service(company_name, language)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_company(request, company_id):
    """
    GET /api/company/{id}
    
    Output: { "company_info": {}, "jobs": [], "ai_jobs": [], "analysis": {} }
    """
    language = request.query_params.get('language', 'zh')
    
    try:
        result = get_company_report_service(company_id, language)
        if result is None:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'ok', 'service': 'company-searcher'})
