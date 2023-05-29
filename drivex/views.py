from typing import Any, Dict
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Prefetch
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from rest_framework.generics import ListAPIView

from .forms import NewUserForm, UserForm, ProfileForm, OrderForm, ReviewForm
from .models import *
from .filters import *
from .serializers import *


class HomeView(TemplateView):
    template_name = "drivex/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        prefetch = Prefetch("features", queryset=Feature.objects.all())
        if user.is_authenticated:
            favorite_cars = (
                Car.objects.filter(favorites=user)
                .select_related("brand", "category", "badge")
                .prefetch_related(prefetch)
                .annotate(num_reviews=Count("reviews"))[:4]
            )
        else:
            favorite_cars = None
        context.update(
            {
                "brands": Brand.objects.annotate(count=Count("cars"))
                .order_by("name")
                .all(),
                "cars": Car.objects.filter(badge__isnull=False)
                .select_related("brand", "category", "badge")
                .annotate(num_reviews=Count("reviews"))
                .prefetch_related(prefetch)
                .annotate(num_reviews=Count("reviews"))[:4],
                "top_cars": Car.objects.filter(rating__gt=4)
                .order_by("-rating")
                .select_related("brand", "category", "badge")
                .prefetch_related(prefetch)
                .annotate(num_reviews=Count("reviews"))[:4],
                "favorite_cars": favorite_cars,
            }
        )
        return context


def car_filter_view(request):
    per_page = 9
    filter_set = CarFilter(
        request.GET,
        queryset=Car.objects.select_related("brand", "category", "badge")
        .prefetch_related("features")
        .annotate(num_reviews=Count("reviews"))
        .all(),
    )
    filtered_queryset = filter_set.qs

    order_by_field = request.GET.get("order_by")  # Default field to order by
    if order_by_field:
        filtered_queryset = filtered_queryset.order_by(order_by_field)
    else:
        filtered_queryset = filtered_queryset

    paginator = Paginator(filtered_queryset, per_page=per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    filter_parameters = request.GET.copy()

    if "page" in filter_parameters:
        del filter_parameters["page"]

    filter_query_string = filter_parameters.urlencode()

    page_obj.filter_query_string = filter_query_string

    return render(
        request,
        "drivex/car_list.html",
        {"filter_set": filter_set, "page_obj": page_obj},
    )


class CarDetailView(DetailView):
    model = Car
    context_object_name = "car"
    queryset = Car.objects.select_related('brand').prefetch_related('features')

    def get_context_data(self, **kwargs):
        context = super(CarDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                review = Review.objects.get(car=self.object, user=self.request.user)
            except Review.DoesNotExist:
                review = None
            form = ReviewForm()
            if review:
                form.fields["text"].initial = review.text
                context["user_rating"] = review.rate
                context["user_comment"] = review.text
            context["review_form"] = form
        context['reviews'] = Review.objects.filter(car=self.object).select_related('user', 'user__profile')
        return context


class BrandListView(ListView):
    paginate_by = 9
    model = Brand
    context_object_name = "brands"
    # queryset = Brand.objects.select_related('cars').prefetch_related(
    #     "cars_features", "cars_reviews"
    # ).annotate(num_reviews=Count("cars_reviews")).all()


class BrandDetailView(DetailView):
    model = Brand
    context_object_name = "brand"
    # queryset = (
    #     Brand.objects.prefetch_related("cars", "cars__features", "cars__reviews")
    #     .all()
    #     .annotate(num_reviews=Count("cars__reviews"))
    # )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["cars"] = (
            Car.objects.annotate(num_reviews=Count("reviews"))
            .select_related("brand", "category", "badge")
            .prefetch_related("features", 'reviews')
            .filter(brand=self.object)
        )
        return context


class OrderListView(ListView):
    paginate_by = 9
    model = Order
    context_object_name = "orders"


class ReviewListView(ListView):
    model = Review
    context_object_name = "reviews"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            reviews = Review.objects.filter(user=self.request.user)
            context["reviews"] = reviews
        return context


def register_request(request):
    if request.user.is_authenticated:
        return redirect("drivex:home")
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            profile_form = ProfileForm(
                request.POST, request.FILES, instance=user.profile
            )
            if "photo" in profile_form.cleaned_data:
                user.profile.photo = profile_form.cleaned_data.get("photo")
            user.profile.name = profile_form.cleaned_data.get("name")
            user.profile.tel = profile_form.cleaned_data.get("tel")
            user.save()
            raw_password = user_form.cleaned_data.get("password1")
            user = auth.authenticate(username=user.username, password=raw_password)
            auth.login(request, user)
            return redirect("drivex:home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(
        request,
        "drivex/user_register.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


def login_request(request):
    if request.user.is_authenticated:
        return redirect("drivex:home")
    next = request.GET.get("next") or ""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                # messages.info(request, f"You are now logged in as {username}.")
                return HttpResponseRedirect(next)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(
        request=request,
        template_name="drivex/user_login.html",
        context={"login_form": form},
    )


def logout_request(request):
    auth.logout(request)
    return redirect("drivex:home")


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == "POST":
        # user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        profile = request.user.profile
        if profile_form.is_valid():
            # print(request.FILES['photo'])
            # print(profile_form.cleaned_data.get('photo'))
            # profile.photo = request.FILES['photo']

            # profile_form.photo = profile_form.cleaned_data.get('photo')
            # request.user.profile.photo = profile_form.cleaned_data.get('photo')
            profile_form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("drivex:user-profile")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        # user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, "drivex/profile.html", {"profile_form": profile_form})


@login_required
def new_order(request, pk):
    user = request.user
    car = Car.objects.get(pk=pk)
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        if order_form.is_valid() and Car.objects.filter(pk=pk).exists() and user:
            if car.is_available(
                from_date=order_form.data["date_start"],
                to_date=order_form.data["date_end"],
            ):
                order = order_form.save(commit=False)
                order.user = request.user
                order.car = car
                order.save()
                messages.success(
                    request,
                    "Your order was successfully created! We are going to contact you soon!",
                )
                return redirect("drivex:user-profile")
            else:
                messages.warning(
                    request,
                    "Sorry, the car is not available in that period. /"
                    "Try another period or choose another car.",
                )
        else:
            messages.error(request, "Please correct the error below.")
    else:
        order_form = OrderForm()
    return render(request, "drivex/order.html", {"order_form": order_form, "car": car})


@login_required
def add_review(request, car_pk):
    user = request.user
    car = Car.objects.get(pk=car_pk)
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        print(review_form)
        rate = request.POST.get("rate")
        if review_form.is_valid() and rate:
            user_voted = Review.objects.filter(car=car, user=user).exists()
            if not user_voted:
                new_review = review_form.save(commit=False)
                new_review.user = user
                new_review.car = car
                new_review.rate = rate
                new_review.save()
                messages.success(request, "You have successfully added a review!")
        else:
            messages.error(request, "Please fill all required fields.")
    return HttpResponseRedirect(car.url())


@login_required
def update_review(request, car_pk):
    print("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
    user = request.user
    car = Car.objects.get(pk=car_pk)
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        rate = request.POST.get("rate")
        text = request.POST.get("text")
        if review_form.is_valid():
            user_review = Review.objects.get(car=car, user=user)
            if user_review:
                user_review.rate = rate
                user_review.text = text
                user_review.save()
                messages.success(request, "You have successfully updated your review!")
            else:
                messages.error(request, "Review not found")
        else:
            messages.error(request, "Please fill all required fields.")
    return HttpResponseRedirect(car.url())


# def add_car_rating(request, car_pk):
#     car = Car.objects.get(pk=car_pk)
#     user = request.user
#     stars = request.POST.get("stars")
#     # print(car, user, stars)
#     if user and car and stars:
#         is_user_voted = Review.objects.filter(car=car, user=user).exists()
#         if not is_user_voted:
#             Review.objects.create(user=user, car=car, stars=stars)
#     return HttpResponseRedirect(car.url())


@login_required
def toggle_car_favorite(request, car_pk):
    car = Car.objects.get(pk=car_pk)
    user = request.user
    if car.favorites.contains(user):
        car.favorites.remove(user)
    else:
        car.favorites.add(user)
    return HttpResponseRedirect(car.url())


@login_required
def favorite_list_view(request):
    user = request.user
    favorite_cars = Car.objects.filter(favorites=user).all()
    return render(
        request,
        "drivex/favorites.html",
        {"favorite_cars": favorite_cars},
    )


def search(request):
    search_str = request.POST["search"]
    search_category = request.POST["search-category"]
    next = request.POST.get("next")
    if search_str:
        cars = None
        if search_category == "1":
            cars = Car.objects.filter(
                Q(name__icontains=search_str) | Q(brand__name__icontains=search_str)
            ).order_by("name")
        if search_category == "2":
            cars = Car.objects.filter(name__icontains=search_str)
        if search_category == "3":
            cars = Car.objects.filter(brand__name__icontains=search_str)
        return render(
            request,
            template_name="drivex/search_page.html",
            context={"search": search_str, "cars": cars},
        )
    else:
        return HttpResponseRedirect(next)


class CarListAPIView(ListAPIView):
    serializer_class = CarSerializer
    queryset = Car.objects.all()


class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

