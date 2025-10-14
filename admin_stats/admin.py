from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from cart.models import Order, Item

# Create a custom model for the purchase statistics
from django.db import models

class PurchaseStats(models.Model):
    """Dummy model to represent purchase statistics in admin"""
    class Meta:
        app_label = 'admin_stats'
        verbose_name = 'Purchase Statistics'
        verbose_name_plural = 'Purchase Statistics'
        managed = False  # This tells Django not to create a database table

# Custom admin class for purchase statistics
class PurchaseStatsAdmin(admin.ModelAdmin):
    """Custom admin for purchase statistics"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view that shows top purchasers"""
        # Get users with their purchase statistics
        top_purchasers = User.objects.annotate(
            total_orders=Count('order'),
            total_movies_purchased=Sum('order__item__quantity'),
            total_spent=Sum('order__total')
        ).filter(total_movies_purchased__gt=0).order_by('-total_movies_purchased')
        
        # Get additional statistics
        total_users_with_purchases = top_purchasers.count()
        total_movies_sold = Item.objects.aggregate(total=Sum('quantity'))['total'] or 0
        total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
        
        context = {
            'title': 'Top Movie Purchasers',
            'top_purchasers': top_purchasers[:20],  # Top 20 purchasers
            'total_users_with_purchases': total_users_with_purchases,
            'total_movies_sold': total_movies_sold,
            'total_revenue': total_revenue,
            'has_permission': True,
            'opts': PurchaseStats._meta,
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
        }
        
        return render(request, 'admin/top_purchasers.html', context)

# Override the default admin site to add custom URLs and register our custom admin
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('purchase-stats/', self.admin_view(self.purchase_stats_view), name='purchase_stats'),
        ]
        return custom_urls + urls
    
    def purchase_stats_view(self, request):
        """Custom admin view to show purchase statistics"""
        # Get users with their purchase statistics
        top_purchasers = User.objects.annotate(
            total_orders=Count('order'),
            total_movies_purchased=Sum('order__item__quantity'),
            total_spent=Sum('order__total')
        ).filter(total_movies_purchased__gt=0).order_by('-total_movies_purchased')
        
        # Get additional statistics
        total_users_with_purchases = top_purchasers.count()
        total_movies_sold = Item.objects.aggregate(total=Sum('quantity'))['total'] or 0
        total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
        
        context = {
            'title': 'Top Movie Purchasers',
            'top_purchasers': top_purchasers[:20],  # Top 20 purchasers
            'total_users_with_purchases': total_users_with_purchases,
            'total_movies_sold': total_movies_sold,
            'total_revenue': total_revenue,
            'has_permission': True,
            'opts': PurchaseStats._meta,
            'site_title': self.site_title,
            'site_header': self.site_header,
        }
        
        return render(request, 'admin/top_purchasers.html', context)

# Replace the default admin site
admin.site.__class__ = CustomAdminSite

# Register the purchase stats admin
admin.site.register(PurchaseStats, PurchaseStatsAdmin)