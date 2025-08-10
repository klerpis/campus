from django.db import models

from django.contrib.auth.models import User
# Create your models here.

from Shop.models import Product, Store
from orders.models import Order


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)  # NEW
    refunded = models.BooleanField(default=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    sold_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Sale made for -> {self.product.product_name}'


class Stock(models.Model):
    product = models.OneToOneField(
        Product, related_name='stock', on_delete=models.CASCADE)
    count = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.product.product_name} has a stock of {self.count}'


class SaleLog(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=[(
        'created', 'Created'), ('refunded', 'Refunded')])
    timestamp = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Log for Sale -> {self.sale}'
