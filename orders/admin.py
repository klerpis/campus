from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin


from . import models


@admin.register(models.Order)
class OrderAdmin(UnfoldModelAdmin):
    pass


@admin.register(models.OrderItem)
class OrderItemAdmin(UnfoldModelAdmin):
    pass


@admin.register(models.Payment)
class PaymentAdmin(UnfoldModelAdmin):
    pass


@admin.register(models.Wishlist)
class WishlistAdmin(UnfoldModelAdmin):
    pass


# admin.site.register(models.Order)
# admin.site.register(models.OrderItem)
# admin.site.register(models.Payment)
# admin.site.register(models.Wishlist)
