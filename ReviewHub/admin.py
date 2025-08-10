from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from . import models

# Register your models here.


@admin.register(models.ProductReview)
class ProductReviewAdmin(UnfoldModelAdmin):
    pass
