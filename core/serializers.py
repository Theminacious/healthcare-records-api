from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Doctor, Patient, PatientDoctorMapping, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "name", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "age", "gender", "contact", "address", "created_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_age(self, value):
        if value > 130:
            raise serializers.ValidationError("Age must be 130 or less.")
        return value


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialty", "contact", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MappingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "patient_name", "doctor", "doctor_name", "assigned_at"]
        read_only_fields = ["id", "patient_name", "doctor_name", "assigned_at"]

    def validate(self, attrs):
        request = self.context["request"]
        if attrs["patient"].created_by_id != request.user.id:
            raise serializers.ValidationError({"patient": "You can only assign doctors to your own patients."})
        if PatientDoctorMapping.objects.filter(**attrs).exists():
            raise serializers.ValidationError("This doctor is already assigned to the patient.")
        return attrs