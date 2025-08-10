from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin


from . import models


@admin.register(models.Student)
class StudentAdmin(UnfoldModelAdmin):
    pass


@admin.register(models.Vendor)
class VendorAdmin(UnfoldModelAdmin):
    pass


# admin.site.register(models.Student)
# admin.site.register(models.Vendor)
