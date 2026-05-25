from django.db import models
from django.contrib.auth.models import AbstractUser



# class CustomUser(AbstractUser):

#     username = models.CharField(max_length=150, unique=True)
#     email = models.EmailField(unique=True)

#     totp_secret = models.CharField(max_length=50, blank=True, null=True)
#     verify_code = models.CharField(max_length=128, blank=True, null=True)
#     verify_code_expire_at = models.DateTimeField(blank=True, null=True)
#     contact_number = models.CharField(max_length=10, null=True, blank=True)
#     alternate_contact_number = models.CharField(max_length=10, null=True, blank=True)
#     notes = models.TextField(null=True, blank=True)
#     is_verify = models.BooleanField(default=False)

#     # ⭐ IMPORTANT
#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["username"]

#     def __str__(self):
#         return self.email

#     class Meta:
#         db_table = "sa_custom_user"


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    alternate_contact_number = models.CharField(max_length=15, blank=True, null=True)
    verify_code = models.CharField(max_length=128, blank=True, null=True)
    verify_code_expire_at = models.DateTimeField(blank=True, null=True)
    is_verify = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    class Meta:
        db_table = "sa_custom_user"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.full_name or self.username
    
    def get_default_address(self):
        return self.addresses.filter(is_default=True, is_deleted=False).first()
    
    def get_all_addresses(self):
        return self.addresses.filter(is_deleted=False)



class SMTPMail(models.Model):
    smtp_id = models.AutoField(primary_key=True)
    action_type = models.CharField(max_length=255, null=True, blank=True)
    action_id  = models.IntegerField(null=True, blank=True)
    smtp_host = models.CharField(max_length=255, null=True, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    encryption_type = models.CharField(max_length=255, null=True, blank=True)
    smtp_host_user = models.CharField(max_length=255, null=True, blank=True)
    smtp_host_password = models.CharField(max_length=255, null=True, blank=True)
    from_email = models.CharField(max_length=255, null=True, blank=True)
    smtp_type = models.CharField(max_length=255, default='GENRAL',null=True, blank=True)
    verify_code = models.CharField(max_length=128, blank=True, null=True)
    verify_code_expire_at = models.DateTimeField(blank=True, null=True)
    is_deactive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sa_smtp_mail'




class Address(models.Model):

    ADDRESS_TYPE_CHOICES = [
        ('HOME', 'Home'),
        ('OFFICE', 'Office'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='addresses')
    house_no = models.CharField(max_length=255)
    area_street = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="India")
    contact_name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=15)
    address_type = models.CharField(max_length=10,choices=ADDRESS_TYPE_CHOICES,default="HOME")
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser,null=True,on_delete=models.SET_NULL,related_name="address_created")
    updated_by = models.ForeignKey(CustomUser,null=True,on_delete=models.SET_NULL,related_name="address_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sa_address"
        ordering = ["-is_default", "-created_at"]

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user,is_default=True,is_deleted=False).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.house_no}, {self.city} - {self.pincode}"