from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='profiles/', default='profiles/default.png')

    def __str__(self):
        return self.user.username


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('Diabetic Care', 'Diabetic Care'),
        ('OTC Medicine', 'OTC Medicine'),
        ('Pain Relief', 'Pain Relief'),
        ('Vitamins & Supplements', 'Vitamins & Supplements'),
        ('Womens Care', 'Womens Care'),
        ('Cold & Flu', 'Cold & Flu'),
        ('Skin Care', 'Skin Care'),
        ('Others', 'Others'),
    ]

    TYPE_CHOICES = [
        ('Tablet', 'Tablet'),
        ('Syrup', 'Syrup'),
        ('Capsule', 'Capsule'),
        ('Injection', 'Injection'),
        ('Cream', 'Cream'),
        ('Gel', 'Gel'),
        ('Others', 'Others'),
    ]

    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    image = models.ImageField(upload_to='medicines/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    dosage_mg = models.PositiveIntegerField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='carts')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.medicine.price * self.quantity  # Calculate price based on quantity

    def __str__(self):
        return f"{self.user.username} - {self.medicine.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    medicines = models.ManyToManyField('Medicine', through='OrderItem', related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    tracking_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    courier_name = models.CharField(max_length=50, blank=True, null=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Generate a unique tracking number if it's not set."""
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4())[:12]  # Generate a 12-character tracking number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.order.user.username} - {self.medicine.name}"



class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    qualifications = models.TextField()
    image = models.ImageField(upload_to='doctors/')
    
    def __str__(self):
        return self.name

class Hospital(models.Model):
    doctor = models.ManyToManyField(Doctor, related_name='hospitals')
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='hospitals/')

    def __str__(self):
        return self.name

class Schedule(models.Model):
    # doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    # hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='schedules')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='schedules')
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='schedules')
    start_time = models.TimeField()
    end_time = models.TimeField()
    days_available = models.CharField(max_length=255) 
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    pay_first = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.name} at {self.hospital.name}"
    

class Appointment (models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='appointments')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='appointments')
    patient_contact = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()

    STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled')
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.patient.username} - {self.doctor.name} at {self.hospital.name}"


from django.contrib.auth import get_user_model

User = get_user_model()

class LabTest(models.Model):
    # Define the available lab tests
    TEST_CHOICES = [
        ('CBC', 'Complete blood count (CBC)'),
        ('ALT', 'Alanine transaminase (ALT)'),
        ('TSH', 'Thyroid stimulating hormone (TSH)'),
        ('TgAb', 'Thyroglobulin antibodies (TgAb)'),
        ('Glucose', 'Blood sugar (glucose) tests'),
        ('B12', 'Vitamin B12'),
    ]

    name = models.CharField(max_length=100, unique=True, choices=TEST_CHOICES)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.get_name_display()  # Display the human-readable name

class LabBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.TimeField()
    patient_name = models.CharField(max_length=100, default='Unknown') # New field
    phone_number = models.CharField(max_length=15, default='0000000000')   # New field
    address = models.TextField(default='Not provided')                    # New field

    def __str__(self):
        return f"{self.patient_name} - {self.test.get_name_display()} - {self.date} {self.time_slot}"


