from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path('create/',views.order_create,name='order_create'),
    path('admin/order/<int:order_id>/',views.admin_order_detail,name='admin_order_detail'),
    path('admin/order/<int:order_id>/pdf',views.render_to_print_pdf_view,name='admin_order_pdf'),


]