from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(LabBooking)
class LabBookingAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'test', 'date', 'time_slot')
    list_filter = ('date', 'test')
    search_fields = ('patient_name', 'phone_number')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Displayed columns in the list view
    list_display = (
        'patient',
        'doctor',
        'hospital',
        'date',
        'time',
        'status',
        'created_at'
    )

    # Filter options (right sidebar)
    list_filter = (
        'status',
        'date',
        'doctor',
        'hospital',
    )

    # Searchable fields
    search_fields = (
        'patient__username',
        'doctor__name',
        'hospital__name',
    )

    # Default ordering (newest first)
    ordering = ('-created_at',)

    # Fields to display in the edit form (grouped logically)
    fieldsets = (
        ('Appointment Details', {
            'fields': (
                'patient',
                'doctor',
                'hospital',
                'schedule',
            ),
        }),
        ('Date & Time', {
            'fields': (
                'date',
                'time',
            ),
        }),
        ('Status', {
            'fields': (
                'status',
                'patient_contact',
            ),
        }),
    )

    # Pre-populate patient_contact from the user's profile (if available)
    def save_model(self, request, obj, form, change):
        if not obj.patient_contact and obj.patient.profile.phone:
            obj.patient_contact = obj.patient.profile.phone
        super().save_model(request, obj, form, change)

from django.contrib import admin
from django.contrib.auth.models import User, Group  # Added Group import
from django.db.models import Q
from .models import Profile, Appointment, Order, LabBooking  # Ensure all models are imported

class UserTypeFilter(admin.SimpleListFilter):
    title = 'User Type'
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        return (
            ('admin', 'Admin'),
            ('customer', 'Customer'),
            ('patient', 'Patient'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'admin':
            return queryset.filter(user__is_staff=True)
        elif self.value() == 'customer':
            order_users = Order.objects.values_list('user', flat=True).distinct()
            lab_users = LabBooking.objects.values_list('user', flat=True).distinct()
            patient_users = Appointment.objects.values_list('patient', flat=True).distinct()
            customer_users = set(order_users).union(set(lab_users)) - set(patient_users)
            return queryset.filter(user__id__in=customer_users)
        elif self.value() == 'patient':
            patient_users = Appointment.objects.values_list('patient', flat=True).distinct()
            return queryset.filter(user__id__in=patient_users)
        return queryset

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'user_type', 'is_patient', 'is_customer',
                   'appointment_count', 'order_count', 'lab_booking_count')
    list_filter = (UserTypeFilter,)
    search_fields = ('user__username', 'phone', 'address', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
    list_select_related = ('user',)

    fieldsets = (
        (None, {
            'fields': ('user', 'phone', 'address')
        }),
        ('Additional Info', {
            'fields': ('date_of_birth', 'gender'),
            'classes': ('collapse',)
        }),
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term.lower() == 'patient':
            patient_users = Appointment.objects.values_list('patient', flat=True).distinct()
            queryset = queryset.filter(user__id__in=patient_users)
        elif search_term.lower() == 'customer':
            order_users = Order.objects.values_list('user', flat=True).distinct()
            lab_users = LabBooking.objects.values_list('user', flat=True).distinct()
            patient_users = Appointment.objects.values_list('patient', flat=True).distinct()
            customer_users = set(order_users).union(set(lab_users)) - set(patient_users)
            queryset = queryset.filter(user__id__in=customer_users)

        return queryset, use_distinct

    def user_type(self, obj):
        if obj.user.is_staff:
            return "Admin"
        elif self.is_patient(obj):
            return "Patient"
        elif self.is_customer(obj):
            return "Customer"
        return "Regular User"

    user_type.short_description = 'User Type'

    def is_patient(self, obj):
        return Appointment.objects.filter(patient=obj.user).exists()

    is_patient.boolean = True
    is_patient.short_description = 'Is Patient'

    def is_customer(self, obj):
        return (Order.objects.filter(user=obj.user).exists() or
                LabBooking.objects.filter(user=obj.user).exists())

    is_customer.boolean = True
    is_customer.short_description = 'Is Customer'

    def appointment_count(self, obj):
        count = Appointment.objects.filter(patient=obj.user).count()
        return count if count > 0 else "-"

    appointment_count.short_description = 'Appointments'

    def order_count(self, obj):
        count = Order.objects.filter(user=obj.user).count()
        return count if count > 0 else "-"

    order_count.short_description = 'Orders'

    def lab_booking_count(self, obj):
        count = LabBooking.objects.filter(user=obj.user).count()
        return count if count > 0 else "-"

    lab_booking_count.short_description = 'Lab Bookings'

def setup_groups():
    Group.objects.get_or_create(name='Customers')
    Group.objects.get_or_create(name='Patients')

setup_groups()

admin.site.register(Medicine)
admin.site.register(Doctor)
admin.site.register(Hospital)
admin.site.register(Schedule)
admin.site.register(Order)
admin.site.register(OrderItem)
# admin.site.register(Profile)
admin.site.register(Cart)

