from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum  # Added database aggregates
from .models import Book, Author, Genre, Order, OrderItem, Review, Customer
from .forms import BookSearchForm, ReviewForm

def home(request):
    books = Book.objects.filter(Stock__gt=0)[:8]
    genres = Genre.objects.all()[:6]
    return render(request, 'books/home.html', {
        'books': books,
        'genres': genres
    })

def book_list(request):
    form = BookSearchForm(request.GET or None)
    books = Book.objects.filter(Stock__gt=0)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        genre = form.cleaned_data.get('genre')
        author = form.cleaned_data.get('author')
        
        if query:
            books = books.filter(
                Q(Title__icontains=query) |
                Q(AuthorID__FirstName__icontains=query) |
                Q(AuthorID__LastName__icontains=query)
            )
        if genre:
            books = books.filter(GenreID=genre)
        if author:
            books = books.filter(AuthorID=author)
    
    return render(request, 'books/book_list.html', {
        'books': books,
        'form': form
    })

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = book.reviews.all().order_by('-ReviewDate')
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.BookID = book
            review.CustomerID = request.user.customer
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect('book_detail', book_id=book_id)
    else:
        review_form = ReviewForm()
    
    return render(request, 'books/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'review_form': review_form
    })

def author_list(request):
    authors = Author.objects.all()
    return render(request, 'books/author_list.html', {'authors': authors})

def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    books = Book.objects.filter(AuthorID=author, Stock__gt=0)
    return render(request, 'books/author_detail.html', {
        'author': author,
        'books': books
    })

def genre_list(request):
    genres = Genre.objects.all()
    total_books = Book.objects.count()
    return render(request, 'books/genre_list.html', {
        'genres': genres,
        'total_books': total_books
    })

def genre_books(request, genre_id):
    genre = get_object_or_404(Genre, pk=genre_id)
    books = Book.objects.filter(GenreID=genre, Stock__gt=0)
    
    # Calculate average price for the genre
    try:
        avg_price_result = books.aggregate(avg_price=Avg('Price'))
        avg_price = avg_price_result['avg_price']
        if avg_price:
            avg_price = round(avg_price, 2)
        else:
            avg_price = 12.50
    except:
        avg_price = 12.50
    
    return render(request, 'books/genre_books.html', {
        'genre': genre,
        'books': books,
        'avg_price': avg_price
    })

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    if book.Stock <= 0:
        messages.error(request, 'This book is out of stock.')
        return redirect('book_detail', book_id=book_id)
    
    # Get or create active order for customer
    customer = request.user.customer
    active_order, created = Order.objects.get_or_create(
        CustomerID=customer,
        OrderStatus='pending',
        defaults={'TotalAmount': 0}
    )
    
    # Check if book already in cart
    order_item, created = OrderItem.objects.get_or_create(
        OrderID=active_order,
        BookID=book,
        defaults={
            'Quantity': 1,
            'UnitPrice': book.Price
        }
    )
    
    if not created:
        order_item.Quantity += 1
        order_item.save()
    
    messages.success(request, f'{book.Title} added to cart!')
    return redirect('view_cart')

@login_required
def view_cart(request):
    try:
        order = Order.objects.get(CustomerID=request.user.customer, OrderStatus='pending')
        order_items = order.orderitems.all()
    except Order.DoesNotExist:
        order = None
        order_items = []
    
    return render(request, 'books/cart.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
def update_cart(request, order_item_id):
    order_item = get_object_or_404(OrderItem, pk=order_item_id, OrderID__CustomerID=request.user.customer)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            order_item.delete()
            messages.success(request, 'Item removed from cart.')
        else:
            order_item.Quantity = quantity
            order_item.save()
            messages.success(request, 'Cart updated successfully.')
    
    return redirect('view_cart')

@login_required
def checkout(request):
    try:
        order = Order.objects.get(CustomerID=request.user.customer, OrderStatus='pending')
        order_items = order.orderitems.all()
        
        if not order_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('view_cart')
        
        # Check stock availability
        for item in order_items:
            if item.Quantity > item.BookID.Stock:
                messages.error(request, f'Not enough stock for {item.BookID.Title}. Only {item.BookID.Stock} available.')
                return redirect('view_cart')
        
        # Update stock and complete order
        for item in order_items:
            book = item.BookID
            book.Stock -= item.Quantity
            book.save()
        
        order.OrderStatus = 'processing'
        order.save()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_history')
        
    except Order.DoesNotExist:
        messages.error(request, 'No active order found.')
        return redirect('view_cart')

@login_required
def order_history(request):
    orders = Order.objects.filter(CustomerID=request.user.customer).exclude(OrderStatus='pending').order_by('-OrderDate')
    
    # Annotate each order with item count for display
    for order in orders:
        order.item_count = order.orderitems.count()
    
    return render(request, 'books/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    """
    View to show details of a specific order
    """
    order = get_object_or_404(
        Order, 
        OrderID=order_id, 
        CustomerID=request.user.customer
    )
    order_items = order.orderitems.all()
    
    return render(request, 'books/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
def cancel_order(request, order_id):
    """
    View to cancel an order with enhanced validation
    """
    order = get_object_or_404(
        Order, 
        OrderID=order_id, 
        CustomerID=request.user.customer
    )
    
    # Check if order can be cancelled
    cancellable_statuses = ['pending', 'processing']
    
    if order.OrderStatus in cancellable_statuses:
        try:
            # Restore stock for each item in the order
            for item in order.orderitems.all():
                book = item.BookID
                book.Stock += item.Quantity
                book.save()
            
            # Update order status to cancelled
            order.OrderStatus = 'cancelled'
            order.save()
            
            messages.success(request, f'Order #{order.OrderID} has been cancelled successfully.')
            
        except Exception as e:
            messages.error(request, f'An error occurred while cancelling the order: {str(e)}')
            
    else:
        status_display = dict(Order.ORDER_STATUS).get(order.OrderStatus, order.OrderStatus)
        messages.error(request, f'Orders with status "{status_display}" cannot be cancelled.')
    
    return redirect('order_detail', order_id=order_id)

def register(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        
        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return render(request, 'books/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'books/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'books/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create customer profile
            customer = Customer.objects.create(
                user=user,
                FirstName=first_name,
                LastName=last_name,
                Email=email,
                Phone=phone,
                Address=address,
                City=city,
                State=state,
                ZipCode=zip_code
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome to BookStore, {first_name}!')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, 'books/register.html')
    
    else:
        # GET request - show empty form
        return render(request, 'books/register.html')