from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


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
    def orders_with_total(self):
        return self.annotate(
            total=Sum(F('products__quantity') * F('products__price'))
        ).order_by('id')


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        NEW = 'NW', _('Новый')
        APPOINTED = 'AP', _('Распределен')
        PREPARING = 'PR', _('Приготовление')
        DELIVERY = 'DL', _('Доставка'),
        COMPLETED = 'CP', _('Исполнен')
        CANCELLED = 'CN', _('Отменен')

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
    comments = models.TextField('Комментарии', max_length=256, blank=True)
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
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='Ресторан',
        null=True,
        blank=True,
    )

    orders = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}, {self.address}'


class OrderPosition(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_positions',
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
