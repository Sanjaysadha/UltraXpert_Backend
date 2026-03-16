import os
import sys
from datetime import datetime

# Add the backend directory to sys.path so we can import our modules
sys.path.append('/Users/sanjaysadha/Desktop/backend')

from core.report_generator import generate_medical_report_pdf

# Mock objects to simulate SQLAlchemy models
class MockPatient:
    def __init__(self):
        self.patient_identifier = "P-8748"
        self.name = "Test Patient"
        self.age = "21"
        self.gender = "Male"

class MockReport:
    def __init__(self):
        self.id = "test-report-id"
        self.scan_type = "Ultrasound Scan"
        self.modality = "Ultrasound"
        self.body_part = "Abdomen"
        self.status = "Completed"
        self.findings = "Scan enhanced and processed successfully. No significant abnormalities detected in the visualized abdominal regions. Organs appear normal in size and texture."
        self.impression = "Normal abdominal ultrasound scan."
        self.recommendations = "Clinical correlation recommended. Follow-up scan in 6 months if symptoms persist."
        self.created_at = datetime.now()

def create_sample_pdf():
    os.makedirs('exports', exist_ok=True)
    file_path = 'exports/test.pdf'
    
    patient = MockPatient()
    report = MockReport()
    
    print(f"Generating sample professional PDF at {file_path}...")
    generate_medical_report_pdf(
        report_obj=report,
        patient_obj=patient,
        doctor_full_name="Dr. Smith (Self-Referred)",
        file_path=file_path,
        enhanced_image_path=None, # No image for mock
        include_notes=True
    )
    print("Done!")

if __name__ == "__main__":
    create_sample_pdf()
