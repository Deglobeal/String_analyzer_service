from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import StringAnalysis
from .serializers import StringAnalysisSerializer, StringCreateSerializer
import re

@api_view(['POST'])
def create_analyze_string(request):
    """Create/Analyze String - POST /strings"""
    serializer = StringCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        errors = serializer.errors
        if 'value' in errors:
            if 'required' in str(errors['value']).lower():
                return Response(
                    {"error": "Missing 'value' field"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "Invalid data type for 'value' (must be string)"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
    
    string_value = serializer.validated_data['value']
    
    try:
        # Check if string already exists
        analysis = StringAnalysis.analyze_string(string_value)
        analysis.save()
        
        response_serializer = StringAnalysisSerializer(analysis)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except IntegrityError:
        # String already exists (unique constraint on value)
        existing_analysis = StringAnalysis.objects.get(value=string_value)
        response_serializer = StringAnalysisSerializer(existing_analysis)
        return Response(response_serializer.data, status=status.HTTP_409_CONFLICT)

@api_view(['GET'])
def get_string_analysis(request, string_value):
    """Get Specific String - GET /strings/{string_value}"""
    analysis = get_object_or_404(StringAnalysis, value=string_value)
    serializer = StringAnalysisSerializer(analysis)
    return Response(serializer.data)

@api_view(['GET'])
def list_strings_with_filters(request):
    """Get All Strings with Filtering - GET /strings"""
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
            queryset = queryset.filter(length__gte=int(min_length))
            filters_applied['min_length'] = int(min_length)
        except ValueError:
            return Response(
                {"error": "Invalid min_length parameter"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    max_length = request.GET.get('max_length')
    if max_length is not None:
        try:
            queryset = queryset.filter(length__lte=int(max_length))
            filters_applied['max_length'] = int(max_length)
        except ValueError:
            return Response(
                {"error": "Invalid max_length parameter"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    word_count = request.GET.get('word_count')
    if word_count is not None:
        try:
            queryset = queryset.filter(word_count=int(word_count))
            filters_applied['word_count'] = int(word_count)
        except ValueError:
            return Response(
                {"error": "Invalid word_count parameter"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    contains_character = request.GET.get('contains_character')
    if contains_character is not None:
        if len(contains_character) != 1:
            return Response(
                {"error": "contains_character must be a single character"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        # Filter by character frequency map
        character = contains_character.lower()
        queryset = [obj for obj in queryset if character in obj.character_frequency_map]
        filters_applied['contains_character'] = contains_character
    
    serializer = StringAnalysisSerializer(queryset, many=True)
    
    return Response({
        'data': serializer.data,
        'count': len(serializer.data),
        'filters_applied': filters_applied
    })

@api_view(['GET'])
def filter_by_natural_language(request):
    """Natural Language Filtering - GET /strings/filter-by-natural-language"""
    query = request.GET.get('query', '').lower().strip()
    
    if not query:
        return Response(
            {"error": "Missing query parameter"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    parsed_filters = {}
    queryset = StringAnalysis.objects.all()
    
    try:
        # Parse natural language query
        if 'palindromic' in query or 'palindrome' in query:
            parsed_filters['is_palindrome'] = True
            queryset = queryset.filter(is_palindrome=True)
        
        if 'single word' in query or 'one word' in query:
            parsed_filters['word_count'] = 1
            queryset = queryset.filter(word_count=1)
        
        # Extract length patterns
        length_match = re.search(r'longer than (\d+)', query)
        if length_match:
            min_len = int(length_match.group(1)) + 1
            parsed_filters['min_length'] = min_len
            queryset = queryset.filter(length__gte=min_len)
        
        length_match = re.search(r'shorter than (\d+)', query)
        if length_match:
            max_len = int(length_match.group(1)) - 1
            parsed_filters['max_length'] = max_len
            queryset = queryset.filter(length__lte=max_len)
        
        # Extract character patterns
        char_match = re.search(r'contain[s]? (?:the letter |the character )?([a-zA-Z])', query)
        if char_match:
            character = char_match.group(1).lower()
            parsed_filters['contains_character'] = character
            queryset = [obj for obj in queryset if character in obj.character_frequency_map]
        
        # Handle "first vowel" case
        if 'first vowel' in query:
            parsed_filters['contains_character'] = 'a'
            queryset = [obj for obj in queryset if 'a' in obj.character_frequency_map]
        
        serializer = StringAnalysisSerializer(queryset, many=True)
        
        return Response({
            'data': serializer.data,
            'count': len(serializer.data),
            'interpreted_query': {
                'original': query,
                'parsed_filters': parsed_filters
            }
        })
        
    except Exception as e:
        return Response(
            {"error": "Unable to parse natural language query"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
def delete_string_analysis(request, string_value):
    """Delete String - DELETE /strings/{string_value}"""
    analysis = get_object_or_404(StringAnalysis, value=string_value)
    analysis.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)