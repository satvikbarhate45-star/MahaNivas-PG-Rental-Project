from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Booking, PGRoom, District
from .models import District
from .models import (
    UserProfile,
    District,
    PGRoom,
    RoomImage,
    Review,
    Complaint
)


# =========================================================
# REGISTER VIEW
# =========================================================
def register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Match your HTML file input name
        id_proof = request.FILES.get('profile_image')  

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Only include fields that exist in the model
        UserProfile.objects.create(
            user=user,
            id_proof=id_proof
        )

        messages.success(request, "Registration Successful. Please Login.")
        return redirect('login')

    return render(request, "register.html")

# =========================================================
# LOGIN VIEW
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials")

    return render(request, "login.html")


# =========================================================
# USER HOME
# =========================================================
@login_required(login_url='login')
def home_view(request):
    query = request.GET.get('search')

    rooms = PGRoom.objects.filter(is_available=True)

    if query:
        rooms = rooms.filter(address__icontains=query)

    context = {
        "rooms": rooms,
        "district_count": District.objects.count(),
        "total_rooms": PGRoom.objects.count(),
        "booked_rooms": PGRoom.objects.filter(is_available=False).count(),
        "search_query": query
    }

    return render(request, "home.html", context)



from django.http import JsonResponse
from django.db.models import Q

def search_rooms(request):
    query = request.GET.get('q')

    if query:
        rooms = PGRoom.objects.filter(
            Q(address__icontains=query) |
            Q(district__name__icontains=query),
            is_available=True
        )[:5]

        data = []
        for room in rooms:
            data.append({
                "title": room.title,
                "price": str(room.price),
                "district": room.district.name
            })

        return JsonResponse({"rooms": data})

    return JsonResponse({"rooms": []})
# =========================================================
# ADMIN DASHBOARD
# =========================================================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    PGRoom,
    UserProfile,
    Review,
    Complaint,
    Booking,
    District
)

@login_required(login_url='login')
def admin_dashboard(request):

    # 🔒 Only Superuser Can Access
    if not request.user.is_superuser:
        return redirect('home')

    # ================= COUNTS =================
    total_rooms = PGRoom.objects.count()
    total_bookings = Booking.objects.count()
    total_reviews = Review.objects.count()
    total_districts = District.objects.count()
    pending_kyc = UserProfile.objects.filter(is_verified=False).count()
    unapproved_reviews = Review.objects.filter(is_approved=False).count()
    active_complaints = Complaint.objects.filter(status='Pending').count()

    # ================= FULL TABLE DATA =================
    bookings = Booking.objects.select_related(
        'user', 'room'
    ).all().order_by('-created_at')

    rooms = PGRoom.objects.select_related(
        'district', 'owner'
    ).all().order_by('-created_at')

    reviews = Review.objects.select_related(
        'user', 'room'
    ).all().order_by('-created_at')

    complaints = Complaint.objects.select_related(
        'user', 'room'
    ).filter(status='Pending').order_by('-created_at')

    kyc_users = UserProfile.objects.select_related(
        'user'
    ).filter(is_verified=False)

    districts = District.objects.all()

    # ================= CONTEXT =================
    context = {
        # Cards Count
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'total_reviews': total_reviews,
        'pending_kyc': pending_kyc,
        'unapproved_reviews': unapproved_reviews,
        'active_complaints': active_complaints,
        'total_districts': total_districts,   # ✅ ADD THIS
        # Tables Data
        'bookings': bookings,
        'rooms': rooms,
        'reviews': reviews,
        'complaints': complaints,
        'kyc_users': kyc_users,
        'districts': districts,
    }

    return render(request, "admin_dashboard.html", context)
# =========================================================
# APPROVE KYC
# =========================================================

@login_required(login_url='login')
@require_POST
def approve_kyc(request, profile_id):

    if not request.user.is_superuser:
        return redirect('home')

    profile = get_object_or_404(UserProfile, id=profile_id)
    profile.is_verified = True
    profile.save()

    messages.success(request, "KYC Approved Successfully.")
    return redirect('admin_dashboard')


# =========================================================
# REJECT KYC
# =========================================================

@login_required(login_url='login')
@require_POST
def reject_kyc(request, profile_id):

    if not request.user.is_superuser:
        return redirect('home')

    profile = get_object_or_404(UserProfile, id=profile_id)
    profile.delete()

    messages.success(request, "KYC Rejected and Profile Deleted.")
    return redirect('admin_dashboard')


# =========================================================
# ACCEPT REVIEW
# =========================================================

@login_required(login_url='login')
@require_POST
def accept_review(request, review_id):

    if not request.user.is_superuser:
        return redirect('home')

    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()

    messages.success(request, "Review Approved Successfully.")
    return redirect('admin_dashboard')


# =========================================================
# ADD ROOM (ADMIN)
# =========================================================

@login_required(login_url='login')
def add_room(request):

    if not request.user.is_superuser:
        return redirect('home')

    if request.method == "POST":

        title = request.POST.get('title')
        price = request.POST.get('price')
        district_id = request.POST.get('district')
        address = request.POST.get('address')
        vibe_tag = request.POST.get('vibe_tag')
        environment_desc = request.POST.get('environment_desc')
        is_trending = request.POST.get('is_trending') == "on"

        wifi = request.POST.get('wifi') == "on"
        parking = request.POST.get('parking') == "on"
        attached_bathroom = request.POST.get('attached_bathroom') == "on"
        ac = request.POST.get('ac') == "on"

        main_image = request.FILES.get('main_image')
        video_tour = request.FILES.get('video_tour')

        district = District.objects.get(id=district_id)

        room = PGRoom.objects.create(
            owner=request.user,
            title=title,
            price=price,
            district=district,
            address=address,
            main_image=main_image,
            video_tour=video_tour,
            vibe_tag=vibe_tag,
            environment_desc=environment_desc,
            is_trending=is_trending,
            wifi=wifi,
            parking=parking,
            attached_bathroom=attached_bathroom,
            ac=ac
        )

        # Multiple images
        images = request.FILES.getlist('gallery_images')
        for img in images:
            RoomImage.objects.create(room=room, image=img)

        messages.success(request, "Room Added Successfully.")
        return redirect('admin_dashboard')

    districts = District.objects.all()
    return render(request, "add_room.html", {"districts": districts})


# =========================================================
# UPDATE COMPLAINT STATUS
# =========================================================

@login_required(login_url='login')
@require_POST
def resolve_complaint(request, complaint_id):

    if not request.user.is_superuser:
        return redirect('home')

    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.status = "Resolved"
    complaint.save()

    messages.success(request, "Complaint Marked as Resolved.")
    return redirect('admin_dashboard')


# =========================================================
# LOGOUT
# =========================================================

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')




@login_required
def add_room(request):
    districts = District.objects.all()

    if request.method == "POST":
        PGRoom.objects.create(
            owner=request.user,
            district_id=request.POST.get("district"),
            title=request.POST.get("title"),
            price=request.POST.get("price"),
            address=request.POST.get("address"),
            main_image=request.FILES.get("main_image"),
            video_tour=request.FILES.get("video_tour"),
            vibe_tag=request.POST.get("vibe_tag"),
            environment_desc=request.POST.get("environment_desc"),
            wifi=request.POST.get("wifi") == "on",
            parking=request.POST.get("parking") == "on",
            attached_bathroom=request.POST.get("attached_bathroom") == "on",
            ac=request.POST.get("ac") == "on",
        )
        return redirect("admin_dashboard")

    return render(request, "addroom.html", {"districts": districts})


def district_list(request):
    districts = District.objects.all()
    return render(request, "admin/district_list.html", {"districts": districts})

def add_district(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if District.objects.filter(name=name).exists():
            messages.error(request, "District already exists.")
        else:
            District.objects.create(name=name)
            messages.success(request, "District added successfully.")
        return redirect("district_list")
    return render(request, "admin/add_district.html")





def total_rooms_view(request):
    rooms = PGRoom.objects.all()
    return render(request, 'total_room.html', {'rooms': rooms})

def view_room_view(request, room_id):
    room = get_object_or_404(PGRoom, id=room_id)
    return render(request, 'view_room.html', {'room': room})


from django.shortcuts import get_object_or_404, redirect
from .models import PGRoom   # ← use correct model name

def delete_room(request, id):
    room = get_object_or_404(PGRoom, id=id)
    room.delete()
    return redirect('total_rooms')

from django.shortcuts import render, get_object_or_404, redirect
from .models import PGRoom, District   # ✅ use PGRoom

def edit_room(request, id):
    room = get_object_or_404(PGRoom, id=id)

    if request.method == "POST":
        room.title = request.POST.get('title')
        room.price = request.POST.get('price')
        room.district_id = request.POST.get('district')
        room.vibe_tag = request.POST.get('vibe_tag')
        room.address = request.POST.get('address')
        room.environment_desc = request.POST.get('environment_desc')

        room.wifi = 'wifi' in request.POST
        room.parking = 'parking' in request.POST
        room.ac = 'ac' in request.POST
        room.attached_bathroom = 'attached_bathroom' in request.POST

        if request.FILES.get('main_image'):
            room.main_image = request.FILES.get('main_image')

        if request.FILES.get('video_tour'):
            room.video_tour = request.FILES.get('video_tour')

        room.save()
        return redirect('view_room', room.id)

    districts = District.objects.all()

    return render(request, 'edit_room.html', {
        'room': room,
        'districts': districts
    })
    
    
    
    
    
    
    
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import District

def delete_district(request, id):
    district = get_object_or_404(District, id=id)
    district.delete()
    messages.success(request, "District deleted successfully.")
    return redirect('district_list')

from django.shortcuts import render
from .models import PGRoom, District, Booking
from django.db.models import Exists, OuterRef

def explore_rooms(request):
    districts = District.objects.all().order_by('name')

    # Subquery: check confirmed booking
    confirmed_booking = Booking.objects.filter(
        room=OuterRef('pk'),
        status='Confirmed'
    )

    rooms = PGRoom.objects.annotate(
        is_booked=Exists(confirmed_booking)
    ).order_by('-created_at')

    selected_district = request.GET.get('district')

    if selected_district:
        rooms = rooms.filter(district_id=selected_district)

    context = {
        'districts': districts,
        'rooms': rooms,
        'selected_district': selected_district
    }

    return render(request, 'explore_room.html', context)
    
    
from django.shortcuts import render, get_object_or_404
from .models import PGRoom, Review

def view_room(request, id):
    room = get_object_or_404(PGRoom, id=id)
    reviews = Review.objects.filter(room=room, is_approved=True)

    return render(request, 'view_room_detail.html', {
        'room': room,
        'reviews': reviews
    })
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PGRoom, Booking


@login_required(login_url='login')
def book_room(request, room_id):
    room = get_object_or_404(PGRoom, id=room_id)

    # 🔴 If room already booked → show already_booked page
    if not room.is_available:
        return render(request, 'already_booked.html', {'room': room})

    # 🟢 If form submitted
    if request.method == "POST":

        booking_name = request.POST.get('booking_name')
        people_count = request.POST.get('people_count')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        aadhaar_number = request.POST.get('aadhaar')   # must match form
        mobile_number = request.POST.get('mobile')
        total_amount = request.POST.get('total_amount')

        if not all([booking_name, people_count, from_date, to_date, aadhaar_number, mobile_number]):
            messages.error(request, "All fields are required.")
            return render(request, 'booking_form.html', {'room': room})

        # ✅ Create booking
        booking = Booking.objects.create(
            user=request.user,
            room=room,
            booking_name=booking_name,
            people_count=int(people_count),
            from_date=from_date,
            to_date=to_date,
            aadhaar_number=aadhaar_number,
            mobile_number=mobile_number,
            total_amount=total_amount if total_amount else room.price,
            status='Confirmed'
        )

        # 🔒 Mark room as not available
        room.is_available = False
        room.save()

        # ✅ Go to success page
        return render(request, 'cone.html', {
            'room': room,
            'booking': booking
        })

    return render(request, 'booking_form.html', {'room': room})
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from django.conf import settings
import os
from datetime import datetime
from .models import PGRoom


def generate_bill_pdf(request, room_id):
    room = get_object_or_404(PGRoom, id=room_id)

    if request.method == "POST":
        name = request.POST.get("name")
        people = request.POST.get("people")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        aadhar = request.POST.get("aadhar")
        mobile = request.POST.get("mobile")

        # Calculate total cost
        d1 = datetime.strptime(from_date, "%Y-%m-%d")
        d2 = datetime.strptime(to_date, "%Y-%m-%d")
        diff_days = (d2 - d1).days
        months = diff_days / 30
        total_cost = round(float(room.price) * months)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Booking_Bill.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()

        # Bill Title
        elements.append(Paragraph("<b>MAHANIVAS BOOKING BILL</b>", styles['Title']))
        elements.append(Spacer(1, 20))

        # Booking Table Data
        data = [
            ["Room Title", room.title],
            ["District", room.district.name],
            ["Booking Name", name],
            ["No. of People", people],
            ["From Date", from_date],
            ["To Date", to_date],
            ["Monthly Cost", f"₹ {room.price}"],
            ["Total Amount", f"₹ {total_cost}"],
            ["Mobile", mobile],
            ["Aadhar", aadhar],
            ["Payment Mode", "Offline (On the Spot)"],
        ]

        table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ]))

        elements.append(table)

        # Add background logo with opacity
        def add_background(canvas, doc):
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')  # keep logo here

            if os.path.exists(logo_path):
                canvas.saveState()
                canvas.setFillAlpha(0.08)  # 🔹 opacity
                canvas.drawImage(
                    logo_path,
                    150, 250,
                    width=300,
                    height=300,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                canvas.restoreState()

        doc.build(elements, onFirstPage=add_background)

        return response
    
    
    
    
    
    
    
    
    
from django.shortcuts import render

def already_booked(request):
    """
    Page shown when a user tries to book a room that's already booked.
    """
    return render(request, 'already_booked.html')

@login_required
def congratulations(request, room_id):
    booking = Booking.objects.filter(user=request.user, room_id=room_id).last()
    return render(request, "cone.html", {"booking": booking, "room": booking.room})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking  # Make sure Booking model exists

# ================= VIEW BOOKING =================
@login_required
def view_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_detail.html', {'booking': booking})

# ================= DELETE BOOKING =================
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking, PGRoom

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room
    booking.delete()  # delete the booking
    room.is_available = True  # mark room as available again
    room.save()
    messages.success(request, f"Booking for room '{room.title}' deleted successfully!")
    return redirect('admin_dashboard')



from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, Review, Complaint
from django.contrib.auth.decorators import login_required

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-from_date')
    return render(request, 'booking_history.html', {'bookings': bookings})

@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        Review.objects.create(user=request.user, room=booking.room, rating=rating, comment=comment)
    return redirect('booking_history')

@login_required
def add_complaint(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        complaint_text = request.POST.get("complaint")
        Complaint.objects.create(user=request.user, room=booking.room, complaint=complaint_text)
    return redirect('booking_history')


# accounts/views.py
from django.shortcuts import render, get_object_or_404
from .models import PGRoom

def ad_total_room_view(request, room_id):
    # Only allow admin users
    if not request.user.is_superuser:
        return redirect('home')  # or any access denied page

    room = get_object_or_404(PGRoom, id=room_id)
    return render(request, 'admin/ad_view_room.html', {
        'room': room
    })
    
    
    
    
    
    
    
from django.shortcuts import render
from .models import Review
from django.contrib.auth.decorators import login_required

@login_required
def unapproved_review_view(request):
    # Only superusers can see this
    if not request.user.is_superuser:
        return redirect('home')
    
    reviews = Review.objects.filter(is_approved=False)
    
    return render(request, 'admin/unapproved_review.html', {
        'reviews': reviews
    })
    
    
    
    
    
    
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review

# ================= APPROVE REVIEW =================
@login_required
def approve_review(request, review_id):
    if not request.user.is_superuser:
        return redirect('home')

    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()
    messages.success(request, "Review approved successfully.")
    return redirect('unapproved_reviews')


# ================= REJECT REVIEW =================
@login_required
def reject_review(request, review_id):
    if not request.user.is_superuser:
        return redirect('home')

    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, "Review rejected and deleted.")
    return redirect('unapproved_reviews')


# ================= UNAPPROVED REVIEWS PAGE =================
@login_required
def unapproved_review_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    reviews = Review.objects.filter(is_approved=False)
    return render(request, 'admin/unapproved_review.html', {'reviews': reviews})



from django.contrib.auth.decorators import login_required
from .models import Complaint

@login_required
def raise_complaint(request, room_id):
    room = get_object_or_404(PGRoom, id=room_id)

    if request.method == "POST":
        complaint_text = request.POST.get("complaint_text")

        Complaint.objects.create(
            room=room,
            user=request.user,
            complaint_text=complaint_text
        )

    return redirect('view_room', id=room.id)




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking

@login_required(login_url='login')
def manage_bookings(request):
    if not request.user.is_superuser:
        return redirect('home')

    bookings = Booking.objects.all().order_by('-created_at')

    return render(request, 'manage_bookings.html', {
        'bookings': bookings
    })
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking

def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room

    if request.method == "POST":
        new_status = request.POST.get('status')

        booking.status = new_status
        booking.save()

        # 🔒 If confirmed → lock room
        if new_status == "Confirmed":
            room.is_available = False
            room.save()

        # 🔓 If cancelled → unlock room
        elif new_status == "Cancelled":
            room.is_available = True
            room.save()

        messages.success(request, "Booking updated successfully.")

    return redirect('manage_bookings')
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking


def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    room = booking.room   # get related room

    if request.method == "POST":
        # ✅ Make room available again
        room.is_available = True
        room.save()

        # ✅ Delete booking
        booking.delete()

        messages.success(request, "Booking deleted. Room is available again.")
        return redirect('manage_bookings')

    return redirect('manage_bookings')


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == "POST":
        review.is_approved = True
        review.save()

    return redirect("unapproved_reviews")



def about_us(request):
    return render(request, "aboutus.html")


# accounts/views.py
from django.shortcuts import render

def contact_us_view(request):
    return render(request, 'contact_us.html')

from django.shortcuts import render

def services_view(request):
    """
    Render the Services page for users.
    """
    return render(request, "services.html")