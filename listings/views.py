from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Car, Brand, Model
from .forms import CarForm, BrandForm, ModelForm

class CarListView(ListView):
    model = Car
    template_name = 'index.html'
    context_object_name = 'cars'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')
        
        if query:
            queryset = queryset.filter(
                Q(brand__name__icontains=query) |
                Q(model__name__icontains=query) |
                Q(description__icontains=query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['query'] = self.request.GET.get('query', '')
        return context

class CarSearchView(ListView):
    model = Car
    template_name = 'listings/search_results.html'
    context_object_name = 'cars'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Car.objects.all()
        
        # Негізгі іздеу
        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(brand__name__icontains=query) |
                Q(model__name__icontains=query) |
                Q(description__icontains=query)
            )
        
        # Бренд бойынша сүзу
        brand_id = self.request.GET.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        
        # Модель бойынша сүзу
        model_id = self.request.GET.get('model')
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        
        # Баға аралығы бойынша сүзу
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Жыл аралығы бойынша сүзу
        min_year = self.request.GET.get('min_year')
        max_year = self.request.GET.get('max_year')
        if min_year:
            queryset = queryset.filter(year__gte=min_year)
        if max_year:
            queryset = queryset.filter(year__lte=max_year)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['models'] = Model.objects.all()
        
        # Формаларды қайта толтыру үшін барлық сүзгі параметрлерін контекстке беру
        for param in ['query', 'brand', 'model', 'min_price', 'max_price', 'min_year', 'max_year']:
            context[param] = self.request.GET.get(param, '')
        
        return context

class CarCatalogView(ListView):
    model = Car
    template_name = 'listings/catalog.html'
    context_object_name = 'cars'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Car.objects.all()
        
        # Бренд бойынша сүзу
        brand_slug = self.kwargs.get('brand_slug')
        if brand_slug:
            queryset = queryset.filter(brand__name__iexact=brand_slug)
        
        # Сұрыптау опциялары
        sort = self.request.GET.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'year_new':
            queryset = queryset.order_by('-year')
        elif sort == 'year_old':
            queryset = queryset.order_by('year')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['models'] = Model.objects.all()
        
        brand_slug = self.kwargs.get('brand_slug')
        if brand_slug:
            context['current_brand'] = brand_slug
            try:
                brand = Brand.objects.get(name__iexact=brand_slug)
                context['brand_models'] = Model.objects.filter(brand=brand)
            except Brand.DoesNotExist:
                context['brand_models'] = []
        
        context['sort'] = self.request.GET.get('sort', 'newest')
        return context

class CarDetailView(DetailView):
    model = Car
    template_name = 'car-details.html'
    context_object_name = 'car'

class SellerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.role == self.request.user.Role.SELLER or self.request.user.role == self.request.user.Role.ADMIN)

    def handle_no_permission(self):
        return render(self.request, '403.html')

class CarCreateView(SellerRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'listings/car_form.html'

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)

class CarUpdateView(SellerRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'listings/car_form.html'

    def test_func(self):
        is_seller_or_admin = super().test_func()
        if not is_seller_or_admin:
            return False
        car = self.get_object()
        return car.seller == self.request.user or self.request.user.is_admin

class CarDeleteView(SellerRequiredMixin, DeleteView):
    model = Car
    template_name = 'listings/car_confirm_delete.html'
    success_url = reverse_lazy('index')

    def test_func(self):
        is_seller_or_admin = super().test_func()
        if not is_seller_or_admin:
            return False
        car = self.get_object()
        return car.seller == self.request.user or self.request.user.is_admin

class SellerDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Car
    template_name = 'listings/seller_dashboard.html'
    context_object_name = 'cars'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_seller
    
    def get_queryset(self):
        return Car.objects.filter(seller=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_listings'] = self.get_queryset().count()
        return context

@login_required
@require_POST
def create_brand(request):
    """API view to create a new brand from the car form"""
    form = BrandForm(request.POST)
    if form.is_valid():
        brand = form.save()
        return JsonResponse({
            'success': True,
            'id': brand.id,
            'name': brand.name
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)

@login_required
@require_POST
def create_model(request):
    """API view to create a new model from the car form"""
    form = ModelForm(request.POST)
    if form.is_valid():
        model = form.save()
        return JsonResponse({
            'success': True,
            'id': model.id,
            'name': model.name,
            'brand_id': model.brand_id
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)

@login_required
def get_models_by_brand(request):
    """API view to get models for a specific brand"""
    brand_id = request.GET.get('brand')
    if not brand_id:
        return JsonResponse([], safe=False)
    
    models = Model.objects.filter(brand_id=brand_id).values('id', 'name')
    return JsonResponse(list(models), safe=False)