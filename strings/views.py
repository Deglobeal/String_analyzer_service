from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import StringAnalysis
from .serializers import (
    StringAnalysisSerializer, 
    StringInputSerializer,
    FilterResponseSerializer
)
from .utils import StringAnalyzer, NaturalLanguageParser

@api_view(['POST'])
def create_analyze_string(request):
    """Create/Analyze String endpoint"""
    serializer = StringInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        if 'value' in serializer.errors:
            if 'This field is required' in str(serializer.errors['value']):
                return Response(
                    {'error': 'Missing "value" field'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error': 'Invalid data type for "value" (must be string)'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
        return Response(
            {'error': 'Invalid request body'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    value = serializer.validated_data['value']
    analysis_result = StringAnalyzer.analyze_string(value)
    
    # Check if string already exists
    if StringAnalysis.objects.filter(id=analysis_result['id']).exists():
        return Response(
            {'error': 'String already exists in the system'},
            status=status.HTTP_409_CONFLICT
        )
    
    # Create and save the analysis
    analysis = StringAnalysis.objects.create(
        id=analysis_result['id'],
        value=analysis_result['value'],
        length=analysis_result['properties']['length'],
        is_palindrome=analysis_result['properties']['is_palindrome'],
        unique_characters=analysis_result['properties']['unique_characters'],
        word_count=analysis_result['properties']['word_count'],
        character_frequency_map=analysis_result['properties']['character_frequency_map']
    )
    
    response_serializer = StringAnalysisSerializer(analysis)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_string(request, string_value):
    """Get Specific String endpoint"""
    analysis = get_object_or_404(StringAnalysis, value=string_value)
    serializer = StringAnalysisSerializer(analysis)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_strings(request):
    """Get All Strings with Filtering endpoint"""
    queryset = StringAnalysis.objects.all()
    
    # Apply filters
    filters_applied = {}
    
    is_palindrome = request.GET.get('is_palindrome')
    if is_palindrome is not None:
        if is_palindrome.lower() in ['true', '1']:
            queryset = queryset.filter(is_palindrome=True)
            filters_applied['is_palindrome'] = True
        elif is_palindrome.lower() in ['false', '0']:
            queryset = queryset.filter(is_palindrome=False)
            filters_applied['is_palindrome'] = False
    
    min_length = request.GET.get('min_length')
    if min_length is not None:
        try:
            min_length = int(min_length)
            queryset = queryset.filter(length__gte=min_length)
            filters_applied['min_length'] = min_length
        except ValueError:
            return Response(
                {'error': 'min_length must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    max_length = request.GET.get('max_length')
    if max_length is not None:
        try:
            max_length = int(max_length)
            queryset = queryset.filter(length__lte=max_length)
            filters_applied['max_length'] = max_length
        except ValueError:
            return Response(
                {'error': 'max_length must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    word_count = request.GET.get('word_count')
    if word_count is not None:
        try:
            word_count = int(word_count)
            queryset = queryset.filter(word_count=word_count)
            filters_applied['word_count'] = word_count
        except ValueError:
            return Response(
                {'error': 'word_count must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    contains_character = request.GET.get('contains_character')
    if contains_character is not None:
        if len(contains_character) != 1:
            return Response(
                {'error': 'contains_character must be a single character'},
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = queryset.filter(value__icontains=contains_character)
        filters_applied['contains_character'] = contains_character
    
    # Serialize response
    serializer = StringAnalysisSerializer(queryset, many=True)
    response_data = {
        'data': serializer.data,
        'count': len(serializer.data),
        'filters_applied': filters_applied
    }
    
    return Response(response_data)

@api_view(['GET'])
def filter_by_natural_language(request):
    """Natural Language Filtering endpoint"""
    query = request.GET.get('query')
    
    if not query:
        return Response(
            {'error': 'Query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        parsed_filters = NaturalLanguageParser.parse_query(query)
    except Exception as e:
        return Response(
            {'error': 'Unable to parse natural language query'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check for conflicting filters
    if 'min_length' in parsed_filters and 'max_length' in parsed_filters:
        if parsed_filters['min_length'] > parsed_filters['max_length']:
            return Response(
                {'error': 'Conflicting filters: min_length > max_length'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
    
    # Apply parsed filters
    queryset = StringAnalysis.objects.all()
    
    if 'is_palindrome' in parsed_filters:
        queryset = queryset.filter(is_palindrome=parsed_filters['is_palindrome'])
    
    if 'min_length' in parsed_filters:
        queryset = queryset.filter(length__gte=parsed_filters['min_length'])
    
    if 'max_length' in parsed_filters:
        queryset = queryset.filter(length__lte=parsed_filters['max_length'])
    
    if 'word_count' in parsed_filters:
        queryset = queryset.filter(word_count=parsed_filters['word_count'])
    
    if 'contains_character' in parsed_filters:
        queryset = queryset.filter(value__icontains=parsed_filters['contains_character'])
    
    # Serialize response
    serializer = StringAnalysisSerializer(queryset, many=True)
    response_data = {
        'data': serializer.data,
        'count': len(serializer.data),
        'interpreted_query': {
            'original': query,
            'parsed_filters': parsed_filters
        }
    }
    
    return Response(response_data)

@api_view(['DELETE'])
def delete_string(request, string_value):
    """Delete String endpoint"""
    analysis = get_object_or_404(StringAnalysis, value=string_value)
    analysis.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)