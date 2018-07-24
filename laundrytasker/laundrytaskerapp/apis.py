import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from laundrytaskerapp.models import Laundromat, Service, Order, OrderDetails, Driver
from laundrytaskerapp.serializers import LaundromatSerializer, ServiceSerializer, OrderSerializer

import stripe
from laundrytasker.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

def customer_get_laundromats(request):
    laundromats = LaundromatSerializer(
        Laundromat.objects.all().order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"laundromats": laundromats})

def customer_get_services(request, laundromat_id):
    services = ServiceSerializer(
        Service.objects.filter(laundromat_id = laundromat_id).order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"services": services})

@csrf_exempt
def customer_add_order(request):
    """
        params:
            access_token
            laundromat_id
            address
            order_details (json format), example:
                [{"service_id": 1, "quantity": 2},{"service_id": 2, "quantity": 3}]
            stripe_token

        return:
            {"status": "success"}
    """

    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        # Get profile
        customer = access_token.user.customer

        # Get Stripe Token
        stripe_token = request.POST["stripe_token"]

        # Check whether customer has any order that is not delivered
        if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
            return JsonResponse({"status": "failed", "error": "Your last order must be completed."})

        # Check Address
        if not request.POST["address"]:
            return JsonResponse({"status": "failed", "error": "Address is required."})

        # Get Order Details
        order_details = json.loads(request.POST["order_details"])

        order_total = 0
        for service in order_details:
            order_total += Service.objects.get(id = service["service_id"]).price * service["quantity"]

        if len(order_details) > 0:
            # Create a charge: Charge Customer Card
            charge = stripe.charge.create(
                amount = order_total * 100, #Amount in cents
                currency = "usd",
                source = stripe_token,
                description = "Chute Laundry Order"
            )

            if charge.status != "failed":
                # Step 1 - Create an Order
                order = Order.objects.create(
                    customer = customer,
                    laundromat_id = request.POST["laundromat_id"],
                    total = order_total,
                    status = Order.CLEANING,
                    address = request.POST["address"]
                )

                # Step 2 - Create Order details
                for service in order_details:
                    OrderDetails.objects.create(
                        order = order,
                        service_id = service["service_id"],
                        quantity = service["quantity"],
                        sub_total = Service.objects.get(id = service["service_id"]).price * service["quantity"]
                    )

                return JsonResponse({"status": "success"})

            else:
                return JsonResponse({"status": "failed", "error": "Failed connect to stripe."})


def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer = customer).last()).data

    return JsonResponse({"order": order})

def customer_driver_location(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    customer = access_token.user.customer

    current_order = Order.objects.filter(customer = customer, status = Order.ONTHEWAY).last()
    location = current_order.driver.location


    return JsonResponse({"location": location})


def laundromat_order_notification(request, last_request_time):
    notification = Order.objects.filter(laundromat = request.user.laundromat,
        created_at__gt = last_request_time).count()

    return JsonResponse({"notification": notification})



def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filer(status = Order.READY, driver = None).order_by("-id"),
        many = True
    ).data
    return JsonResponse({"orders": orders})

@csrf_exempt
def driver_pick_order(request):

    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        driver = access_token.driver

        if Order.objects.filter(driver = driver).exclude(status = Order.ONTHEWAY):
            return JsonResponse({"status": "failed", "error": "You can only pick one order at a time"})

        try:
            order = Order.objects.get(
                id = request.POST["order_id"],
                driver = None,
                status = Order.READY
            )
            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked = Order.timezone.now()
            order.save()

            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"status": "This order has been picked up by another driver"})


def driver_get_latest_order(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    driver = access_token.user.driver
    order = OrderSerializer(
        Order.objects.filter(driver = driver).order_by("picked_at").last()
    ).data

    return JsonResponse({})

@csrf_exempt
def driver_complete_order(request):
    access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
        expires__gt = timezone.now())

    driver = access_token.user.driver

    order = Order.objects.get(id = request.POST["order_id"], driver = driver)
    order.status = Order.DELIVERED
    order.save()


    return JsonResponse({"status": "success"})


def driver_get_revenue(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    driver = access_token.driver

    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday)]

    for day in current_weekdays:
        orders = Order.objects.fiter(
            driver = driver,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        revenue[day.strftime("%a")] = sum(order.total for order in orders)

    return JsonResponse({"revenue": revenue})

@csrf_exempt
def driver_update_location(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        driver = access_token.driver

        driver.location = request.POST["location"]
        driver.save()

        return JsonResponse({"status": "success"})
