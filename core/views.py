from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Doctor, Patient, PatientDoctorMapping
from .serializers import DoctorSerializer, LoginSerializer, MappingSerializer, PatientSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = RefreshToken.for_user(serializer.validated_data["user"])
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class MappingViewSet(viewsets.ModelViewSet):
    serializer_class = MappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.select_related("patient", "doctor").filter(patient__created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        mappings = self.get_queryset().filter(patient_id=kwargs["pk"])
        return Response(self.get_serializer(mappings, many=True).data)