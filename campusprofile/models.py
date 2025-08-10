from django.db import models

from django.contrib.auth import get_user_model
from django.conf import settings
from Shop.models import Store

User = get_user_model()


class Credentials(models.Model):
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL, verbose_name="User's Name", on_delete=models.CASCADE,
    #     null=True, blank=True)
    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=40, null=True, blank=True)
    phonenumber = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(
        choices=[('student', 'student'), ('vendor', 'vendor')])
    email = models.CharField(max_length=35)

    class Meta:
        abstract = True


class Vendor(Credentials):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='vendor',
        verbose_name="User's Name",
        on_delete=models.CASCADE,
        null=True, blank=True)

    store = models.OneToOneField(
        Store, related_name='vendor',
        on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        print()
        print("dir for store", self.store)
        print()
        print()
        print()
        if hasattr(self, 'store') and self.store:
            store_name = self.store.store_name
        else:
            store_name = "NO store yet"

        return f'Vendor {self.first_name or self.user.username} for Store: {store_name}'


class Student(Credentials):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='student',
        verbose_name="User's Name",
        on_delete=models.CASCADE,
        null=True, blank=True)

    def __str__(self):
        return f"Student: {self.user.username.capitalize()}"
