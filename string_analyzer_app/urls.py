from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# /strings/ and /strings/{value}
router.register(r'strings', views.AnalyzedStringViewSet, basename='string')

urlpatterns = [
    *router.urls,
    # /strings/filter-by-natural-language
    path(
        'strings/filter-by-natural-language',
        views.NaturalLanguageFilterView.as_view(),
        name='natural-language-filter'
    ),
]