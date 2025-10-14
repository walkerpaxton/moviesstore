from django.contrib import admin
from django.db.models import Count, Sum
from .models import Order, Item

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    readonly_fields = ('movie', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'date', 'movie_count', 'total_movies_purchased')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('id', 'date')
    inlines = [ItemInline]
    
    def movie_count(self, obj):
        """Display the number of different movies in this order"""
        return obj.item_set.aggregate(count=Count('movie'))['count']
    movie_count.short_description = 'Movies in Order'
    
    def total_movies_purchased(self, obj):
        """Display total quantity of movies purchased in this order"""
        return obj.item_set.aggregate(total=Sum('quantity'))['total'] or 0
    total_movies_purchased.short_description = 'Total Movies'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie', 'order', 'user', 'price', 'quantity', 'total_price')
    list_filter = ('movie', 'order__date')
    search_fields = ('movie__name', 'order__user__username')
    
    def user(self, obj):
        """Display the user who made the purchase"""
        return obj.order.user.username
    user.short_description = 'User'
    
    def total_price(self, obj):
        """Display total price for this item"""
        return obj.price * obj.quantity
    total_price.short_description = 'Total Price'