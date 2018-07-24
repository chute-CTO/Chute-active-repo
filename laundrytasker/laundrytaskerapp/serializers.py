from rest_framework import serializers

from laundrytaskerapp.models import Laundromat, Service, Customer, Driver, Order, OrderDetails

class LaundromatSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    def get_logo(self, laundromat):
        request = self.context.get('request')
        logo_url = laundromat.logo.url
        return request.build_absolute_uri(logo_url)

    class Meta:
        model = Laundromat
        fields = ("id", "name", "phone", "address", "logo")

class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, service):
        request = self.context.get('request')
        image_url = service.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = Service
        fields = ("id", "name", "short_description", "image", "price")


class OrderCustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "address")

class OrderDriverSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Driver
        fields = ("id", "name", "avatar", "phone", "address")

class OrderLaudromatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laundromat
        fields = ("id", "name", "phone", "address")

class OrderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "name", "price")

class OrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ("id", "service", "quantity", "subtotal")

class OrderSerializer(serializers.ModelSerializer):
    customer = OrderCustomerSerializer()
    driver = OrderDriverSerializer()
    Laundromat = OrderLaudromatSerializer()
    order_details = OrderDetailsSerializer(many = True)
    status = serializers.ReadOnlyField(source = "get_status_display")

    class Meta:
        model = Order
        fields = ("id", "customer", "laundromat", "driver", "order_details", "total", "status", "address")
