import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Profile
from .nlp_parser import NaturalLanguageParser

def api_docs(request):
    """Render the API documentation page"""
    return render(request, 'docs.html')

def add_cors(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def error_response(status, message):
    res = JsonResponse({'status': 'error', 'message': message}, status=status)
    return add_cors(res)

def json_response(data, status=200):
    res = JsonResponse(data, status=status)
    return add_cors(res)


@method_decorator(csrf_exempt, name='dispatch')
class ProfileListCreateView(View):
    
    def options(self, request, *args, **kwargs):
        res = HttpResponse(status=204)
        res['Access-Control-Allow-Origin'] = '*'
        res['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        res['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return res
    
    def get(self, request):
        queryset = Profile.objects.all()
        
        # Apply filters
        gender = request.GET.get('gender', '').strip().lower()
        if gender:
            if gender not in ['male', 'female']:
                return error_response(422, 'Invalid gender value')
            queryset = queryset.filter(gender=gender)
        
        age_group = request.GET.get('age_group', '').strip().lower()
        if age_group:
            valid_groups = ['child', 'teenager', 'adult', 'senior']
            if age_group not in valid_groups:
                return error_response(422, 'Invalid age_group')
            queryset = queryset.filter(age_group=age_group)
        
        country_id = request.GET.get('country_id', '').strip().upper()
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        
        min_age = request.GET.get('min_age', '').strip()
        if min_age:
            try:
                min_age = int(min_age)
                queryset = queryset.filter(age__gte=min_age)
            except ValueError:
                return error_response(422, 'min_age must be an integer')
        
        max_age = request.GET.get('max_age', '').strip()
        if max_age:
            try:
                max_age = int(max_age)
                queryset = queryset.filter(age__lte=max_age)
            except ValueError:
                return error_response(422, 'max_age must be an integer')
        
        min_gender_prob = request.GET.get('min_gender_probability', '').strip()
        if min_gender_prob:
            try:
                min_gender_prob = float(min_gender_prob)
                queryset = queryset.filter(gender_probability__gte=min_gender_prob)
            except ValueError:
                return error_response(422, 'min_gender_probability must be a number')
        
        min_country_prob = request.GET.get('min_country_probability', '').strip()
        if min_country_prob:
            try:
                min_country_prob = float(min_country_prob)
                queryset = queryset.filter(country_probability__gte=min_country_prob)
            except ValueError:
                return error_response(422, 'min_country_probability must be a number')
        
        # Apply sorting
        sort_by = request.GET.get('sort_by', '').strip().lower()
        order = request.GET.get('order', '').strip().lower()
        
        allowed_sort_fields = ['age', 'created_at', 'gender_probability']
        
        if sort_by:
            if sort_by not in allowed_sort_fields:
                return error_response(422, 'Invalid sort_by field')
            
            if order == 'desc':
                sort_by = f'-{sort_by}'
            elif order and order != 'asc':
                return error_response(422, 'Invalid order value. Use asc or desc')
            
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 10)
        
        try:
            page = int(page)
            limit = int(limit)
            if limit > 50:
                limit = 50
            if limit < 1:
                limit = 10
            if page < 1:
                page = 1
        except ValueError:
            return error_response(422, 'page and limit must be integers')
        
        paginator = Paginator(queryset, limit)
        
        try:
            profiles_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            return error_response(404, 'Page not found')
        
        profiles = [p.to_dict(full=False) for p in profiles_page]
        
        return json_response({
            'status': 'success',
            'page': page,
            'limit': limit,
            'total': paginator.count,
            'data': profiles
        }, status=200)
    
    def post(self, request):
        """POST endpoint for creating profiles (not the primary method - use seed data)"""
        return error_response(501, 'Use the seed_data command to add profiles. See README for details.')


@method_decorator(csrf_exempt, name='dispatch')
class ProfileSearchView(View):
    
    def options(self, request, *args, **kwargs):
        res = HttpResponse(status=204)
        res['Access-Control-Allow-Origin'] = '*'
        res['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        res['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return res
    
    def get(self, request):
        q = request.GET.get('q', '').strip()
        
        if not q:
            return error_response(400, 'Missing or empty query parameter')
        
        # Parse natural language query
        filters, error = NaturalLanguageParser.parse(q)
        
        if error:
            return error_response(400, error)
        
        queryset = Profile.objects.all()
        
        # Apply parsed filters
        if 'gender' in filters:
            queryset = queryset.filter(gender=filters['gender'])
        
        if 'age_group' in filters:
            queryset = queryset.filter(age_group=filters['age_group'])
        
        if 'country_id' in filters:
            queryset = queryset.filter(country_id=filters['country_id'])
        
        if 'min_age' in filters:
            queryset = queryset.filter(age__gte=filters['min_age'])
        
        if 'max_age' in filters:
            queryset = queryset.filter(age__lte=filters['max_age'])
        
        # Apply pagination
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 10)
        
        try:
            page = int(page)
            limit = int(limit)
            if limit > 50:
                limit = 50
            if limit < 1:
                limit = 10
            if page < 1:
                page = 1
        except ValueError:
            return error_response(422, 'page and limit must be integers')
        
        paginator = Paginator(queryset, limit)
        
        try:
            profiles_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            return error_response(404, 'Page not found')
        
        profiles = [p.to_dict(full=False) for p in profiles_page]
        
        return json_response({
            'status': 'success',
            'query': q,
            'interpreted_as': filters,
            'page': page,
            'limit': limit,
            'total': paginator.count,
            'data': profiles
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ProfileDetailView(View):
    
    def options(self, request, *args, **kwargs):
        res = HttpResponse(status=204)
        res['Access-Control-Allow-Origin'] = '*'
        res['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        res['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return res
    
    def get(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
        except (Profile.DoesNotExist, ValueError):
            return error_response(404, 'Profile not found')
        
        return json_response({'status': 'success', 'data': profile.to_dict(full=True)}, status=200)
    
    def delete(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
        except (Profile.DoesNotExist, ValueError):
            return error_response(404, 'Profile not found')
        
        profile.delete()
        res = HttpResponse(status=204)
        res['Access-Control-Allow-Origin'] = '*'
        return res