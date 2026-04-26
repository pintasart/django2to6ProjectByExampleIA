from django.contrib import admin
from .models import Category, Product
from parler.admin import TranslatableAdmin


@admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
class CategoryAdmin(TranslatableAdmin):

    list_display = ['name', 'slug']
    # prepopulated_fields = {'slug': ('name',)}
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

@admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
class ProductAdmin(TranslatableAdmin):
    list_display = ['name', 'slug', 'price','available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    #Any field in list_editable must also be listed in the list_display attribute since only the fields displayed can be edited.
    list_editable = ['price', 'available']
    #we use the prepopulated_fields attribute to specify fields where the value is automatically set using the value of other fields
    # prepopulated_fields = {'slug': ('name',)}
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


