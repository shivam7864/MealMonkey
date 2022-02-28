from django.contrib import admin
from django.urls import path,include

from .import views

urlpatterns = [
    path('', views.index,name='index'),
    path('fooddesk/<id>', views.fooddesk,name='fooddesk'),
    path('yourorders/<id>', views.yourorders,name='yourorders'),
    path('deleteorder/<order_id>', views.deleteorder,name='deleteorder'),
    path('yourwishlist', views.yourwishlist,name='yourwishlist'),
    path('signin', views.signin,name='signin'),
    path('signout', views.signout,name='signout'),
    path('register', views.register, name='register'),
    path('search', views.search, name='search'),
    path('persondetails', views.persondetails, name='persondetails'),
    path('payment', views.payment, name="payment"),
    path('order_success', views.order_success, name="order_success"),
    path('forgotpassword', views.forgotpassword, name="forgotpassword"),
    path('changepassword/<token>', views.changepassword, name="changepassword"),
   
]