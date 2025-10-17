from .models import Order, Genre



def cart_count(request):
    if request.user.is_authenticated:
        try:
            # Get pending order for the user
            pending_order = request.user.customer.order_set.filter(OrderStatus='pending').first()
            if pending_order:
                cart_count = pending_order.orderitems.count()
            else:
                cart_count = 0
        except:
            cart_count = 0
    else:
        cart_count = 0
    
    return {'cart_count': cart_count}

def store_context(request):
    """
    Context processor for store-wide data
    """
    context = {}
    
    # Cart count
    cart_count = 0
    if request.user.is_authenticated:
        try:
            pending_order = Order.objects.filter(
                CustomerID=request.user.customer,
                OrderStatus='pending'
            ).first()
            if pending_order:
                cart_count = pending_order.orderitems.count()
        except:
            cart_count = 0
    context['cart_count'] = cart_count
    
    # Genres for navigation (optional)
    context['all_genres'] = Genre.objects.all()[:10]
    
    return context