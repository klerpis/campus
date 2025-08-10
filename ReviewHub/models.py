from django.db import models

from Shop.models import Product
from campusprofile.models import Student

# Create your models here.


class ProductReview(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Optional: prevent duplicate reviews
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.user.username} rated {self.product.product_name} - {self.rating}/5'
