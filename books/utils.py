from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_confirmation_email(order, order_items):
    """
    Send order confirmation email to customer
    """
    try:
        customer = order.CustomerID
        subject = f"Order Confirmation - #{order.OrderID}"
        
        # Prepare context for email template
        context = {
            'order': order,
            'order_items': order_items,
            'customer': customer,
            'total_items': sum(item.Quantity for item in order_items),
            'site_name': 'BookHub',
            'support_email': 'support@bookhub.com'
        }
        
        # Render HTML email template
        html_content = render_to_string('books/emails/order_confirmation.html', context)
        text_content = strip_tags(html_content)  # Strip HTML for plain text version
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer.Email],
            reply_to=['support@bookhub.com']
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_order_status_update_email(order, order_items, status_message):
    """
    Send order status update email
    """
    try:
        customer = order.CustomerID
        subject = f"Order Update - #{order.OrderID}"
        
        context = {
            'order': order,
            'order_items': order_items,
            'customer': customer,
            'status_message': status_message,
            'site_name': 'BookHub'
        }
        
        html_content = render_to_string('books/emails/order_status_update.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer.Email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
        
    except Exception as e:
        print(f"Error sending status email: {e}")
        return False