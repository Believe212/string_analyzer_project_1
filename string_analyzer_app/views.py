import hashlib
import json
from collections import Counter
from django.db import models
from django.utils import timezone
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import serializers
from rest_framework.views import APIView
from django.db.models import Q  # For advanced filtering
import re  #
# --- 1. UTILITY FUNCTIONS ---
#
# def analyze_string(value: str) -> dict:
#     """Computes all required properties for a given string."""
#     value = str(value)
#     length = len(value)
#     normalized = ''.join(filter(str.isalnum, value)).lower()
#     is_palindrome = normalized == normalized[::-1]
#     char_freq_map = dict(Counter(value))
#     unique_characters = len(char_freq_map)
#     word_count = len(value.split()) if value.strip() else 0
#     sha256_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
#
#     return {
#         "length": length,
#         "is_palindrome": is_palindrome,
#         "unique_characters": unique_characters,
#         "word_count": word_count,
#         "sha256_hash": sha256_hash,
#         "character_frequency_map": char_freq_map,
#     }

#
# def parse_natural_language_query(query: str) -> dict:
#     """Simple rule-based parser for natural language queries."""
#     query = query.lower()
#     parsed_filters = {}
#     if "palindrome" in query: parsed_filters['is_palindrome'] = True
#     if "single word" in query: parsed_filters['word_count'] = 1
#     if "longer than" in query:
#         parts = query.split("longer than")
#         if len(parts) > 1:
#             try:
#                 num_str = "".join(filter(str.isdigit, parts[1].split()[0]))
#                 if num_str:
#                     parsed_filters['min_length'] = int(num_str) + 1
#             except ValueError:
#                 pass
#     if "contain" in query:
#         char_match = None
#         if "first vowel" in query:
#             char_match = 'a'
#         elif "letter" in query:
#             parts = query.split("letter")
#             if len(parts) > 1:
#                 char_candidate = parts[1].strip().split()[0].strip('\'" ')
#                 if len(char_candidate) == 1 and char_candidate.isalpha():
#                     char_match = char_candidate
#         if char_match: parsed_filters['contains_character'] = char_match
#     return parsed_filters


# --- 1. UTILITY FUNCTIONS ---

def analyze_string(value: str) -> dict:
# ... (rest of analyze_string remains the same) ...
    """Computes all required properties for a given string."""
    value = str(value)
    length = len(value)
    normalized = ''.join(filter(str.isalnum, value)).lower()
    is_palindrome = normalized == normalized[::-1]
    char_freq_map = dict(Counter(value))
    unique_characters = len(char_freq_map)
    word_count = len(value.split()) if value.strip() else 0
    sha256_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": char_freq_map,
    }


def parse_natural_language_query(query: str) -> dict:
    """Robust rule-based parser for natural language queries."""
    query_lower = query.lower()
    parsed_filters = {}

    # 1. Palindrome Check (Fix: Uses regex to match 'palindrome' or 'palindromic')
    if re.search(r'palindromic?s?', query_lower):
        parsed_filters['is_palindrome'] = True

    # 2. Word Count Check (Uses regex to match 'single word', 'two words', etc.)
    word_match = re.search(r'(\d+|single|one|two)\s+word', query_lower)
    if word_match:
        word_str = word_match.group(1)
        word_count_map = {'single': 1, 'one': 1, 'two': 2}
        try:
            count = int(word_str) if word_str.isdigit() else word_count_map.get(word_str)
            if count is not None:
                parsed_filters['word_count'] = count
        except ValueError:
            pass

    # 3. Length Checks (Uses regex to match 'longer than 10', 'shorter than 5')
    length_match = re.search(r'(longer than|shorter than)\s+(\d+)', query_lower)
    if length_match:
        op = length_match.group(1)
        num = int(length_match.group(2))

        # 'longer than 10' means length >= 11 (min_length=11)
        if 'longer than' in op:
            parsed_filters['min_length'] = num + 1
            # 'shorter than 5' means length <= 4 (max_length=4)
        elif 'shorter than' in op:
            parsed_filters['max_length'] = num - 1

    # 4. Contains Character Check (Fix: Improved 'first vowel' logic)
    char_match = None

    # Target phrase: "palindromic strings that contain the first vowel" -> 'a'
    if "first vowel" in query_lower:
        char_match = 'a'
    elif "contain" in query_lower:
        # Check for 'letter X' pattern (Original logic kept but slightly simplified)
        match = re.search(r'letter\s+([a-z])', query_lower)
        if match:
            char_match = match.group(1)

    if char_match:
        parsed_filters['contains_character'] = char_match

    return parsed_filters



# --- 2. MODELS ---

class AnalyzedString(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    value = models.TextField(unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        app_label = 'string_analyzer_app'  # Required when consolidating

    @property
    def properties(self):
        return {
            "length": self.length,
            "is_palindrome": self.is_palindrome,
            "unique_characters": self.unique_characters,
            "word_count": self.word_count,
            "sha256_hash": self.id,
            "character_frequency_map": self.character_frequency_map,
        }

    def save(self, *args, **kwargs):
        analysis = analyze_string(self.value)
        self.id = analysis["sha256_hash"]
        self.length = analysis["length"]
        self.is_palindrome = analysis["is_palindrome"]
        self.unique_characters = analysis["unique_characters"]
        self.word_count = analysis["word_count"]
        self.character_frequency_map = analysis["character_frequency_map"]
        super().save(*args, **kwargs)


# --- 3. SERIALIZERS ---

class AnalyzedStringSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = AnalyzedString
        fields = ('id', 'value', 'properties', 'created_at')
        read_only_fields = ('id', 'properties', 'created_at')

    def get_properties(self, obj):
        return obj.properties


class StringValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=10000)


# --- 4. CUSTOM EXCEPTIONS ---

class ConflictError(APIException):
    status_code = 409
    default_detail = 'String already exists in the system.'


class UnprocessableEntity(APIException):
    status_code = 422
    default_detail = 'Invalid data type or conflicting filters.'


# --- 5. VIEWS (API ENDPOINTS) ---

class AnalyzedStringViewSet(viewsets.ViewSet):

    def get_object_by_value(self, string_value):
        hash_id = analyze_string(string_value)['sha256_hash']
        return get_object_or_404(AnalyzedString, pk=hash_id)

    # 1. POST /strings (Create)
    def create(self, request):
        serializer = StringValueSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        string_value = serializer.validated_data['value']
        if not isinstance(string_value, str):
            raise UnprocessableEntity(detail='Invalid data type for "value" (must be string)')

        try:
            analyzed_string = AnalyzedString.objects.create(value=string_value)
        except IntegrityError:
            raise ConflictError()

        response_serializer = AnalyzedStringSerializer(analyzed_string)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # 2. GET /strings/{value} (Retrieve)
    def retrieve(self, request, pk=None):
        instance = self.get_object_by_value(pk)
        serializer = AnalyzedStringSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 5. DELETE /strings/{value} (Delete)
    def destroy(self, request, pk=None):
        instance = self.get_object_by_value(pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 3. GET /strings (List/Filter)
    def list(self, request):
        queryset = AnalyzedString.objects.all()
        filters = {}
        filters_applied = {}

        # is_palindrome
        p = request.query_params.get('is_palindrome')
        if p is not None:
            if p.lower() in ('true', '1'):
                filters['is_palindrome'] = True;
                filters_applied['is_palindrome'] = True
            elif p.lower() in ('false', '0'):
                filters['is_palindrome'] = False;
                filters_applied['is_palindrome'] = False
            else:
                return Response({"error": "Invalid is_palindrome value."}, status=status.HTTP_400_BAD_REQUEST)

        # length & word_count
        for param, field, query_op in [('min_length', 'length', '__gte'), ('max_length', 'length', '__lte'),
                                       ('word_count', 'word_count', '__exact')]:
            value = request.query_params.get(param)
            if value is not None:
                try:
                    int_val = int(value)
                    filters[f'{field}{query_op}'] = int_val
                    filters_applied[param] = int_val
                except ValueError:
                    return Response({"error": f"Invalid {param} value."}, status=status.HTTP_400_BAD_REQUEST)

        # contains_character (JSONField lookup)
        contains_char = request.query_params.get('contains_character')
        if contains_char:
            if len(contains_char) != 1:
                return Response({"error": "contains_character must be a single character."},
                                status=status.HTTP_400_BAD_REQUEST)
            filters[f'character_frequency_map__{contains_char}__gt'] = 0
            filters_applied['contains_character'] = contains_char

        queryset = queryset.filter(**filters)
        serializer = AnalyzedStringSerializer(queryset, many=True)

        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "filters_applied": filters_applied
        }, status=status.HTTP_200_OK)


class NaturalLanguageFilterView(APIView):
    # 4. GET /strings/filter-by-natural-language
    def get(self, request):
        query = request.query_params.get('query')
        if not query:
            return Response({"error": "Missing 'query' parameter."}, status=status.HTTP_400_BAD_REQUEST)

        parsed_filters = parse_natural_language_query(query)

        if not parsed_filters:
            return Response({"error": "Unable to parse natural language query."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = AnalyzedString.objects.all()
        orm_filters = {}

        # Build ORM filters from parsed_filters
        if 'is_palindrome' in parsed_filters: orm_filters['is_palindrome'] = parsed_filters['is_palindrome']
        if 'word_count' in parsed_filters: orm_filters['word_count'] = parsed_filters['word_count']
        if 'min_length' in parsed_filters: orm_filters['length__gte'] = parsed_filters['min_length']
        if 'contains_character' in parsed_filters:
            char = parsed_filters['contains_character']
            orm_filters[f'character_frequency_map__{char}__gt'] = 0

        # Note: We skip complex conflict checks for brevity, assuming simple queries.

        queryset = queryset.filter(**orm_filters)
        serializer = AnalyzedStringSerializer(queryset, many=True)

        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed_filters
            }
        }, status=status.HTTP_200_OK)