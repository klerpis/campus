from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from . import models


@admin.register(models.Sale)
class SaleAdmin(UnfoldModelAdmin):
    pass


@admin.register(models.Stock)
class StockAdmin(UnfoldModelAdmin):
    pass


# admin.site.register(models.Sale)
# admin.site.register(models.Stock)
