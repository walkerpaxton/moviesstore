from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from cart.models import Order

# Unregister the default User admin
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'total_orders', 'total_movies_purchased', 'total_spent')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    def total_orders(self, obj):
        """Display total number of orders for this user"""
        return obj.order_set.count()
    total_orders.short_description = 'Total Orders'
    total_orders.admin_order_field = 'order__count'
    
    def total_movies_purchased(self, obj):
        """Display total number of movies purchased by this user"""
        total = obj.order_set.aggregate(
            total=Sum('item__quantity')
        )['total']
        return total or 0
    total_movies_purchased.short_description = 'Movies Purchased'
    total_movies_purchased.admin_order_field = 'order__item__quantity__sum'
    
    def total_spent(self, obj):
        """Display total amount spent by this user"""
        total = obj.order_set.aggregate(
            total=Sum('total')
        )['total']
        return f"${total or 0}"
    total_spent.short_description = 'Total Spent'
    total_spent.admin_order_field = 'order__total__sum'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations for better performance"""
        return super().get_queryset(request).annotate(
            order_count=Count('order'),
            movies_purchased=Sum('order__item__quantity'),
            money_spent=Sum('order__total')
        )
