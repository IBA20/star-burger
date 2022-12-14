from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, F, Subquery, Count, Case, When, IntegerField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class RestaurantQuerySet(models.QuerySet):
    def get_available_for_order(self, order):
        order_products = Product.objects.filter(
            positions__order=order
        ).only('id')

        restaurant_ids = RestaurantMenuItem.objects.filter(
            product__in=Subquery(order_products)
        ).values(
            'restaurant'
        ).annotate(
            unavailable=Count(
                Case(
                    When(availability=False, then=1),
                    When(availability__isnull=True, then=1),
                    output_field=IntegerField()
                )
            )
        ).filter(unavailable=0).values_list('restaurant', flat=True)

        return self.filter(
            id__in=Subquery(restaurant_ids)
        )


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    objects = RestaurantQuerySet.as_manager()

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def fetch_with_total(self):
        return self.annotate(
            total=Sum(F('positions__quantity') * F('positions__price'))
        )


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        NEW = '10', _('Новый')
        APPOINTED = '20', _('Распределен')
        PREPARING = '30', _('Приготовление')
        DELIVERY = '40', _('Доставка'),
        COMPLETED = '50', _('Исполнен')
        CANCELLED = '90', _('Отменен')

    class PaymentMethod(models.TextChoices):
        CASH = 'CS', _('Наличными при получении')
        CARD = 'CD', _('Картой на сайте')
        ELECTRONICALLY = 'EL', _('Электронно')

    firstname = models.CharField('Имя', max_length=50, db_index=True)
    lastname = models.CharField('Фамилия', max_length=50, db_index=True)
    phonenumber = PhoneNumberField(
        'Телефон',
        db_index=True,
    )
    address = models.CharField('Адрес', max_length=100, db_index=True)
    status = models.CharField(
        'Статус',
        max_length=2,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        db_index=True
    )
    comments = models.TextField('Комментарии', blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    called_at = models.DateTimeField(null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True, db_index=True)
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=2,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        db_index=True
    )
    performer = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='Ресторан',
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}, {self.address}'


class OrderPosition(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='продукт',
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1), MaxValueValidator(99)],
    )
    price = models.DecimalField(
        'цена',
        blank=True,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
