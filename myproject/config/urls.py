"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),

    path('home/', views.home_view, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('logout/', views.logout_view, name='logout'),
    path('approve-kyc/<int:profile_id>/', views.approve_kyc, name='approve_kyc'),
path('reject-kyc/<int:profile_id>/', views.reject_kyc, name='reject_kyc'),
path('accept-review/<int:review_id>/', views.accept_review, name='accept_review'),
path('resolve-complaint/<int:complaint_id>/', views.resolve_complaint, name='resolve_complaint'),
path('add-room/', views.add_room, name='add_room'),
path("dashboard/addroom/", views.add_room, name="add_room"),
   path('districts/', views.district_list, name="district_list"),
    path('districts/add/', views.add_district, name="add_district"),
      path('total-rooms/', views.total_rooms_view, name='total_rooms'),
    path('view-room/<int:room_id>/', views.view_room_view, name='view_room'),
path('edit-room/<int:id>/', views.edit_room, name='edit_room'),
path('delete-room/<int:id>/', views.delete_room, name='delete_room'),
path('district/delete/<int:id>/', views.delete_district, name='delete_district'),
  path('explore-rooms/', views.explore_rooms, name='explore_rooms'),
  path('room/<int:id>/', views.view_room, name='view_room'),
  path('book-room/<int:room_id>/', views.book_room, name='book_room'),
  path('generate-bill/<int:room_id>/', views.generate_bill_pdf, name='generate_bill'),
   path('already-booked/', views.already_booked, name='already_booked'),
   path('congratulations/<int:room_id>/', views.congratulations, name='congratulations'),
   # bookings URLs
path('booking/view/<int:booking_id>/', views.view_booking, name='view_booking'),
path('booking/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
path('booking-history/', views.booking_history, name='booking_history'),
    path('booking/<int:booking_id>/review/', views.add_review, name='add_review'),
    path('booking/<int:booking_id>/complaint/', views.add_complaint, name='add_complaint'),
    # Admin-specific room view
# config/urls.py
path('admin-rooms/view-room/<int:room_id>/', views.ad_total_room_view, name='ad_view_room'),
# URL to show unapproved reviews
# Admin URLs for reviews
path('admin-rooms/unapproved-reviews/', views.unapproved_review_view, name='unapproved_reviews'),
path('admin-rooms/approve-review/<int:review_id>/', views.approve_review, name='approve_review'),
path('admin-rooms/reject-review/<int:review_id>/', views.reject_review, name='reject_review'),
path('raise-complaint/<int:room_id>/', views.raise_complaint, name='raise_complaint'),

    path('admin/review/approve/<int:review_id>/', views.approve_review, name='approve_review'),
    path('admin/complaint/resolve/<int:complaint_id>/', views.resolve_complaint, name='resolve_complaint'),
    path('manage-bookings/', views.manage_bookings, name='manage_bookings'),
path('update-booking-status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
path('review/approve/<int:review_id>/', views.approve_review, name='approve_review'),
path('about-us/', views.about_us, name='about_us'),

path('contact-us/', views.contact_us_view, name='contact_us'),
 path('services/', views.services_view, name='services'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)