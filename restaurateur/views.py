from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import (Product, Restaurant, Order)
from location.geofunctions import get_coordinates, get_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Укажите имя пользователя'
            }
        )
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль'
            }
        )
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(
            request, "login.html", context={
                'form': form
            }
            )

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request, "login.html", context={
                'form': form,
                'ivalid': True,
            }
            )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in
                        product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for
                                restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(
        request, template_name="products_list.html", context={
            'products_with_restaurant_availability': products_with_restaurant_availability,
            'restaurants': restaurants,
        }
        )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(
        request, template_name="restaurants_list.html", context={
            'restaurants': Restaurant.objects.all(),
        }
        )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    restaurants = Restaurant.objects.prefetch_related('menu_items')

    restaurants_with_availability = {}
    for restaurant in restaurants:
        restaurants_with_availability[restaurant] = [
            item.product_id for item in restaurant.menu_items.all()
            if item.availability]

    active_orders = Order.objects \
        .filter(status__in=['10', '20', '30', '40']) \
        .prefetch_related('products') \
        .prefetch_related('restaurant') \
        .order_by('status') \
        .fetch_with_total()

    for order in active_orders:
        order.possible_restaurants = []
        if not order.restaurant:
            order_location = get_coordinates(order.address)
            if not order_location:
                order.error = 'Ошибка геолокации'
            else:
                for restaurant in restaurants:
                    if all(
                        [product.product_id in restaurants_with_availability[
                            restaurant]
                         for product in order.products.all()]
                    ):
                        restaurant_location = get_coordinates(restaurant.address)
                        distance = round(get_distance(
                            order_location, restaurant_location
                            ), 2)
                        order.possible_restaurants.append(
                            (distance, restaurant.name)
                            )
                order.possible_restaurants.sort()

    return render(
        request, template_name='order_items.html', context={
            'active_orders': active_orders,
            'opts': Order._meta,
        }
    )
