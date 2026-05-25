from rest_framework import serializers
from .models import *


class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user", "created_by", "updated_by"]

    def get_full_address(self, obj):
        return f"{obj.house_no}, {obj.area_street}, {obj.locality}, {obj.city}, {obj.state} - {obj.pincode}"



class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    default_address = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'full_name', 'contact_number','alternate_contact_number', 
            'profile_picture', 'is_verify','addresses', 'default_address','created_at']
        read_only_fields = ['id', 'email', 'is_verify', 'created_at']
    
    def get_default_address(self, obj):
        default = obj.get_default_address()
        if default:
            return AddressSerializer(default).data
        return None


