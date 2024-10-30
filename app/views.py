from unicodedata import category
import requests  # Ensure this import is correct

from django.shortcuts import render, redirect, reverse, get_object_or_404
from pyparsing import empty
from .models import *
from .forms import *
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split
from django.conf import settings  # To access the BASE_DIR from settings.py

from sklearn.ensemble import RandomForestClassifier

# Create your views here.
# views.py
from django.shortcuts import render
import joblib
import numpy as np

# Load the model (ensure the file path is correct)
model = joblib.load(f"{settings.BASE_DIR}/soil_fertility_model.pkl")


def predict_soil_fertility(request):
    prediction = None
    form = SoilFertilityForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Get form data
        soil_ph = form.cleaned_data['soil_ph']
        moisture = form.cleaned_data['moisture']
        nitrogen = form.cleaned_data['nitrogen']
        phosphorus = form.cleaned_data['phosphorus']
        potassium = form.cleaned_data['potassium']
        organic_matter = form.cleaned_data['organic_matter']

        # Prepare input for prediction
        input_data = np.array([[soil_ph, moisture, nitrogen, phosphorus, potassium, organic_matter]])

        # Make prediction
        prediction = model.predict(input_data)[0]

    return render(request, 'visitor/visitor_find_soil_detail.html', {'form': form, 'prediction': prediction})

def predict_sales(request):
    prediction = None

    if request.method == 'POST':
        # Capture form data from POST request
        location = request.POST.get('Location')
        product = request.POST.get('Product')
        season = request.POST.get('Season')
        crop_type = request.POST.get('CropType')
        soil_type = request.POST.get('SoilType')
        weather_condition = request.POST.get('WeatherCondition')

        # Prepare data to send to Flask API
        data = {
            "Location": location,
            "Product": product,
            "Season": season,
            "CropType": crop_type,
            "SoilType": soil_type,
            "WeatherCondition": weather_condition
        }

        # Send POST request to Flask API
        try:
            response = requests.post('http://127.0.0.1:5000/predict', json=data)
            if response.status_code == 200:
                prediction = response.json().get("predicted_sales_volume")
            else:
                prediction = "Error: Could not retrieve prediction."
        except requests.exceptions.RequestException as e:
            prediction = f"Error: {str(e)}"

    # Render form template with prediction result
    return render(request, 'admin/products_prediction.html', {
        'prediction': prediction,
        'locations': ["Tunis", "Sfax", "Sousse", "Gabès", "Kairouan", "Monastir", "Mahdia", "Bizerte", "Nabeul", "Tozeur"],
        'products': ["Urea Fertilizer", "Hybrid Corn Seed", "Drip Irrigation Kit", "NPK Fertilizer", "Organic Compost",
                     "Ammonium Nitrate", "Herbicide", "Water-Soluble Fertilizer", "Mulching Film", "Date Palm Fertilizer"],
        'seasons': ["Spring", "Summer", "Fall", "Winter"],
        'crop_types': ["Wheat", "Corn", "Vegetables", "Olive Trees", "Tomatoes", "Citrus", "Dates", "Strawberries"],
        'soil_types': ["Loamy", "Sandy", "Clay", "Peaty", "Sandy-Loamy", "Arid"],
        'weather_conditions': ["Rainy", "Sunny", "Cold", "Windy", "Hot", "Mild", "Very Hot"],
    })


def predict_best_selling_product(request):
    prediction = None
    form = PredictionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Get form data
        city = form.cleaned_data['city']
        date = form.cleaned_data['date'].strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD

        # Prepare data to send to the Flask API
        data = {
            "City": city,
            "Date": date
        }

        # Send POST request to Flask API
        try:
            response = requests.post('http://127.0.0.1:5000/predict', json=data)
            if response.status_code == 200:
                prediction = response.json().get("best_selling_product")
            else:
                prediction = "Error: Could not retrieve prediction."
        except requests.exceptions.RequestException as e:
            prediction = f"Error: {str(e)}"

    return render(request, 'seller/predict_best_selling_product.html', {'form': form, 'prediction': prediction})
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

#<-----For check user is Admin, Visitor and Officer----->#
def is_admin(user):
    # return user.groups.filter(name='ADMIN').exists()
    return 1 
def is_visitor(user):
    return user.groups.filter(name='VISITOR').exists()

def is_seller(user):
    return user.groups.filter(name='SELLER').exists()

#<-----LogOut For All----->#
def logout_view(request):
    logout(request)
    return redirect('/')

#<-------------------------------------------->#
#<---------------Admin Functions-------------->#
#<-------------------------------------------->#

#<-----Login For Admin----->#
def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            
            user = authenticate(username=username, password=password)
            if user:
                print(user.groups.filter(name='ADMIN'))
                if 1:
                    login(request,user)
                    return redirect('admin_home')
                else:
                    messages.success(request, 'Your account is not found in Admin..')
            else:
                messages.success(request, 'Your Username and Password is Wrong..')
    else:
         form = AdminLoginForm()           
    return render(request, 'admin/admin_login.html',{'form':form})


#<-----Home Page for Admin----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_home(request):
    return render(request, 'admin/admin_home.html')

#<-----Profile Page for Admin----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_profile(request):
    return render(request, 'admin/admin_profile.html')

#<-----Change password----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def change_password_admin(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('admin_home')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'admin/change_password_admin.html', {'form': form})

#<-----Admin Approvall for visitors----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_approve_visitor(request):
    visitors = Visitor.objects.all().filter(status=False)
    return render(request, 'admin/admin_approve_visitor.html',{'visitors':visitors})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def approve_visitor(request):
    visitor=get_object_or_404(Visitor, pk=request.GET.get('visitor_id'))
    visitor.status=True
    visitor.save()
    return redirect(reverse('admin_approve_visitor'))

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_visitor(request):
    visitor=get_object_or_404(Visitor, pk=request.GET.get('visitor_id'))
    user=User.objects.get(id=visitor.user_id)
    user.delete()
    visitor.delete()
    return redirect(reverse('admin_approve_visitor'))

#<-----Admin Approvall for sellers----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_approve_seller(request):
    sellers = Seller.objects.all().filter(status=False)
    return render(request, 'admin/admin_approve_seller.html',{'sellers':sellers})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def detail_seller(request, id):
    sellers = Seller.objects.all().get(id=id)
    data={'sellers':sellers}
    return render(request, 'admin/detail_seller.html',data)

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def approve_seller(request):
    seller=get_object_or_404(Seller, pk=request.GET.get('seller_id'))
    seller.status=True
    seller.save()
    return redirect(reverse('admin_approve_seller'))

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_seller(request):
    seller=get_object_or_404(Seller, pk=request.GET.get('seller_id'))
    user=User.objects.get(id=seller.user_id)
    user.delete()
    seller.delete()
    return redirect(reverse('admin_approve_seller'))


#<-----Admin add Admin----->#
def admin_add_admin(request):
    if request.method=='POST':
        form1=AdminUserForm(request.POST)
        form2=AdminExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_admin_group=Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('admin_active_admin')
    else:
        form1=AdminUserForm()
        form2=AdminExtraForm()
    return render(request, 'admin/admin_add_admin.html',{'form1':form1,'form2':form2})

#<-----Active Admin View for Admin----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_active_admin(request):
    admins = Admin.objects.all()
    return render(request, 'admin/admin_active_admin.html',{'admins':admins})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_admin_active(request):
    admin=get_object_or_404(Admin, pk=request.GET.get('admin_id'))
    user=User.objects.get(id=admin.user_id)
    user.delete()
    admin.delete()
    return redirect(reverse('admin_active_admin'))

#<-----Active Visitor View for Admin----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_active_visitor(request):
    visitors = Visitor.objects.all().filter(status=True)
    return render(request, 'admin/admin_active_visitor.html',{'visitors':visitors})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_visitor_active(request):
    visitor=get_object_or_404(Visitor, pk=request.GET.get('visitor_id'))
    user=User.objects.get(id=visitor.user_id)
    user.delete()
    visitor.delete()
    return redirect(reverse('admin_active_visitor'))

#<-----Active Seller View for Admin----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_active_seller(request):
    sellers = Seller.objects.all().filter(status=True)
    return render(request, 'admin/admin_active_seller.html',{'sellers':sellers})

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def detail_active_seller(request, id):
    products=''
    sellers = Seller.objects.all().get(id=id)
    products = Product.objects.all().filter(seller=id,status=True)
    data={'sellers':sellers,'products':products}
    return render(request, 'admin/detail_active_seller.html',data)

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_seller_active(request):
    seller=get_object_or_404(Seller, pk=request.GET.get('seller_id'))
    user=User.objects.get(id=seller.user_id)
    user.delete()
    seller.delete()
    return redirect(reverse('admin_active_seller'))

#<-----Admin active product page----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_product(request):
    products = Product.objects.all().filter(status=True)
    return render(request, 'admin/admin_product.html',{'products':products})

#<-----admin Detail view of product----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def detail_product_admin(request, id):
    products = Product.objects.all().get(id=id)
    return render(request, 'admin/detail_product_admin.html',{'products':products})

#<-----Admin active product page----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_request_product(request):
    products = Product.objects.all().filter(status=False)
    return render(request, 'admin/admin_request_product.html',{'products':products})

#<-----admin Detail view of product----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def detail_request_product_admin(request, id):
    products = Product.objects.all().get(id=id)
    return render(request, 'admin/detail_request_product_admin.html',{'products':products})

#<-----Admin approve product----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def product_approve(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.status=True
    product.save()
    return redirect(reverse('admin_request_product'))

#<-----admin delete product----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def product_delete(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.delete()
    return redirect(reverse('admin_request_product'))

#<-----admin inactive product----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def inactive(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.activity=False
    product.save()
    return redirect(reverse('admin_product'))

#<-----admin active product----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def active(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.activity=True
    product.save()
    return redirect(reverse('admin_product'))

#<-----admin delete approved product----->#
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def approve_product_delete(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.delete()
    return redirect(reverse('admin_product'))

#<---------------------------------------------->#
#<---------------Visitor Functions-------------->#
#<---------------------------------------------->#

#<-----Signup For Visitor----->#
def visitor_signup(request):
    if request.method=='POST':
        form1=VisitorUserForm(request.POST)
        form2=VisitorExtraForm(request.POST)
        print(form1.is_valid())
        print(form2.is_valid())
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_visitor_group=Group.objects.get_or_create(name='VISITOR')
            my_visitor_group[0].user_set.add(user)

            messages.success(request, 'Request send for approval, Try Login after 24 Hours..')
            print("done!!")
            return HttpResponseRedirect('/')
    else:
        form1=VisitorUserForm()
        form2=VisitorExtraForm()
    return render(request, 'visitor/visitor_signup.html',{'form1':form1,'form2':form2})

#<-----Login For Visitor----->#
def visitor_login(request):
    if request.method == 'POST':
        form = VisitorLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.groups.filter(name='VISITOR'):
                    if Visitor.objects.all().filter(user_id=user.id,status=True):
                        login(request,user)
                        return redirect('visitor_home')
                    else:
                       messages.success(request, 'Your Request is in process, please wait for Approval..') 
                else:
                    messages.success(request, 'Your account is not found in Visitor..')
            else:
                messages.success(request, 'Your Username and Password is Wrong..')
    else:
         form = VisitorLoginForm()           
    return render(request, 'visitor/visitor_login.html',{'form':form})

#<-----Home Page for Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_home(request):
    return render(request, 'visitor/visitor_home.html')

#<-----Profile Page for Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_profile(request):
    return render(request, 'visitor/visitor_profile.html')

#<-----Change password----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def change_password_visitor(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('visitor_home')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'visitor/change_password_visitor.html', {'form': form})

#<-----Add soil By Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_add_soil(request):
    if request.method=='POST':
        form=SoilAddForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.save()

            messages.success(request, 'Your Contibution send for Verification, If detail is genuine it may reflect in Soil after 24 Hours..')

            return HttpResponseRedirect('visitor_home')
    else:
        form=SoilAddForm()
    return render(request, 'visitor/visitor_add_soil.html',{'form':form})

def load_regions(request):
    district_id = request.GET.get('district_id')
    regions = Region.objects.filter(district_id=district_id).all()
    return render(request, 'dropdown_list_region.html', {'regions':regions})

#<-----Find Soil for Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_find_soil(request):
    soils = None
    if request.method == 'POST':
        form = FindSoilForm(request.POST)
        if form.is_valid():
            district = request.POST['district']
            soils = SoilLocationDetail.objects.all().filter(district=district, status=True)
    else:
        form = FindSoilForm()
    return render(request, 'visitor/visitor_find_soil.html',{'form':form,'soils':soils})

#<-----Find Soil Detail for Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_find_soil_detail(request):
    soils = None
    if request.method == 'POST':
        form = FindSoilDetailForm(request.POST)
        if form.is_valid():
            soil = request.POST['soil']
            soils = SoilDetail.objects.all().filter(soil=soil)
    else:
        form = FindSoilDetailForm()
    return render(request, 'visitor/visitor_find_soil_detail.html',{'form':form,'soils':soils})

#<-----Find Rainfall for Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_find_rainfall(request):
    rainfalls = None
    if request.method == 'POST':
        form = FindRainfallForm(request.POST)
        if form.is_valid():
            district = request.POST['district']
            rainfalls = RainfallDetail.objects.all().order_by('year').filter(district=district)
    else:
        form = FindRainfallForm()
    return render(request, 'visitor/visitor_find_rainfall.html',{'form':form,'rainfalls':rainfalls})

#<-----Request seed by Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_get_seed(request):
    if request.method=='POST':
        form=RequestSeedForm(request.POST)
        if form.is_valid():
            
            username = request.user.username
            name = request.user.visitor.get_name
            email = request.user.visitor.email
            district = str(request.user.visitor.district)
            gender = request.user.visitor.gender
            address = request.POST.get('address')
            crop = request.POST.get('crop')
            quantity = request.POST.get('quantity')

            req=RequestSeed.objects.create(username=username, name=name, email=email, district=district, gender=gender, address=address, crop=crop, quantity=quantity)
            req.save()
            
            messages.success(request, 'Your application in process it may take some time..')

            return HttpResponseRedirect('visitor_home')
    else:
        form=RequestSeedForm()
    return render(request, 'visitor/visitor_get_seed.html',{'form':form})

#<-----Request seed by Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_get_fertilizer(request):
    if request.method=='POST':
        form=RequestFertilizerForm(request.POST)
        if form.is_valid():
            
            username = request.user.username
            name = request.user.visitor.get_name
            email = request.user.visitor.email
            district = str(request.user.visitor.district)
            gender = request.user.visitor.gender
            address = request.POST.get('address')
            fertilizer = request.POST.get('fertilizer')
            quantity = request.POST.get('quantity')

            req=RequestFertilizer.objects.create(username=username, name=name, email=email, district=district, gender=gender, address=address, fertilizer=fertilizer, quantity=quantity)
            req.save()
            
            messages.success(request, 'Your application in process it may take some time..')

            return HttpResponseRedirect('visitor_home')
    else:
        form=RequestFertilizerForm()
    return render(request, 'visitor/visitor_get_fertilizer.html',{'form':form})

#<-----Application for seed request view by Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_seed_request(request):
    username=request.user.username
    seeds = RequestSeed.objects.all().filter(username=username)
    return render(request, 'visitor/visitor_seed_request.html',{'seeds':seeds})

#<-----Application for fertilizer request view by Visitor----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_fertilizer_request(request):
    username=request.user.username
    ferts = RequestFertilizer.objects.all().filter(username=username)
    return render(request, 'visitor/visitor_fertilizer_request.html',{'ferts':ferts})

#<-----Visitor Virtual Market Home----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_market_home(request):
    seller = Seller.objects.all().filter(status=True)
    visitor = request.user.visitor
    cart_count = Cart.objects.all().filter(visitor=visitor).count()
    order_count = Order.objects.all().filter(visitor=visitor, payment=False).count()
    pay_count = Order.objects.all().filter(visitor=visitor, payment=True).count()
    return render(request, 'visitor/visitor_market_home.html',{'seller':seller,'cart_count':cart_count,'order_count':order_count,'pay_count':pay_count})

#<-----Visitor Virtual Market Search----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def search(request):
    search=''
    product=''
    if request.method=='POST':
        search = request.POST.get('search')
        product = Product.objects.all().filter(status=True,activity=True,product_name=search)
    return render(request, 'visitor/search.html',{'search':search,'product':product})

#<-----Visitor Virtual Market Vegitable category----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def vegetable_cat(request):
    veg = Product.objects.all().filter(status=True,activity=True,category="Vegetable")
    return render(request, 'visitor/vegetable_cat.html',{'veg':veg})

#<-----Visitor Virtual Market Fruits category----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def fruit_cat(request):
    fru = Product.objects.all().filter(status=True,activity=True,category="Fruit")
    return render(request, 'visitor/fruit_cat.html',{'fru':fru})

#<-----Visitor Virtual Market Seeds category----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def seed_cat(request):
    seed = Product.objects.all().filter(status=True,activity=True,category="Seed")
    return render(request, 'visitor/seed_cat.html',{'seed':seed})

#<-----Visitor Virtual Market Bio Fertilizer category----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def bio_cat(request):
    bio = Product.objects.all().filter(status=True,activity=True,category="Bio Fertilizer")
    return render(request, 'visitor/bio_cat.html',{'bio':bio})

#<-----Visitor Virtual Market Nuts category----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def nut_cat(request):
    nut = Product.objects.all().filter(status=True,activity=True,category="Nuts")
    return render(request, 'visitor/nut_cat.html',{'nut':nut})

#<-----Visitor Virtual Market Spices category----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def spices_cat(request):
    spi = Product.objects.all().filter(status=True,activity=True,category="Spices")
    return render(request, 'visitor/spices_cat.html',{'spi':spi})

#<-----Visitor Detail view of product----->#
@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def view_product_visitor(request, id):
    visitor = request.user.visitor
    products = Product.objects.all().get(id=id)
    cart = Cart.objects.all().filter(visitor=visitor).first()
    return render(request, 'visitor/view_product_visitor.html',{'products':products,'cart':cart})

@login_required(login_url='visitor_login')
@user_passes_test(is_visitor)
def visitor_view_seller(request, id):
    products=''
    sellers = Seller.objects.all().get(id=id)
    products = Product.objects.all().filter(seller=id,status=True)
    data={'sellers':sellers,'products':products}
    return render(request, 'visitor/visitor_view_seller.html',data)



#<-----Signup For Seller----->#
def seller_signup(request):
    if request.method=='POST':
        form1=SellerUserForm(request.POST)
        form2=SellerExtraForm(request.POST,request.FILES)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_seller_group=Group.objects.get_or_create(name='SELLER')
            my_seller_group[0].user_set.add(user)

            messages.success(request, 'Request send for process, please wait for Approval..')

            return HttpResponseRedirect('/')
    else:
        form1=SellerUserForm()
        form2=SellerExtraForm()
    return render(request, 'seller/seller_signup.html',{'form1':form1,'form2':form2})

#<-----Login For Seller----->#
def seller_login(request):
    if request.method == 'POST':
        form = SellerLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.groups.filter(name='SELLER'):
                    if Seller.objects.all().filter(user_id=user.id,status=True):
                        login(request,user)
                        return redirect('seller_home')
                    else:
                       messages.success(request, 'Your Request is in process, please wait for Approval..') 
                else:
                    messages.success(request, 'Your account is not found in Seller..')
            else:
                messages.success(request, 'Your Username and Password is Wrong..')
    else:
         form = VisitorLoginForm()           
    return render(request, 'seller/seller_login.html',{'form':form})

#<-----Home Page for Seller----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def seller_home(request):
    return render(request, 'seller/seller_home.html')

#<-----Profile Page for Seller----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def seller_profile(request):
    return render(request, 'seller/seller_profile.html')

#<-----Change password----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def change_password_seller(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('seller_home')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'seller/change_password_seller.html', {'form': form})

#<-----Seller product page----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def product(request):
    products = Product.objects.all().filter(seller=request.user.seller.id)
    return render(request, 'seller/product.html',{'products':products})

#<-----Detail view of product----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def detail_product_seller(request, id):
    products = Product.objects.all().get(id=id)
    if request.method=='POST':
        form=EditPriceForm(request.POST)
        if form.is_valid():
            obj = Product.objects.all().get(id=id)
            obj.price = request.POST.get('price')
            obj.save()

            return HttpResponseRedirect('detail_product_seller')
    else:
        form=EditPriceForm()
    return render(request, 'seller/detail_product_seller.html',{'products':products,'form':form})

#<-----Seller add new product page----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def add_product(request):
    if request.method=='POST':
        form=ProductAddForm(request.POST, request.FILES)
        if form.is_valid():
            
            product_name = request.POST.get('product_name')
            describe = request.POST.get('describe')
            image_1 = request.FILES.get('image_1')
            image_2 = request.FILES.get('image_2')
            image_3 = request.FILES.get('image_3')
            image_4 = request.FILES.get('image_4')
            seller = str(request.user.seller.id)
            category=request.POST.get('category')
            price = request.POST.get('price')
            price_per_quantity = request.POST.get('price_per_quantity')

            req=Product.objects.create(product_name=product_name, describe=describe, image_1=image_1, image_2=image_2, image_3=image_3, image_4=image_4, seller_id = seller, category=category, price=price, price_per_quantity=price_per_quantity)
            req.save()

            return HttpResponseRedirect('seller_home')
    else:
        form=ProductAddForm()
    return render(request, 'seller/add_product.html',{'form':form})

#<-----Make out of stock----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def outofstock(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.stock=False
    product.save()
    return redirect(reverse('product'))

#<-----Make out of stock----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def instock(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.stock=True
    product.save()
    return redirect(reverse('product'))

#<-----Delete product----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def delete_product_seller(request):
    product=get_object_or_404(Product, pk=request.GET.get('product_id'))
    product.delete()
    return redirect(reverse('product'))


#<-----Package Shipped----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def shipped_package(request):
    order=get_object_or_404(Order, pk=request.GET.get('order_id'))
    order.shipped=True
    order.save()
    return redirect(reverse('new_order_seller'))

#<-----Shipped Order----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def shipped_order_seller(request):
    orders = Order.objects.all().filter(payment=True, shipped=True, order=True)
    pay = Pay.objects.all().filter(order__in=orders)
    zippedList = zip(orders, pay)
    return render(request, 'seller/shipped_order_seller.html',{'zippedList':zippedList})

#<-----Package Shipped----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def delivered_order(request):
    order=get_object_or_404(Order, pk=request.GET.get('order_id'))
    order.shipped=False
    order.delivered=True
    order.order=False
    order.save()
    return redirect(reverse('shipped_order_seller'))

#<-----Delivered Order----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def delivered_order_seller(request):
    orders = Order.objects.all().filter(payment=True, delivered=True, order=False)
    pay = Pay.objects.all().filter(order__in=orders)
    zippedList = zip(orders, pay)
    return render(request, 'seller/delivered_order_seller.html',{'zippedList':zippedList})

#<-----Canceled Order----->#
@login_required(login_url='seller_login')
@user_passes_test(is_seller)
def canceled_order_seller(request):
    orders = Order.objects.all().filter(payment=True, delivered=False, order=False)
    pay = Pay.objects.all().filter(order__in=orders)
    zippedList = zip(orders, pay)
    return render(request, 'seller/canceled_order_seller.html',{'zippedList':zippedList})