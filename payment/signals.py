from django.shortcuts import get_object_or_404
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import os,io
from django.template.loader import get_template
from django.template import loader
import pdfkit
import base64



def payment_notification(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # payment was successful
        order = get_object_or_404(Order, id=ipn_obj.invoice)
        # mark the order as paid
        order.paid = True
        order.save()
        




pp=valid_ipn_received.connect(payment_notification)

