import requests
class Patient:
    pass
class Bundle:
    pass

# Below code was written by git copilot and does not work out of the gate
class FHIRBridge:
    def __init__(self, fhir_server_url: str, fhir_server_auth: str):
        self.fhir_server_url = fhir_server_url
        self.fhir_server_auth = fhir_server_auth

    def get_patient(self, patient_id: str) -> Patient:
        response = requests.get(
            f"{self.fhir_server_url}/Patient/{patient_id}",
            headers={"Authorization": self.fhir_server_auth},
        )
        response.raise_for_status()
        return Patient.parse_raw(response.text)

    def get_patient_medication_statements(
        self, patient_id: str
    ) -> Bundle[MedicationStatement]:
        response = requests.get(
            f"{self.fhir_server_url}/MedicationStatement?patient={patient_id}",
            headers={"Authorization": self.fhir_server_auth},
        )
        response.raise_for_status()
        return Bundle.parse_raw(response.text)

    def get_patient_medication_request(
        self, patient_id: str
    ) -> Bundle[MedicationRequest]:
        response = requests.get(
            f"{self.fhir_server_url}/MedicationRequest?patient={patient_id}",
            headers={"Authorization": self.fhir_server_auth},
        )
        response.raise_for_status()
        return Bundle.parse_raw(response.text)

    def get_patient_medication_administrations(
        self, patient_id: str
    ) -> Bundle[MedicationAdministration]:
        response = requests.get(
            f"{self.fhir_server_url}/MedicationAdministration?patient={patient_id}",
            headers={"Authorization": self.fhir_server_auth},
        )
        response.raise_for_status()
        return Bundle.parse_raw(response.text)

    def get_patient_medication_dispenses(
        self, patient_id: str
    ) -> Bundle[MedicationDispense]:
        response = requests.get(
            f"{self.fhir_server_url}/MedicationDispense?patient={patient_id}",
            headers={"Authorization": self.fhir_server})