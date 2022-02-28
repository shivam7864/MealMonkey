from django.contrib import admin

from .models import Product
from .models import OrderPost
from .models import PersonDetails,PaymentDetails,Profile

admin.site.register(Product)
admin.site.register(OrderPost)
admin.site.register(PersonDetails)
admin.site.register(PaymentDetails)
admin.site.register(Profile)
