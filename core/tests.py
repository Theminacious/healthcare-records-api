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

    def test_patient_and_doctor_crud(self):
        self.client.post(self.register_url, self.user_data, format="json")
        self.authenticate()
        patient_data = {"name": "Sam Carter", "age": 35, "gender": "other", "contact": "555-0100", "address": "1 Main St"}
        patient = self.client.post("/api/patients/", patient_data, format="json")
        self.assertEqual(patient.status_code, status.HTTP_201_CREATED)
        patient_id = patient.data["id"]
        patient_data["age"] = 36
        self.assertEqual(self.client.put(f"/api/patients/{patient_id}/", patient_data, format="json").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(f"/api/patients/{patient_id}/").status_code, status.HTTP_204_NO_CONTENT)

        doctor = self.client.post("/api/doctors/", {"name": "Dr. Lee", "specialty": "Cardiology", "contact": "555-0110"}, format="json")
        self.assertEqual(doctor.status_code, status.HTTP_201_CREATED)
        doctor_id = doctor.data["id"]
        self.assertEqual(self.client.get(f"/api/doctors/{doctor_id}/").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.put(f"/api/doctors/{doctor_id}/", {"name": "Dr. Lee", "specialty": "Neurology", "contact": "555-0110"}, format="json").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(f"/api/doctors/{doctor_id}/").status_code, status.HTTP_204_NO_CONTENT)

    def test_protected_endpoints_require_jwt(self):
        self.assertEqual(self.client.get("/api/patients/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get("/api/doctors/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get("/api/mappings/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mapping_delete(self):
        registration = self.client.post(self.register_url, self.user_data, format="json")
        self.authenticate()
        patient = Patient.objects.create(name="Sam Carter", age=35, gender="other", contact="555-0100", address="1 Main St", created_by_id=registration.data["id"])
        doctor = Doctor.objects.create(name="Dr. Lee", specialty="Cardiology", contact="555-0110")
        mapping = self.client.post("/api/mappings/", {"patient": patient.id, "doctor": doctor.id}, format="json")
        self.assertEqual(self.client.delete(f"/api/mappings/{mapping.data['id']}/").status_code, status.HTTP_204_NO_CONTENT)

    def test_users_cannot_access_or_map_other_users_patients(self):
        self.client.post(self.register_url, self.user_data, format="json")
        self.authenticate()
        patient_response = self.client.post("/api/patients/", {"name": "Private Patient", "age": 42, "gender": "female", "contact": "555-0120", "address": "2 Main St"}, format="json")
        patient_id = patient_response.data["id"]
        doctor = Doctor.objects.create(name="Dr. Patel", specialty="Pediatrics", contact="555-0130")

        other_user = {"name": "Ben Jones", "email": "ben@example.com", "password": "strong-pass-456"}
        self.client.post(self.register_url, other_user, format="json")
        self.authenticate(other_user)
        self.assertEqual(self.client.get(f"/api/patients/{patient_id}/").status_code, status.HTTP_404_NOT_FOUND)
        mapping = self.client.post("/api/mappings/", {"patient": patient_id, "doctor": doctor.id}, format="json")
        self.assertEqual(mapping.status_code, status.HTTP_400_BAD_REQUEST)