from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

# from .models import Car, Brand
from .models import Car, Brand, Profile, Order




class CarTest(TestCase):
    class Meta:
        app_label = "drivex"

    def setUp(self):
        brand1 = Brand.objects.create(name="ZAZ")
        car1 = Car.objects.create(brand=brand1, name="Lanos")
        car2 = Car.objects.create(brand=brand1, name="Sens")
        user1 = User.objects.create(username='jackson', password="123")
        Order.objects.create(car=car1, user=user1, date_start='2023-05-17', date_end='2023-05-21')
        Order.objects.create(car=car1, user=user1, date_start='2023-05-23', date_end='2023-05-24')
        Order.objects.create(car=car1, user=user1, date_start='2023-05-25', date_end='2023-05-27',
                             status=Order.ACTIVE)
        Order.objects.create(car=car1, user=user1, date_start='2023-05-30', date_end='2023-06-05',
                             status=Order.CLOSED)

    def test_car_brands_created_count(self):
        number_of_cars = Car.objects.count()
        self.assertEqual(number_of_cars, 2)
        number_of_brands = Brand.objects.count()
        self.assertEqual(number_of_brands, 1)

    def test_users_and_profiles_count(self):
        number_of_users = User.objects.count()
        self.assertEqual(number_of_users, 1)
        number_of_profiles = Profile.objects.count()
        self.assertEqual(number_of_profiles, 1)

    def test_orders_count(self):
        number_of_orders = Order.objects.count()
        self.assertEqual(number_of_orders, 4)

    def test_user_orders_count(self):
        user = User.objects.get(username__exact='jackson')
        # print(user)
        number_of_user_orders = user.orders.count()
        self.assertEqual(number_of_user_orders, 4)

    def test_orders_statuses(self):
        new_orders = Order.objects.filter(status=Order.NEW).count()
        active_orders = Order.objects.filter(status=Order.ACTIVE).count()
        # for o in Order.objects.filter(status=Order.ACTIVE):
        #     print(o.date_start, '-', o.date_end)
        closed_orders = Order.objects.filter(status=Order.CLOSED).count()
        self.assertEqual(new_orders, 2)
        self.assertEqual(active_orders, 1)
        self.assertEqual(closed_orders, 1)

    def test_car_availability(self):
        car1 = Car.objects.get(name__exact='Lanos')
        self.assertFalse(car1.is_available(from_date='2023-03-01', to_date='2023-05-30'))
        self.assertFalse(car1.is_available(from_date='2023-05-26', to_date='2023-06-10'))
        self.assertFalse(car1.is_available(from_date='2023-05-25', to_date='2023-05-25'))
        self.assertFalse(car1.is_available(from_date='2023-05-26', to_date='2023-05-26'))
        self.assertFalse(car1.is_available(from_date='2023-05-27', to_date='2023-05-27'))
        self.assertTrue(car1.is_available(from_date='2023-05-28', to_date='2023-05-28'))

        car2 = Car.objects.get(name__exact='Sens')
        self.assertTrue(car2.is_available(from_date='2023-05-27', to_date='2023-05-27'))

    def test_order_number(self):
        today = timezone.now().strftime("%Y%m%d")
        order1 = Order.objects.get(pk=1)
        order2 = Order.objects.get(pk=2)
        order3 = Order.objects.get(pk=3)
        order4 = Order.objects.get(pk=4)

        self.assertEqual(order1.number, '20230526-0001')
        self.assertEqual(order2.number, '20230526-0002')
        self.assertEqual(order3.number, '20230526-0003')
        self.assertEqual(order4.number, '20230526-0004')
