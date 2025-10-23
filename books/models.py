from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Author(models.Model):
    AuthorID = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=100)
    LastName = models.CharField(max_length=100)
    Bio = models.TextField(blank=True, null=True)
    DateOfBirth = models.DateField(blank=True, null=True)
    DateOfDeath = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"

    @property
    def full_name(self):
        return f"{self.FirstName} {self.LastName}"

class Genre(models.Model):
    GenreID = models.AutoField(primary_key=True)
    GenreName = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.GenreName

class Book(models.Model):
    BookID = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=200)
    AuthorID = models.ForeignKey(Author, on_delete=models.CASCADE)
    GenreID = models.ForeignKey(Genre, on_delete=models.CASCADE)
    ISBN = models.CharField(max_length=13, unique=True)
    PublicationDate = models.DateField()
    Price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    Stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    Photo = models.CharField(max_length=200, default='', blank=True)

    def __str__(self):
        return self.Title

    @property
    def is_available(self):
        return self.Stock > 0

    @property
    def photo_url(self):
        if self.Photo:
            return self.Photo
        else:
            # Default book cover image
            return "https://via.placeholder.com/200x300/cccccc/666666/?text=No+Cover"

class Customer(models.Model):
    CustomerID = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    FirstName = models.CharField(max_length=100)
    LastName = models.CharField(max_length=100)
    Email = models.EmailField(unique=True)
    Phone = models.CharField(max_length=15, blank=True, null=True)
    Address = models.TextField()
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)
    ZipCode = models.CharField(max_length=10)
    ProfilePicture = models.CharField(max_length=200, blank=True, null=True)  # Optional: for profile pics
    DateJoined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"

    def get_full_name(self):
        return f"{self.FirstName} {self.LastName}"

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    OrderID = models.AutoField(primary_key=True)
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    OrderDate = models.DateTimeField(auto_now_add=True)
    TotalAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    OrderStatus = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')

    def __str__(self):
        return f"Order {self.OrderID} - {self.CustomerID}"

    def update_total_amount(self):
        total = sum(item.TotalPrice for item in self.orderitems.all())
        self.TotalAmount = total
        self.save()

class OrderItem(models.Model):
    OrderItemID = models.AutoField(primary_key=True)
    OrderID = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    BookID = models.ForeignKey(Book, on_delete=models.CASCADE)
    Quantity = models.IntegerField(validators=[MinValueValidator(1)])
    UnitPrice = models.DecimalField(max_digits=10, decimal_places=2)
    TotalPrice = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.TotalPrice = self.UnitPrice * self.Quantity
        super().save(*args, **kwargs)
        self.OrderID.update_total_amount()

    def __str__(self):
        return f"{self.Quantity} x {self.BookID.Title}"

class Review(models.Model):
    ReviewID = models.AutoField(primary_key=True)
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    BookID = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    ReviewText = models.TextField()
    ReviewDate = models.DateTimeField(auto_now_add=True)
    Rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ['CustomerID', 'BookID']

    def __str__(self):
        return f"Review by {self.CustomerID} for {self.BookID.Title}"