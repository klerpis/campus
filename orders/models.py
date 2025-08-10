from django.db import models

from Shop.models import Product, Store
from campusprofile.models import Student


class Cart(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.product_name} in {self.user.user.username}\'s cart'


class Order(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    ordered_at = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)  # NEW
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[('card', 'Card'), ('bank', 'Bank Transfer'),
                 ('cash', 'Cash on Delivery')],
        default='cash'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'),
                 ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending'
    )
    payment_reference = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.id}|| {self.store.store_name.upper()} (Store) received an Order from {str(self.student.user.username).upper()} (Student) - status: [{self.status}]'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.product_name}'


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=30, default='cash')
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment for {self.order.id} - {self.amount_paid}'


class Wishlist(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} wishes for {self.product.product_name}'
