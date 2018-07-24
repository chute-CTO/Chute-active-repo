from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from laundrytaskerapp.forms import UserForm, LaundromatForm, UserFormForEdit, ServiceForm
from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User
from laundrytaskerapp.models import Service, Order, Driver

from django.db.models import Sum, Count, Case, When

# Create your views here.
def home(request):
    return redirect(laundromat_home)

@login_required(login_url='/laundromat/sign-in/')
def laundromat_home(request):
    return redirect(laundromat_order)

@login_required(login_url='/laundromat/sign-in/')
def laundromat_account(request):
    user_form = UserFormForEdit(instance = request.user)
    laundromat_form = LaundromatForm(instance = request.user.laundromat)

    if request.method == 'POST':
        user_form = UserFormForEdit(request.POST, instance = request.user)
        laundromat_form = LaundromatForm(request.POST, request.FILES, instance = request.user.laundromat)

        if user_form.is_valid() and laundromat_form.is_valid():
            user_form.save()
            laundromat.save()

    return render(request, 'laundromat/account.html', {
        "user_form": user_form,
        "laundromat": laundromat_form
    })

@login_required(login_url='/laundromat/sign-in/')
def laundromat_service(request):
    services = Service.objects.filter(laundromat = request.user.laundromat).order_by("-id")
    return render(request, 'laundromat/service.html', {"services": services})

@login_required(login_url='/laundromat/sign-in/')
def laundromat_add_service(request):
    form = ServiceForm()

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)

        if form.is_valid():
            service = form.save(commit=False)
            service.laundromat = request.user.laundromat
            service.save()
            return redirect(laundromat_service)

    return render(request, 'laundromat/add_service.html', {
        "form": form
    })

@login_required(login_url='/laundromat/sign-in/')
def laundromat_edit_service(request, service_id):
    form = ServiceForm(instance = Service.objects.get(id = service_id))

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES, instance = Service.objects.get(id = service_id))

        if form.is_valid():
            form.save()
            return redirect(laundromat_service)

    return render(request, 'laundromat/edit_service.html', {
        "form": form
    })
@login_required(login_url='/laundromat/sign-in/')
def laundromat_order(request):
    if request.method == "POST":
        order = Order.objects.get(id = request.POST["id"], laundromat = request.user.laundromat)

        if order.status == Order.CLEANING:
            order.status = Order.READY
            order.save()
    orders = Order.objects.filter(laundromat = request.user.laundromat).order_by("-id")
    return render(request, 'laundromat/order.html', {"orders": orders})

@login_required(login_url='/laundromat/sign-in/')
def laundromat_report(request):
    from datetime import datetime, timedelta

    revenue = []
    orders = []

    today = datetime.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        delivered_orders = Order.objects.filter(
            laundromat = request.user.laundromat,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )
        revenue.append(sum(order.total for order in delivered_orders))
        orders.append(delivered_orders.count())

    top3_services = Service.objects.filter(laundromat = request.user.laundromat).annotate(total_order = Sum('orderdetails__quantity')).order_by("-total_order")[:3]

    service = {
        "labels": [service.name for service in top3_services],
        "data": [service.total_order or 0 for service in top3_services]
    }

    top3_drivers = Driver.objects.annotate(
        total_order = Count(
            Case (
                When(order__laundromat = request.user.laundromat, then = 1)
            )
        )
    ).order_by("-total_order")[:3]

    driver = {
        "labels": [driver.user.get_full_name() for driver in top3_drivers],
        "data": [driver.total_order for driver in top3_drivers]
    }

    return render(request, 'laundromat/report.html', {
        "revenue": revenue,
        "orders": orders,
        "service": service,
        "driver": driver
    })

def laundromat_sign_up(request):
    user_form = UserForm()
    laundromat_form = LaundromatForm()

    if request.method == "POST":
        user_form = UserForm(request.POST)
        laundromat_form = LaundromatForm(request.POST, request.FILES)

        if user_form.is_valid() and laundromat_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            new_laundromat = laundromat_form.save(commit=False)
            new_laundromat.user = new_user
            new_laundromat.save()

            login(request, authenticate(
                username = user_form.cleaned_data["username"],
                password = user_form.cleaned_data["password"]
            ))

            return redirect(laundromat_home)

    return render(request, "laundromat/sign_up.html", {
        "user_form": user_form,
        "laundromat_form": laundromat_form
    })
