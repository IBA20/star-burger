from django import forms
from django.contrib import admin
from django.db.models import Count, Subquery, Case, When, IntegerField
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from django.conf import settings
from .models import (
    Product, ProductCategory, Restaurant, RestaurantMenuItem,
    Order, OrderPosition
)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url
            )

    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
            edit_url=edit_url, src=obj.image.url
            )

    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderPositionInline(admin.TabularInline):
    model = OrderPosition
    extra = 0


class OrderAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        order_products = Product.objects.filter(
            positions__order=self.instance).only('id')

        restaurant_ids = Restaurant.objects.filter(
            menu_items__product__in=Subquery(order_products)
        ).values(
            'id', unavailable=Count(
                Case(
                    When(menu_items__availability=False, then=1),
                    When(menu_items__availability__isnull=True, then=1),
                    output_field=IntegerField()
                )
            )
        ).filter(unavailable=0).values_list('id', flat=True)

        self.fields['performer'].queryset = Restaurant.objects.filter(
            id__in=Subquery(restaurant_ids)
        )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    inlines = [OrderPositionInline]
    list_display = ('firstname', 'lastname', 'phonenumber', 'address')

    def save_model(self, request, obj, form, change):
        """If restaurant selected - change status to APPOINTED"""
        if obj.performer and obj.status == '10':
            obj.status = '20'
        obj.save()

    def save_formset(self, request, form, formset, change):
        """Saves product prices as of the order creation moment"""
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.price = instance.product.price
            instance.save()

    def response_post_save_change(self, request, obj):
        default_response = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            next_url = request.GET['next']
            if url_has_allowed_host_and_scheme(
                next_url, settings.ALLOWED_HOSTS
            ):
                return HttpResponseRedirect(next_url)
        return default_response
