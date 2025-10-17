from django.contrib import admin
from .models import Author, Genre, Book, Customer, Order, OrderItem, Review

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['FirstName', 'LastName', 'DateOfBirth']
    search_fields = ['FirstName', 'LastName']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['GenreName']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['Title', 'AuthorID', 'GenreID', 'Price', 'Stock', 'Photo']
    list_filter = ['GenreID', 'AuthorID']
    search_fields = ['Title', 'ISBN']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['FirstName', 'LastName', 'Email', 'City']
    search_fields = ['FirstName', 'LastName', 'Email']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['OrderID', 'CustomerID', 'OrderDate', 'TotalAmount', 'OrderStatus']
    list_filter = ['OrderStatus', 'OrderDate']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['OrderItemID', 'OrderID', 'BookID', 'Quantity', 'TotalPrice']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['CustomerID', 'BookID', 'Rating', 'ReviewDate']
    list_filter = ['Rating', 'ReviewDate']