from django.contrib import admin
from .models import Car, Brand, Model

class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'price', 'seller', 'created_at')
    list_filter = ('brand', 'year', 'seller')
    search_fields = ('brand__name', 'model__name', 'description')

admin.site.register(Car, CarAdmin)
admin.site.register(Brand)
admin.site.register(Model)