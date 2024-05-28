from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    postcode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.postcode}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_address = models.OneToOneField(Address, related_name='shipping_address', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Clothing', 'Clothing'),
        ('Electronics', 'Electronics'),
        ('Home Appliances', 'Home Appliances'),
        ('Sports & Outdoors', 'Sports & Outdoors'),
        ('Books & Media', 'Books & Media')
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=50)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)


class OrderPayment(models.Model):
    card_number = models.CharField(max_length=16)
    txnid = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    billing_address = models.OneToOneField(Address, related_name='billing_address', on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='CartItem')

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"

    def subtotal(self):
        return self.product.price * self.quantity
