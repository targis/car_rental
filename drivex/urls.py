from django.urls import path, include
from . import views

app_name = 'drivex'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('car/list', views.car_filter_view, name='car-list'),
    path('car/<int:pk>', views.CarDetailView.as_view(), name='car-detail'),

    path('brand/list', views.BrandListView.as_view(), name='brand-list'),
    path('brand/<int:pk>', views.BrandDetailView.as_view(), name='brand-detail'),

    path('user/register', views.register_request, name='user-register'),
    path('user/login', views.login_request, name='user-login'),
    path('user/logout', views.logout_request, name='user-logout'),
    path('user/profile', views.update_profile, name='user-profile'),

    path('order/new/<int:pk>', views.new_order, name='new-order'),
    path('order/list', views.OrderListView.as_view(), name='order-list'),

    path('review/<int:car_pk>/add', views.add_review, name='add-review'),
    path('review/<int:car_pk>/update', views.update_review, name='update-review'),

    # path('rating/<int:car_pk>/add', views.add_car_rating, name='add-rating'),

    path('favorite/<int:car_pk>/add', views.toggle_car_favorite, name='toggle-favorite'),
    path('profile/favorites', views.favorite_list_view, name='profile-favorites'),
    path('profile/reviews', views.ReviewListView.as_view(), name='profile-reviews'),

    path('search', views.search, name='search'),

    path('api/cars', views.CarListAPIView.as_view())
]

