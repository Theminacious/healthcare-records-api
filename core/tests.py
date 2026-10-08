from rest_framework import status
from rest_framework.test import APITestCase

from .models import Doctor, Patient


class HealthcareAPITests(APITestCase):
    def setUp(self):
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.user_data = {"name": "Ava Carter", "email": "ava@example.com", "password": "strong-pass-123"}

    def authenticate(self, data=None):
        response = self.client.post(self.login_url, data or self.user_data, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_register_login_and_patient_ownership(self):
        self.assertEqual(self.client.post(self.register_url, self.user_data, format="json").status_code, status.HTTP_201_CREATED)
        self.authenticate()
        patient = self.client.post("/api/patients/", {"name": "Sam Carter", "age": 35, "gender": "other", "contact": "555-0100", "address": "1 Main St"}, format="json")
        self.assertEqual(patient.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.get("/api/patients/").data["count"], 1)

    def test_mapping_is_unique_and_patient_scoped(self):
        registration = self.client.post(self.register_url, self.user_data, format="json")
        self.authenticate()
        patient = Patient.objects.create(name="Sam Carter", age=35, gender="other", contact="555-0100", address="1 Main St", created_by_id=registration.data["id"])
        doctor = Doctor.objects.create(name="Dr. Lee", specialty="Cardiology", contact="555-0110")
        payload = {"patient": patient.id, "doctor": doctor.id}
        self.assertEqual(self.client.post("/api/mappings/", payload, format="json").status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.post("/api/mappings/", payload, format="json").status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f"/api/mappings/{patient.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)