from email import message
from unicodedata import category
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from bus_booking_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from reservationApp.forms import UserRegistration, UpdateProfile, UpdatePasswords, SaveCategory, SaveLocation, SaveBus, SaveSchedule, SaveBooking, PayBooked
from reservationApp.models import Booking, Category, Location, Bus, Schedule
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from datetime import datetime
from django.db.models import Q
from reservationApp.models import Bus
from .mongoClient import mongoDBClient,busColl,categoriesColl,tripsColl,locationCOll,schedulesColl,bookingsColl





context = {
    'page_title' : 'File Management System',
}


#login
def login_user(request):
    print("Login view called!") 
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# @login_required

def home(request):
    context['page_title'] = 'Home'
    context['buses'] = busColl.count_documents({})
    context['categories'] = categoriesColl.count_documents({})
    context['upcoming_trip'] = tripsColl.count_documents({})

    # context['upcoming_trip'] = Schedule.objects.filter(status= 1, schedule__gt = datetime.today()).count()
    return render(request, 'home.html',context)

def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)


@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html',context)


# Category
@login_required
def category_mgt(request):
    context['page_title'] = "Bus Categories"
    categories = categoriesColl.find()
    categories=list(categories)
    # for catg in categories:
    #     catg['id']=str(catg['_id'])
    context['categories'] = categories

    return render(request, 'category_mgt.html', context)

@login_required
def save_category(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        query={"name":request.POST['name']}
        print(query)
        existdata=categoriesColl.find_one(query)
        count=categoriesColl.count_documents({})
        categoryDict={}

        if existdata:
            resp['msg'] = 'Please use unique category names.'
        else:
            categoryDict['name']=request.POST['name']
            categoryDict['description']=request.POST['description']
            categoryDict['status']=request.POST['status']
            categoryDict['date_created']=datetime.now()
            categoryDict['date_updated']=datetime.now()
            print("fields updating")

        updateStatus=   categoriesColl.update_one({"id":request.POST['id']},{"$set":categoryDict})
        if updateStatus.modified_count >0:
            print("modified")
            resp['status']= "success"
        else:
            categoryDict['id']=count+1

            print("new document added")
            categoriesColl.insert_one(categoryDict)
            resp['status'] = 'success'
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_category(request, pk=None):
    context['page_title'] = "Manage Category"
    print(pk,"given id ")
    if not pk is None:
        category = categoriesColl.find_one({"id" : pk})
        context['category'] = category
    else:
        context['category'] = {}

    return render(request, 'manage_category.html', context)

@login_required
def delete_category(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            print(request.POST['id'])
            category = categoriesColl.delete_one({"id" : int(request.POST['id'])})
            messages.success(request, 'Category has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Category has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Category has failed to delete'
    print(resp)
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Location
@login_required
def location_mgt(request):
    context['page_title'] = "Locations"
    locations = locationCOll.find()
    locations = list(locations)
    print(locations,"all location")

    context['locations'] = locations

    return render(request, 'location_mgt.html', context)

@login_required
def save_location(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
            query={"location":request.POST['location']}
            print(query)
            existdata=locationCOll.find_one(query)
            count=locationCOll.count_documents({})
            locationDict={}

            if existdata:
                resp['msg'] = 'please use a different location this already Exists'
            else:
               locationDict['location']=request.POST['location']
               locationDict['status']=request.POST['status']
               locationDict['date_created']=datetime.now()
               locationDict['date_updated']=datetime.now()
               print("fields updating")

            updateStatus = locationCOll.update_one({"id":request.POST['id']},{"$set":locationDict})
            if updateStatus.modified_count >0:
                print("modified")
                resp['status'] = "success"
            else:
                locationDict['id']=count+1
            
            print("new document added ")

            locationCOll.insert_one(locationDict)
            resp['msg'] = 'Data added successfully.'
            return HttpResponse(json.dumps(resp), content_type = 'application/json')

    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')


@login_required
def manage_location(request, pk=None):
    context['page_title'] = "Manage Location"
    print(pk,"given id")
    if not pk is None:
        location = locationCOll.find_one({"id" : pk})
        context['location'] = location
    else:
        context['location'] = {}

    return render(request, 'manage_location.html', context)

@login_required
def delete_location(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        print(request)
        try:
            print(request.POST['id'],"check id")
            location = locationCOll.delete_one({"id":int(request.POST['id'])})
            messages.success(request, 'Location has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'location has failed to delete'
            print(err)

    else:
        resp['msg'] = 'location has failed to delete'
    print(resp)
    return HttpResponse(json.dumps(resp), content_type="application/json")


# bus
@login_required
def bus_mgt(request):
    context['page_title'] = "Buses"
    buses = busColl.find()
    buses = list(buses)
    print(buses)
    context['buses'] = buses

    return render(request, 'bus_mgt.html', context)

@login_required
def save_bus(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        query={"bus":request.POST['bus_number']}
        print(query)
        existdata = busColl.find_one(query)
        count=busColl.count_documents({})
        busDict={}

        if existdata:
            resp['msg'] ="please use a different bus name this already Exits"
        else:
            busDict['bus_number'] = request.POST['bus_number']
            busDict['category'] = request.POST['category']
            busDict['seats'] = request.POST['seats']
            busDict['status']= request.POST['status']
            busDict['date_created']=datetime.now()
            busDict['date_updated']=datetime.now()
            print("fields updating")
            busDict['id']=count+1

            busColl.insert_one(busDict)
            resp['msg'] = "data added successfully"
            return HttpResponse(json.dumps(resp),content_type ='application/json')
    


        updateStatus = busColl.update_one({"id":request.POST['id']},{"$set":busDict})
        if updateStatus.modified_count >0:
            print("modified")
            resp['status'] = "success"
        else:
            busDict['id']=count+1
        
        print("new Document added")

        busColl.insert_one(busDict)
        resp['msg'] = "data added successfully"
        return HttpResponse(json.dumps(resp),content_type ='application/json')
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_bus(request, pk=None):
    context['page_title'] = "Manage Bus"
    categories = categoriesColl.find()
    categories=list(categories)
    allCategory=[]
    for cat in categories:
        allCategory.append({"category":cat['name'],"id":cat['id']})

    print(allCategory)

    context['categories'] = allCategory
    print(context)
    if not pk is None:
        bus = busColl.find_one({"id" : pk})
        context['bus'] = bus
    else:
        context['bus'] = {}

    return render(request, 'manage_bus.html', context)

@login_required
def delete_bus(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            bus = busColl.delete_one({"id":int(request.POST['id'])})
            messages.success(request, 'Bus has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'bus has failed to delete'
            print(err)

    else:
        resp['msg'] = 'bus has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")    


# schedule
@login_required
def schedule_mgt(request):
    context['page_title'] = "Trip Schedules"
    schedules = schedulesColl.find()
    schedules = list(schedules)

    context['schedules'] = schedules
    print(schedules)

    return render(request, 'schedule_mgt.html', context)

@login_required
def save_schedule(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
       query={"schedules":request.POST['schedule']}
       existdata = schedulesColl.find_one(query)
       count=schedulesColl.count_documents({})
       scheduleDict={}

    if existdata:
        resp['msg'] = "please give a different time this is already Scheduled "
    else:
        scheduleDict['bus'] = request.POST['bus']
        scheduleDict['depart'] = request.POST['depart']
        scheduleDict['destination'] = request.POST['destination']
        scheduleDict['code'] = request.POST['code']
        scheduleDict['schedule'] = datetime.now()
        scheduleDict['fare'] = request.POST['fare']
        scheduleDict['status'] = request.POST['status']
        scheduleDict['date_created']=datetime.now()
        scheduleDict['date_updated']=datetime.now()
        scheduleDict['id']=count+1

        schedulesColl.insert_one(scheduleDict)
        resp['msg'] = "data added sccessufully"
        return HttpResponse(json.dumps(resp),content_type ='application/json')
    
    updateStatus = schedulesColl.update_one({"id":request.POST['id']},{ "$set":scheduleDict})
    if updateStatus.modified_count >0:
        print("modified")
        resp['msg'] = "data added successfully "
        return HttpResponse(json.dumps(resp),content_type = 'application/json')
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_schedule(request, pk=None):
    context['page_title'] = "Manage Schedule"
    buses = busColl.find()
    buses =list(buses)
    allbuses=[]
    for all in buses:
        allbuses.append({"buses":all['bus_number'],"id":all['id']})
    
    print(allbuses)
    locations = locationCOll.find()
    locations =list(locations)
    alllocations=[]
    for loc in locations:
        alllocations.append({"locations":loc['location'],"id":loc['id']})
    
    context['buses'] = buses
    context['locations'] = locations

    if not pk is None:
        schedule = schedulesColl.find_one({"id":pk})
        context['schedule'] = schedule
    else:
        context['schedule'] = {}

    return render(request, 'manage_schedule.html', context)

@login_required
def delete_schedule(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            schedule = schedulesColl.delete_one({"id":int(request.POST['id'])}) 
            messages.success(request, 'Schedule has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'schedule has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Schedule has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")  


# scheduled Trips
def scheduled_trips(request):
    if not request.method == 'POST':
        context['page_title'] = "Scheduled Trips"
        schedules = schedulesColl.find({})
        context['schedules'] = schedules
        context['is_searched'] = False
        context['data'] = {}
    else:
        context['page_title'] = "Search Result | Scheduled Trips"
        context['is_searched'] = True
        date = datetime.strptime(request.POST['date'],"%Y-%m-%d").date()
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        depart = Location.objects.get(id = request.POST['depart'])
        destination = Location.objects.get(id = request.POST['destination'])
        schedules = Schedule.objects.filter(Q(status = 1) & Q(schedule__year = year) & Q(schedule__month = month) & Q(schedule__day = day) & Q(Q(depart = depart) | Q(destination = destination ))).all()
        context['schedules'] = schedules
        context['data'] = {'date':date,'depart':depart, 'destination': destination}

    return render(request, 'scheduled_trips.html', context)

def manage_booking(request, schedPK=None, pk=None):
    context['page_title'] = "Manage Booking"
    context['schedPK'] = schedPK
    if not schedPK is None:
        schedule = schedulesColl.find_one({'id': (schedPK)})
        context['schedule'] = schedule
    else:
        context['schedule'] = {}
    if not pk is None:
        book = bookingsColl.find_one({'id': pk})
        context['book'] = book
    else:
        context['book'] = {}

    return render(request, 'manage_book.html', context)

def save_booking(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            booking = Booking.objects.get(pk=request.POST['id'])
        else:
            booking = None
        if booking is None:
            form = SaveBooking(request.POST)
        else:
            form = SaveBooking(request.POST, instance= booking)
        if form.is_valid():
            form.save()
            if booking is None:
                booking = Booking.objects.last()
                messages.success(request, f'Booking has been saved successfully. Your Booking Refderence Code is: <b>{booking.code}</b>', extra_tags = 'stay')
            else:
                messages.success(request, f'<b>{booking.code}</b> Booking has been updated successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

def bookings(request):
    context['page_title'] = "Bookings"
    bookings = Booking.objects.all()
    context['bookings'] = bookings

    return render(request, 'bookings.html', context)


@login_required
def view_booking(request,pk=None):
    if pk is None:
        messages.error(request, "Unkown Booking ID")
        return redirect('booking-page')
    else:
        context['page_title'] = 'Vieww Booking'
        context['booking'] = Booking.objects.get(id = pk)
        return render(request, 'view_booked.html', context)


@login_required
def pay_booked(request):
    resp = {'status':'failed','msg':''}
    if not request.method == 'POST':
        resp['msg'] = "Unknown Booked ID"
    else:
        booking = Booking.objects.get(id= request.POST['id'])
        form = PayBooked(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, f"<b>{booking.code}</b> has been paid successfully", extra_tags='stay')
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += str(error + "<br>")
    
    return HttpResponse(json.dumps(resp),content_type = 'application/json')

@login_required
def delete_booking(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            booking = Booking.objects.get(id = request.POST['id'])
            code = booking.code
            booking.delete()
            messages.success(request, f'[<b>{code}</b>] Booking has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'booking has failed to delete'
            print(err)

    else:
        resp['msg'] = 'booking has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")  

def find_trip(request):
    context['page_title'] = 'Find Trip Schedule'
    context['locations'] = Location.objects.filter(status = 1).all
    today = datetime.today().strftime("%Y-%m-%d")
    context['today'] = today
    return render(request, 'find_trip.html', context)
    