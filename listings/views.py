from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Car
from .forms import CarForm

class CarListView(ListView):
    model = Car
    template_name = 'index.html'
    context_object_name = 'cars'
    paginate_by = 10

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