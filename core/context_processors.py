    
from .models import Wishlist

def wishlist_count(request):
    """
    Adds 'wishlist_count' to the template context for logged-in users.
    """
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        count = 0
    return {
        'wishlist_count': count
    }






def cart_count(request):
    cart = request.session.get('cart', {})
    return {
        'cart_count': sum(cart.values())
    }
