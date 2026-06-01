from django.contrib import admin
from .models import (
    District,
    UserProfile,
    PGRoom,
    RoomImage,
    Review,
    Complaint,
    Booking,
    ContactMessage
)

# 1️⃣ District
admin.site.register(District)

# 2️⃣ User Profile
admin.site.register(UserProfile)

# 3️⃣ PG Room
class PGRoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'price', 'is_available', 'is_trending')
    list_filter = ('district', 'is_available', 'vibe_tag')
    search_fields = ('title', 'address')

admin.site.register(PGRoom, PGRoomAdmin)

# 4️⃣ Room Images
admin.site.register(RoomImage)

# 5️⃣ Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('room__title', 'user__username')

admin.site.register(Review, ReviewAdmin)

# 6️⃣ Complaint
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'room__title')

admin.site.register(Complaint, ComplaintAdmin)

# 7️⃣ Booking
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_name', 'room', 'user', 'status', 'from_date', 'to_date')
    list_filter = ('status',)
    search_fields = ('booking_name', 'room__title', 'user__username')

admin.site.register(Booking, BookingAdmin)

# 8️⃣ Contact Messages
admin.site.register(ContactMessage)