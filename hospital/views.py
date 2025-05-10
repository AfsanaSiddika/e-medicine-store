import random
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from urllib.parse import unquote, quote
from .models import *
from .forms import LabBookingForm


# Create your views here.
def home(request):
    return render(request, 'index.html')

def SignUp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose a different username.')
            return render(request, 'signup.html')

       
        user = User.objects.create_user(username=username, email=email, password=password)

        
        request.session['signup_username'] = username
        request.session['signup_email'] = email
        request.session['signup_password'] = password

        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'You have successfully signed up!')
            return redirect('login')  
        else:
            messages.error(request, 'An error occurred while signing up. Please try again.')
            return render(request, 'Signup.html')
        
    return render(request, 'Signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the login credentials belong to a regular user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'You have successfully logged in!')
            return redirect('home')  # Redirect to the booking page
         
        else:
            # Authentication failed, display an error message
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    return render(request, 'login.html')

@login_required
def logout(request):
    django_logout(request)
    return redirect('home')


@login_required
def user_profile(request):
    user = request.user

    # Get or create the user profile
    profile, created = Profile.objects.get_or_create(user=user)

    # Get all related data for the user
    orders = Order.objects.filter(user=user)
    appointments = Appointment.objects.filter(patient=user)
    carts = Cart.objects.filter(user=user)
    lab_bookings = LabBooking.objects.filter(user=user)  # Add this line to get lab test bookings

    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'appointments': appointments,
        'carts': carts,
        'lab_bookings': lab_bookings,  # Add this to the context
    }

    return render(request, 'Userprofile.html', context)


def shopmedicine(request):
    selected_category = request.GET.get('category', None)
    
    if selected_category:
        # Decode the category to handle special characters
        selected_category = unquote(selected_category)
        # print(f"Decoded selected category: {selected_category}")
        
        medicines = Medicine.objects.filter(category=selected_category)
    else:
        medicines = Medicine.objects.all()
    
    categories = Medicine.CATEGORY_CHOICES
    medicines_by_category = {}

    for category, _ in categories:
        medicines_in_category = Medicine.objects.filter(category=category)
        medicines_by_category[category] = medicines_in_category

    # Encode the category name for the URL
    encoded_categories = [(quote(category), name) for category, name in categories]

    context = {
        'medicines': medicines,
        'medicines_by_category': medicines_by_category,
        'categories': encoded_categories,  # Pass encoded categories
        'selected_category': selected_category,
    }

    return render(request, 'Medicine.html', context)

def medicine_details(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    context = {
        'medicine': medicine,
    }
    return render(request, 'MedicineDetails.html', context)



def appointments(request):
    doctors = Doctor.objects.all()
    hospitals = Hospital.objects.all()
    context = {
        'doctors': doctors,
        'hospitals': hospitals,
    }
    return render(request, 'Appointments.html', context)

# Doctor details and schedule view
def doctor_details(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    schedules = Schedule.objects.filter(doctor=doctor).order_by('hospital')

    context = {
        'doctor': doctor,
        'schedules': schedules,
    }
    return render(request, 'doctor_details.html', context)

# Booking logic
@login_required(login_url='login')
def book_appointment(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    doctor = schedule.doctor
    hospital = schedule.hospital

    if request.method == "POST":
        date = request.POST.get('date')
        time = request.POST.get('time')
        contact = request.POST.get('contact')

        # Check if this doctor is already booked at the selected date and time
        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
            return HttpResponse("This time is already booked for the selected doctor.")

        # Create the appointment
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            hospital=hospital,
            schedule=schedule,
            patient_contact=contact,
            date=date,
            time=time,
            status='pending'
        )

        return redirect('appointment_confirmation', appointment_id=appointment.id)

    context = {
        'doctor': doctor,
        'schedule': schedule
    }
    return render(request, 'book_appointment.html', context)

# Appointment confirmation view
@login_required(login_url='login')
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointment_confirmation.html', {'appointment': appointment})


def hospital_details(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = hospital.schedules.values('doctor').distinct()
    doctor_list = Doctor.objects.filter(id__in=[d['doctor'] for d in doctors])
    
    context = {
        'hospital': hospital,
        'doctors': doctor_list,  # Pass the doctors related to the hospital
    }
    return render(request, 'hospital_details.html', context)

@login_required(login_url='login')
def cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    total_price = sum([item.total_price() for item in cart_items])  # Calculate total price of all cart items

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)


@login_required(login_url='login')
def add_to_cart(request, medicine_id):
    user = request.user
    medicine = get_object_or_404(Medicine, id=medicine_id)

    # Check if cart item already exists for the user and medicine
    cart_item, created = Cart.objects.get_or_create(user=user, medicine=medicine)
    
    if not created:  # If it already exists, increase the quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')
   
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required
def clear_cart(request):
    user = request.user
    Cart.objects.filter(user=user).delete()  # Delete all cart items for the user
    return redirect('cart')

@login_required
def increase_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

@login_required
def decrease_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()  # Remove item if quantity reaches 0
    return redirect('cart')



@login_required(login_url='login')
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum([item.total_price() for item in cart_items])  # Calculate total price

    if request.method == 'POST':
        contact_number = request.POST.get('contact_number', '').strip()
        address = request.POST.get('address', '').strip()

        # Validate that both fields are not empty
        if not contact_number or not address:
            messages.error(request, "Please fill in both Contact Number and Delivery Address!")
            return redirect('checkout')  # Redirect back to the checkout page

        # Create a new order if validations pass
        order = Order.objects.create(
            user=user,
            total=total_price,
            status='shipped'
        )

        # Add cart items to order
        for item in cart_items:
            OrderItem.objects.create(order=order, medicine=item.medicine, quantity=item.quantity)

        # Clear the cart
        cart_items.delete()

        # Redirect to order confirmation page using order ID
        return redirect('order_confirmation', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, user=request.user, id=order_id)

    context = {
        'order': order,
    }
    return render(request, 'order_confirmation.html', context)


@login_required(login_url='login')
def manage_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-ordered_at')  # Get user's orders

    context = {
        'orders': orders,
    }
    return render(request, 'manage_orders.html', context)


def mark_as_processing(modeladmin, request, queryset):
    queryset.update(delivery_status='Processing')
mark_as_processing.short_description = "Mark selected orders as Processing"

def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(delivery_status='Shipped')
mark_as_shipped.short_description = "Mark selected orders as Shipped"

def mark_as_delivered(modeladmin, request, queryset):
    queryset.update(delivery_status='Delivered')
mark_as_delivered.short_description = "Mark selected orders as Delivered"


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LabBooking
from .forms import LabBookingForm

@login_required(login_url='login')
def lab_test_view(request):
    if request.method == "POST":
        form = LabBookingForm(request.POST)
        if form.is_valid():
            lab_booking = form.save(commit=False)
            lab_booking.user = request.user  # Assign the logged-in user
            lab_booking.save()
            messages.success(request, "Lab test booked successfully!")
            return redirect('lab_booking_list')  # Redirect to the list of bookings
    else:
        form = LabBookingForm()

    context = {'form': form}
    return render(request, 'lab_booking.html', context)

@login_required(login_url='login')
def lab_booking_list(request):
    bookings = LabBooking.objects.filter(user=request.user)
    return render(request, 'lab_booking_list.html', {'bookings': bookings})


import random
import json
from django.http import JsonResponse
from django.shortcuts import render

def emergency_ambulance(request):
    districts = [
        "Bagerhat", "Bandarban", "Barguna", "Barishal", "Bhola", "Bogra", "Brahmanbaria",
        "Chandpur", "Chapai Nawabganj", "Chattogram", "Chuadanga", "Comilla", "Cox's Bazar",
        "Dhaka", "Dinajpur", "Faridpur", "Feni", "Gaibandha", "Gazipur", "Gopalganj", "Habiganj",
        "Jamalpur", "Jessore", "Jhalokati", "Jhenaidah", "Joypurhat", "Khagrachhari", "Khulna",
        "Kishoreganj", "Kurigram", "Kushtia", "Lakshmipur", "Lalmonirhat", "Madaripur", "Magura",
        "Manikganj", "Meherpur", "Moulvibazar", "Munshiganj", "Mymensingh", "Naogaon", "Narail",
        "Narayanganj", "Narsingdi", "Natore", "Netrokona", "Nilphamari", "Noakhali", "Pabna",
        "Panchagarh", "Patuakhali", "Pirojpur", "Rajbari", "Rajshahi", "Rangamati", "Rangpur",
        "Satkhira", "Shariatpur", "Sherpur", "Sirajganj", "Sunamganj", "Sylhet", "Tangail", "Thakurgaon"
    ]

    ambulances = []
    for district in districts:
        num_services = random.randint(1, 3)
        for i in range(num_services):
            service_types = ["Government", "Private", "24/7 Service", "Red Crescent", "City Corporation"]
            service_type = random.choice(service_types)
            phone = f"01{random.randint(10000000, 99999999)}"
            phone2 = f"01{random.randint(10000000, 99999999)}" if random.random() > 0.5 else None

            ambulance = {
                'name': f"{district} {'Medical' if service_type == 'Government' else 'Emergency'} Service",
                'district': district,
                'phone': phone,
                'phone2': phone2,
                'type': service_type,
                'area': random.choice([
                    "Citywide coverage",
                    "District headquarters",
                    "Upazila coverage",
                    "All major hospitals",
                    "Whole district"
                ])
            }

            # Special cases for major cities
            if district == "Dhaka":
                ambulance['name'] = random.choice([
                    "Dhaka Metro Emergency",
                    "Dhaka City Ambulance",
                    "Dhaka Medical College",
                    "Dhaka Central Hospital"
                ])
                ambulance['phone'] = f"01{random.randint(700000000, 799999999)}"

            elif district == "Chattogram":
                ambulance['name'] = random.choice([
                    "Chattogram Port Authority",
                    "Chattogram City Emergency",
                    "Cox's Bazar Coastal Service"
                ])

            ambulances.append(ambulance)

    # For AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').lower()
        filtered = [a for a in ambulances
                   if query in a['district'].lower()
                   or query in a['name'].lower()]
        return JsonResponse({'ambulances': filtered})

    context = {
        'ambulances_json': json.dumps(ambulances),
        'title': 'Emergency Ambulance Services - All 64 Districts'
    }
    return render(request, 'emergency_ambulance.html', context)



