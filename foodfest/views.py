from contextlib import ContextDecorator
from django.shortcuts import render,redirect
from django.http import HttpResponse
from . models import OrderPost, Product, PersonDetails,PaymentDetails,Profile
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from instamojo_wrapper import Instamojo
from django.conf import settings
from . my_captcha import *
from .helpers import send_forgot_password_mail
import uuid
from django.contrib import messages 
from django.contrib.auth.decorators import login_required


api = Instamojo(api_key=settings.API_KEY,
    auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/'
)


# Create your views here.
def index(request):
    food=Product.objects.all()
    context={'food':food}
    return render(request,'foodfest/index.html',context)

@login_required(login_url='signin')
def fooddesk(request,id):
    food=Product.objects.filter(id=id).first()   
    context={'food':food}
    return render(request,'foodfest/fooddesk.html',context)

@login_required(login_url='signin')
def yourorders(request,id):
    food=Product.objects.filter(id=id).first()
    name=food.name
    price=food.price
    user=request.user
    foodpost=OrderPost(order_name=name,order_price=price,user=user)
    foodpost.save()
    return redirect('index')

@login_required(login_url='signin')
def yourwishlist(request):
    if request.user.is_authenticated:
        user=request.user
        food=OrderPost.objects.filter(user=user)
        cost=0
        for f in food:
            cost=cost+f.order_price
        context={'food':food,'cost':cost}
        return render(request,'foodfest/yourorders.html',context)


def register(request):

    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        flag=request.POST.get('g-recaptcha-response')
        print(flag)
        if flag=="":
            context={'msg':'Recaptcha not verified','captcha':FormWithCaptcha}
            return render(request,'foodfest/register.html',context)
        if User.objects.filter(username=username):
            context={'msg':'Username already exists','captcha':FormWithCaptcha}
            return render(request,'foodfest/register.html',context)

        if User.objects.filter(email=email):
            context={'msg':'Email already exists','captcha':FormWithCaptcha}
            return render(request,'foodfest/register.html',context)

        user = User.objects.create_user(username, email, password)
        user.save()
        # context={'msg':'Account created'}
        messages.success(request, "Account created Successfully")
        return redirect('signin')
    context={'captcha':FormWithCaptcha}
    return render(request, "foodfest/register.html",context)


def signin(request):
    if request.method == 'POST':
        flag=request.POST.get('g-recaptcha-response')
        print(flag)
        if flag=="":
            context={'msg':'Recaptcha not verified','captcha':FormWithCaptcha}
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            context={'msg':'User Not identified','captcha':FormWithCaptcha}
            return render(request,'foodfest/signin.html',context)
    context={'captcha':FormWithCaptcha}
    return render(request,'foodfest/signin.html',context)

@login_required(login_url='signin')
def signout(request):
    logout(request)
    context={'msg':"Successfully logged out"}
    messages.success(request, "Successfully logged out")
    return redirect('index')
  

def search(request):

    query=request.GET['query']
    if len(query)>78:
        allPosts=Product.objects.none()
    else:
        allPostsTitle= Product.objects.filter(name__icontains=query)
        # allPostsAuthor= USERBLOG.objects.filter(author__icontains=query)
        allPostsdescription =Product.objects.filter(desc__icontains=query)
        allPostscat =Product.objects.filter(category__icontains=query)
        allPosts=  allPostsTitle.union(allPostsdescription,allPostscat)
        # return render(request, 'iblog/search.html')
    if allPosts.count()==0:
        context = {'msg':"No search result found",'query':query}
        return render(request, 'foodfest/search.html', context)

    params={'allPosts': allPosts, 'query': query}
    return render(request, 'foodfest/search.html', params)

@login_required(login_url='signin')
def deleteorder(request,order_id):
    food=OrderPost.objects.filter(order_id=order_id).first()
    food.delete()
    return redirect('yourwishlist')



def persondetails(request):
    if request.method=="POST":
        if request.user.is_authenticated:
            global person_name
            person_name=request.POST['name']
            phone=request.POST['mobile']
            address=request.POST['address']
            postal=request.POST['postal']
            user=request.user
            food=OrderPost.objects.filter(user=user)
            global cost
            cost=0
            for f in food:
                cost=cost+f.order_price

            details=PersonDetails(person_name=person_name,phone=phone,address=address,postal=postal,price=cost,user=user)
            details.save()
            
           
            messages.success(request, "Your order have been successfully placed")
            return redirect('payment')
    else:
        return HttpResponse("cannot submit")


def payment(request):
    user = request.user
    try:
        global cost
        global person_name
        print(cost)
        user=request.user
        mail = User.objects.filter(username=user).first()
        mail1=mail.email
        response = api.payment_request_create(

            amount=cost,
            purpose='Order Process for your food delivery',
            buyer_name=person_name,
            email=mail1,
            redirect_url='https://127.0.0.1:8000/order_success'
        )
        print(response)
        
        
        print(mail1)
        cart_id = response['payment_request']['id']
        payment= PaymentDetails(payid=cart_id, payuser=person_name, payemail=mail1, payaccount= user)
        payment.save()
        orders=OrderPost.objects.filter(user=user)
        for order in orders:
            order.delete()

        context={"url":response['payment_request']['longurl']}
        return render(request, "foodfest/payment.html", context)
    except Exception as e:
        return HttpResponse("error")


def order_success(request):
    return render(request, "foodfest/order_success.html")

def forgotpassword(request):

    if request.method=="POST":
        username=request.POST['name']
        
        
        if User.objects.filter(username=username).first():
            user = User.objects.get(username=username)
            # print(user)
            user_obj=user.email
            # print(user_obj)
            token=str(uuid.uuid4())
            # print(token)
            profile = Profile(user=user)
            profile.forgot_password_token=token
            profile.save()
            send_forgot_password_mail(user_obj,token)
            context={"msg":"Email has been sent"}
            return render(request, 'foodfest/forgotpassword.html', context)
        else:
           
            messages.error(request,"User does not exist")
            return redirect( '/forgotpassword')

    return render(request, "foodfest/forgotpassword.html")

def changepassword(request,token):

    profile = Profile.objects.filter(forgot_password_token=token).first()
    if request.method=="POST":
        new_password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        user_id = request.POST['user_id']

        if user_id is None:
            return redirect(f"/changepassword/{token}")

        if new_password!=confirm_password:
            messages.error(request,"Both password should be same")
            return redirect(f"/changepassword/{token}")

        user_obj = User.objects.get(id=user_id)
        user_obj.set_password(new_password)
        user_obj.save()
        return redirect('signin')
        
    context = {"user_id":profile.user.id}
    print(profile)
    
    return render(request, "foodfest/changepassword.html", context)


