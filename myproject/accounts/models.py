from django.db import models
from django.contrib.auth.models import User

# ==========================================================
# 1️⃣ DISTRICT MODEL
# ==========================================================
class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ==========================================================
# 2️⃣ USER PROFILE (KYC SYSTEM)
# ==========================================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='kyc/profile_pics/', blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    id_proof = models.ImageField(upload_to='kyc/id_proofs/')
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# ==========================================================
# 3️⃣ PG ROOM MODEL (CORE MODEL)
# ==========================================================
class PGRoom(models.Model):

    VIBE_CHOICES = (
        ('Peaceful', 'Peaceful'),
        ('Lively', 'Lively'),
        ('Study-friendly', 'Study-friendly'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    # Basic Info
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    main_image = models.ImageField(upload_to='rooms/main_images/')
    video_tour = models.FileField(upload_to='rooms/videos/', blank=True, null=True)

    # Vibe / Atmosphere
    vibe_tag = models.CharField(max_length=20, choices=VIBE_CHOICES)
    environment_desc = models.TextField()
    is_trending = models.BooleanField(default=False)

    # Availability
    is_available = models.BooleanField(default=True)

    # Amenities
    wifi = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    attached_bathroom = models.BooleanField(default=False)
    ac = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==========================================================
# 4️⃣ ROOM GALLERY MODEL (MULTIPLE IMAGES)
# ==========================================================
class RoomImage(models.Model):

    IMAGE_TYPE_CHOICES = (
        ('Interior', 'Interior'),
        ('Exterior', 'Exterior'),
        ('Vibe', 'Vibe'),
    )

    room = models.ForeignKey(PGRoom, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to='rooms/gallery/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)

    def __str__(self):
        return f"{self.room.title} - {self.image_type}"


# ==========================================================
# 5️⃣ REVIEW MODEL (WITH MODERATION)
# ==========================================================
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PGRoom, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField()
    review_image = models.ImageField(upload_to='reviews/images/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room.title} - {self.rating}⭐"


# ==========================================================
# 6️⃣ COMPLAINT MODEL
# ==========================================================
class Complaint(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PGRoom, on_delete=models.CASCADE)

    issue = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"
    
    
    
    
    # ==========================================================
# 7️⃣ BOOKING MODEL
# ==========================================================
class Booking(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PGRoom, on_delete=models.CASCADE)

    booking_name = models.CharField(max_length=200)
    people_count = models.IntegerField()
    from_date = models.DateField()
    to_date = models.DateField()

    aadhaar_number = models.CharField(max_length=12)
    mobile_number = models.CharField(max_length=10)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # ✅ ADD THIS
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking_name} - {self.room.title}"
    
# accounts/models.py
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"