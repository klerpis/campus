from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=40)

    def __str__(self):
        return f'[{self.category_name.capitalize()}]'


class StoreType(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return f'[{self.name.capitalize()}] Store'


class Product(models.Model):

    product_name = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    price = models.CharField(max_length=20)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(default='product_images/default.png',
                              upload_to='product_images/', null=True, blank=True)
    # variant is a sub category of a product and is linked to only one possible product,
    # like face-cap is a variant of Cap
    variant = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, related_name='main_product', null=True, blank=True)
    discount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    store = models.ForeignKey(
        "Store", on_delete=models.CASCADE, related_name='products', default="")

    def __str__(self):
        return f"{self.product_name} sold at {self.price}"


class Store(models.Model):
    store_name = models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    description = models.TextField(null=True, blank=True)
    store_type = models.ForeignKey(StoreType, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    currently_active = models.BooleanField(default=False)
    # active_time_range = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    # products = models.ManyToManyField(
    #     Product, related_name='store')

    def __str__(self):
        return f"{self.store_name} belonging to {self.address}"
