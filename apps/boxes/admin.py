from django.contrib import admin
from .models import Box, BoxCategory

@admin.register(BoxCategory)
class BoxCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'price_per_hour', 'status')
    list_filter = ('status','category',)
    search_fields = ('name',)