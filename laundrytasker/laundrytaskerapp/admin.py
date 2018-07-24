from django.contrib import admin

# Register your models here.
from laundrytaskerapp.models import Laundromat, Customer, Driver, Service, Order, OrderDetails

admin.site.register(Laundromat)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Service)
admin.site.register(Order)
admin.site.register(OrderDetails)
