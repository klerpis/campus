from django.contrib import admin

from Shop import models
from unfold.admin import ModelAdmin as UnfoldModelAdmin

# Register your models here.


# shop/admin.py


@admin.register(models.Store)
# class StoreAdmin(admin.ModelAdmin):
class StoreAdmin(UnfoldModelAdmin):
    list_display = ('store_name', 'vendor',
                    'created_at', 'currently_active', 'approved', )
    list_editable = ['approved']
    list_display_links = ['store_name', 'vendor',]
    list_filter = ('approved', 'created_at')
    actions = ['approve_stores']

    @admin.action(description='Approve selected stores')
    def approve_stores(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f'{updated} store(s) approved.')


@admin.register(models.Category)
class CategoryAdmin(UnfoldModelAdmin):
    pass


# admin.site.register(models.Product)
@admin.register(models.Product)
class ProductAdmin(UnfoldModelAdmin):
    pass


# admin.site.register(models.StoreType)
# admin.site.register(models.Store, UnfoldModelAdmin)


@admin.register(models.StoreType)
class StoreTypeAdmin(UnfoldModelAdmin):
    pass
