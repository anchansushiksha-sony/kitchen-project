from django.contrib import admin
from .models import Order, OrderItem

""" # CATEGORY ADMIN
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}  # Auto-fill slug

# PRODUCT ADMIN
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_active', 'featured')
    list_filter = ('category', 'is_active', 'featured')
    search_fields = ('name', 'category__name')
    list_editable = ('is_active', 'featured')
    ordering = ('name',)
    list_per_page = 20

# RATING ADMIN
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('product__name', 'user__username')
    ordering = ('-created_at',)
 """


# ORDER AND ITEMS
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_method', 'payment_status', 'order_status', 'created_at')
    list_filter = ('payment_status', 'order_status', 'payment_method')
    search_fields = ('id', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'total_amount', 'created_at')
    inlines = [OrderItemInline]
