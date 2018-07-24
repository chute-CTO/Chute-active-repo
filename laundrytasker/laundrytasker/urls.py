from django.conf.urls import url
from django.contrib import admin

from laundrytaskerapp import views, apis
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),

    # Laundromat
    url(r'^laundromat/sign-in/$', auth_views.login,
        {'template_name': 'laundromat/sign_in.html'},
        name = 'laundromat-sign-in'),
    url(r'^laundromat/sign-out', auth_views.logout,
        {'next_page': '/'},
        name = 'laundromat-sign-out'),
    url(r'^laundromat/sign-up', views.laundromat_sign_up,
        name = 'laundromat-sign-up'),
    url(r'^laundromat/$', views.laundromat_home, name = 'laundromat-home'),

    url(r'^laundromat/account/$', views.laundromat_account, name = 'laundromat-account'),
    url(r'^laundromat/service/$', views.laundromat_service, name = 'laundromat-service'),
    url(r'^laundromat/service/add/$', views.laundromat_add_service, name = 'laundromat-add-service'),
    url(r'^laundromat/service/edit/(?P<service_id>\d+)/$', views.laundromat_edit_service, name = 'laundromat-edit-service'),
    url(r'^laundromat/order/$', views.laundromat_order, name = 'laundromat-order'),
    url(r'^laundromat/report/$', views.laundromat_report, name = 'laundromat-report'),


    url(r'^api/laundromat/order/notification/(?P<last_request_time>.+)/$', apis.laundromat_order_notification),



    url(r'^api/customer/laundromat/$', apis.customer_get_laundromats),
    url(r'^api/customer/services/(?P<laundromat_id>\d+)/$', apis.customer_get_services),
    url(r'^api/customer/order/add/$', apis.customer_add_order),
    url(r'^api/customer/order/latest/$', apis.customer_get_latest_order),
    url(r'^api/customer/driver/location/$', apis.customer_driver_location),

    url(r'^api/driver/order/ready/$', apis.driver_get_ready_orders),
    url(r'^api/driver/order/pick/$', apis.driver_pick_order),
    url(r'^api/driver/order/latest/$', apis.driver_get_latest_order),
    url(r'^api/driver/order/complete/$', apis.driver_complete_order),
    url(r'^api/driver/revenue/$', apis.driver_get_revenue),
    url(r'^api/driver/location/update/$', apis.driver_update_location),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
