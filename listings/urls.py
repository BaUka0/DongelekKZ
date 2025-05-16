from django.urls import path
from .views import (
    CarListView,
    CarDetailView,
    CarCreateView,
    CarUpdateView,
    CarDeleteView,
    CarSearchView,
    CarCatalogView,
    create_brand,
    create_model,
    get_models_by_brand,
)

urlpatterns = [
    path('', CarListView.as_view(), name='index'),
    path('car/new/', CarCreateView.as_view(), name='car_create'),
    path('car/<int:pk>/', CarDetailView.as_view(), name='car_detail'),
    path('car/<int:pk>/edit/', CarUpdateView.as_view(), name='car_update'),
    path('car/<int:pk>/delete/', CarDeleteView.as_view(), name='car_delete'),
    path('search/', CarSearchView.as_view(), name='car_search'),
    path('catalog/', CarCatalogView.as_view(), name='catalog'),
    path('catalog/<str:brand_slug>/', CarCatalogView.as_view(), name='catalog_by_brand'),
    
    # API endpoints
    path('api/brands/create/', create_brand, name='create_brand'),
    path('api/models/create/', create_model, name='create_model'),
    path('api/models/', get_models_by_brand, name='get_models_by_brand'),
]