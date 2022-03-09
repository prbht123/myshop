from django.shortcuts import render,redirect,get_object_or_404
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required

from .models import Order
from django.template.loader import render_to_string
import weasyprint
from django.conf import settings
from django.http import HttpResponse
import os,io
from django.template.loader import get_template
from django.template import loader
import pdfkit
import base64
# Create your views here.


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,product=item['product'],price=item['price'],quantity=item['quantity'])
            # clear the cart
        cart.clear()
        # launch asynchronous task
        #pp=order_created.delay(order.id)
        #return render(request,'orders/order/created.html',{'order': order})
        # set the order in the session
        request.session['order_id'] = order.id # redirect to the payment
        return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request,'orders/order/create.html',{'cart': cart, 'form': form})



@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,'orders/order/detail.html',{'order': order})


def render_to_print_pdf_view(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, id=order.id)
    data = order.__dict__ 
    data['get_cost']=order_item.get_cost()
    data['price']=order_item.price
    data['quantity']=order_item.quantity
    data['product_name'] = order_item.product.name
    template = get_template("orders/order/pdf.html")
    name=str(order.id)+"_invoice.pdf"
    name = '_'.join(name.split())
    order=order.__dict__
    html = template.render(data)
    pdffile_content = loader.get_template("orders/order/pdf.html").render(data)
    
    pdfkit.from_string(html,name)
    with open(name, 'rb') as file:
        encoded = base64.b64encode(file.read())
    pdf =io.BytesIO(base64.decodebytes(encoded))
    response = HttpResponse(pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename = %s' %name
    os.remove(name)
    return response
