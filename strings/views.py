from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import Q
import json

from .models import StringAnalysis
from .serializers import StringAnalysisSerializer
from .utils import compute_string_properties, parse_natural_language_query

from django.http import JsonResponse

def root_view(request):
    """Simple root view to handle base URL"""
    return JsonResponse({
        "message": "String Analyzer Service is running",
        "endpoints": {
            "POST /strings": "Create and analyze a string",
            "GET /strings/{string_value}": "Get specific string analysis", 
            "GET /strings": "Get all strings with filters",
            "GET /strings/filter-by-natural-language": "Filter using natural language",
            "DELETE /strings/{string_value}": "Delete string analysis"
        }
    })



class StringsView(APIView):
    """Handle both POST and GET for /strings endpoint"""
    
    def post(self, request):
        """POST /strings - Create and analyze a string."""
        
        # Check if value field exists
        if 'value' not in request.data:
            return Response(
                {'error': 'Missing "value" field'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if value is a string
        if not isinstance(request.data['value'], str):
            return Response(
                {'error': 'Invalid data type for "value" (must be string)'}, 
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        value = request.data['value'].strip()
        
        if not value:
            return Response(
                {'error': 'String value cannot be empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if string already exists
        if StringAnalysis.objects.filter(value=value).exists():
            return Response(
                {'error': 'String already exists in the system'}, 
                status=status.HTTP_409_CONFLICT
            )
        
        # Compute properties
        properties = compute_string_properties(value)
        
        # Create analysis object
        try:
            analysis = StringAnalysis.objects.create(
                id=properties['sha256_hash'],
                value=value,
                length=properties['length'],
                is_palindrome=properties['is_palindrome'],
                unique_characters=properties['unique_characters'],
                word_count=properties['word_count'],
                sha256_hash=properties['sha256_hash'],
                character_frequency_map=properties['character_frequency_map']
            )
            
            serializer = StringAnalysisSerializer(analysis)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except IntegrityError:
            return Response(
                {'error': 'String already exists in the system'}, 
                status=status.HTTP_409_CONFLICT
            )
    
    def get(self, request):
        """GET /strings - Get all strings with filtering."""
        
        analyses = StringAnalysis.objects.all()
        
        # Apply filters
        filters_applied = {}
        
        # Palindrome filter
        is_palindrome = request.GET.get('is_palindrome')
        if is_palindrome is not None:
            if is_palindrome.lower() in ['true', '1', 'yes']:
                analyses = analyses.filter(is_palindrome=True)
                filters_applied['is_palindrome'] = True
            elif is_palindrome.lower() in ['false', '0', 'no']:
                analyses = analyses.filter(is_palindrome=False)
                filters_applied['is_palindrome'] = False
        
        # Length filters
        min_length = request.GET.get('min_length')
        if min_length:
            try:
                min_length = int(min_length)
                analyses = analyses.filter(length__gte=min_length)
                filters_applied['min_length'] = min_length
            except ValueError:
                return Response(
                    {'error': 'Invalid min_length parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        max_length = request.GET.get('max_length')
        if max_length:
            try:
                max_length = int(max_length)
                analyses = analyses.filter(length__lte=max_length)
                filters_applied['max_length'] = max_length
            except ValueError:
                return Response(
                    {'error': 'Invalid max_length parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Word count filter
        word_count = request.GET.get('word_count')
        if word_count:
            try:
                word_count = int(word_count)
                analyses = analyses.filter(word_count=word_count)
                filters_applied['word_count'] = word_count
            except ValueError:
                return Response(
                    {'error': 'Invalid word_count parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Character containment filter
        contains_character = request.GET.get('contains_character')
        if contains_character and len(contains_character) == 1:
            analyses = analyses.filter(value__icontains=contains_character)
            filters_applied['contains_character'] = contains_character
        
        serializer = StringAnalysisSerializer(analyses, many=True)
        
        return Response({
            'data': serializer.data,
            'count': analyses.count(),
            'filters_applied': filters_applied
        })

class StringDetailView(APIView):
    """Handle GET and DELETE for /strings/{string_value} endpoint"""
    
    def get(self, request, string_value):
        """GET /strings/{string_value} - Get specific string analysis."""
        
        try:
            analysis = get_object_or_404(StringAnalysis, value=string_value)
            serializer = StringAnalysisSerializer(analysis)
            return Response(serializer.data)
        except StringAnalysis.DoesNotExist:
            return Response(
                {'error': 'String does not exist in the system'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, string_value):
        """DELETE /strings/{string_value} - Delete string analysis."""
        
        try:
            analysis = get_object_or_404(StringAnalysis, value=string_value)
            analysis.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except StringAnalysis.DoesNotExist:
            return Response(
                {'error': 'String does not exist in the system'}, 
                status=status.HTTP_404_NOT_FOUND
            )

@api_view(['GET'])
def natural_language_filter(request):
    """GET /strings/filter-by-natural-language - Filter using natural language."""
    
    query = request.GET.get('query')
    if not query:
        return Response(
            {'error': 'Missing "query" parameter'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    print(f"🎯 Natural Language Query: '{query}'")
    
    try:
        parsed_filters = parse_natural_language_query(query)
        
        # Check for conflicting filters
        if 'min_length' in parsed_filters and 'max_length' in parsed_filters:
            if parsed_filters['min_length'] > parsed_filters['max_length']:
                return Response(
                    {'error': 'Conflicting filters: min_length > max_length'}, 
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
        
        # Apply filters
        analyses = StringAnalysis.objects.all()
        initial_count = analyses.count()
        
        if 'is_palindrome' in parsed_filters:
            analyses = analyses.filter(is_palindrome=parsed_filters['is_palindrome'])
            print(f"  Applied is_palindrome filter: {parsed_filters['is_palindrome']}")
        
        if 'min_length' in parsed_filters:
            analyses = analyses.filter(length__gte=parsed_filters['min_length'])
            print(f"  Applied min_length filter: {parsed_filters['min_length']}")
        
        if 'max_length' in parsed_filters:
            analyses = analyses.filter(length__lte=parsed_filters['max_length'])
            print(f"  Applied max_length filter: {parsed_filters['max_length']}")
        
        if 'word_count' in parsed_filters:
            analyses = analyses.filter(word_count=parsed_filters['word_count'])
            print(f"  Applied word_count filter: {parsed_filters['word_count']}")
        
        if 'contains_character' in parsed_filters:
            analyses = analyses.filter(value__icontains=parsed_filters['contains_character'])
            print(f"  Applied contains_character filter: '{parsed_filters['contains_character']}'")
        
        final_count = analyses.count()
        print(f"  Results: {final_count}/{initial_count} strings match")
        
        serializer = StringAnalysisSerializer(analyses, many=True)
        
        return Response({
            'data': serializer.data,
            'count': analyses.count(),
            'interpreted_query': {
                'original': query,
                'parsed_filters': parsed_filters
            }
        })
        
    except Exception as e:
        print(f"❌ Error in natural language filter: {e}")
        return Response(
            {'error': f'Unable to parse natural language query: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

        