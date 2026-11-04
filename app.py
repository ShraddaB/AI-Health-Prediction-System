
from flask import Flask, render_template, request, redirect, url_for, flash
from database import db, Patient, RejectedPatient
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
from google import genai
import os
import math
import time


# ------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# ------------------------------------------
# AI HEALTH ANALYSIS FUNCTION
# ------------------------------------------

def generate_health_remarks(glucose, haemoglobin, cholesterol):

    if client is None:
        return "AI analysis unavailable. Please configure the Gemini API key."

    prompt = f"""
    You are an AI health information assistant.

    Review these patient blood test values:

    Glucose: {glucose}
    Haemoglobin: {haemoglobin}
    Cholesterol: {cholesterol}

    Instructions:
    1. Explain what each measurement generally relates to.
    2. Mention that units, test type and laboratory reference ranges
       were not provided, so reliable interpretation is limited.
    3. Do not diagnose any disease.
    4. Recommend consulting a qualified healthcare professional.
    5. Keep the response concise and within 100 words.
    """

    for attempt in range(3):

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            return response.text or "AI could not generate health remarks."

        except Exception as error:

            print("\n========== GEMINI API ERROR ==========")
            print("ERROR TYPE:", type(error).__name__)
            print("ERROR DETAILS:", str(error))
            print("======================================\n")

            error_message = str(error)

            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "high demand" in error_message.lower()
            ):

                if attempt < 2:
                    wait_seconds = 2 ** (attempt + 1)

                    print(
                        f"Gemini is busy. Retrying in {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)
                    continue

            break

    return "AI analysis temporarily unavailable. Please try again later."


# ------------------------------------------
# FLASK APPLICATION CONFIGURATION
# ------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY", "development-secret-key"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///patients.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ------------------------------------------
# HOME PAGE - WELCOME PAGE
# ------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


# ------------------------------------------
# ADD PATIENT FORM PAGE
# ------------------------------------------

@app.route("/add-patient-form")
def add_patient_form():

    return render_template("add_patient.html")


# ------------------------------------------
# PATIENT DASHBOARD
# ------------------------------------------

@app.route("/dashboard")
def dashboard():

    patients = Patient.query.order_by(
        Patient.id.desc()
    ).all()

    rejected_count = RejectedPatient.query.count()

    return render_template(
        "dashboard.html",
        patients=patients,
        rejected_count=rejected_count
    )


# ------------------------------------------
# REJECTED PATIENT RECORDS
# ------------------------------------------

@app.route("/rejected-patients")
def rejected_patients():

    rejected_records = RejectedPatient.query.order_by(
        RejectedPatient.id.desc()
    ).all()

    return render_template(
        "rejected_patients.html",
        rejected_records=rejected_records
    )


# ------------------------------------------
# ADD PATIENT WITH VALIDATION
# ------------------------------------------

@app.route("/add-patient", methods=["POST"])
def add_patient():

    full_name = request.form.get("full_name", "").strip()
    dob = request.form.get("date_of_birth", "").strip()
    email = request.form.get("email", "").strip()

    glucose_raw = request.form.get("glucose", "").strip()
    haemoglobin_raw = request.form.get("haemoglobin", "").strip()
    cholesterol_raw = request.form.get("cholesterol", "").strip()

    errors = []

    # Validate patient name
    if not full_name:
        errors.append("Patient name is required.")

    # Validate email
    try:
        validate_email(
            email,
            check_deliverability=False
        )
    except EmailNotValidError:
        errors.append("Invalid email address.")

    # Validate date of birth
    date_of_birth = None

    try:
        try:
            date_of_birth = datetime.strptime(
                dob, "%d/%m/%Y"
            ).date()
        except ValueError:
            date_of_birth = datetime.strptime(
                dob, "%d.%m.%Y"
            ).date()

        if date_of_birth > date.today():
            errors.append("Date of birth cannot be in the future.")

    except ValueError:
        errors.append(
            "Invalid date. Please use DD/MM/YYYY format."
        )

    # Validate blood test values
    blood_values = {}

    for field, raw_value in [
        ("Glucose", glucose_raw),
        ("Haemoglobin", haemoglobin_raw),
        ("Cholesterol", cholesterol_raw)
    ]:

        try:
            number = float(raw_value)

            if not math.isfinite(number) or number <= 0:
                raise ValueError

            blood_values[field] = number

        except ValueError:
            errors.append(
                f"{field} must be a valid positive number."
            )

    # SAVE REJECTED PATIENT IF ERRORS EXIST

    if errors:

        rejected_patient = RejectedPatient(
            full_name=full_name or "Not provided",
            date_of_birth=dob,
            email=email,
            glucose=glucose_raw,
            haemoglobin=haemoglobin_raw,
            cholesterol=cholesterol_raw,
            rejection_reason="; ".join(errors)
        )

        try:
            db.session.add(rejected_patient)
            db.session.commit()

            flash(
                "Patient entry rejected and saved. Reasons: "
                + " ".join(errors),
                "danger"
            )

        except Exception as error:
            db.session.rollback()

            print("Rejected record database error:", error)

            flash(
                "Invalid entry could not be saved in rejected records.",
                "danger"
            )

        return redirect(url_for("add_patient_form"))

    # GENERATE AI HEALTH REMARKS

    ai_remarks = generate_health_remarks(
        blood_values["Glucose"],
        blood_values["Haemoglobin"],
        blood_values["Cholesterol"]
    )

    # CREATE VALID PATIENT RECORD

    patient = Patient(
        full_name=full_name,
        date_of_birth=date_of_birth,
        email=email,
        glucose=blood_values["Glucose"],
        haemoglobin=blood_values["Haemoglobin"],
        cholesterol=blood_values["Cholesterol"],
        remarks=ai_remarks
    )

    try:
        db.session.add(patient)
        db.session.commit()

        flash(
            "Patient registered successfully!",
            "success"
        )

    except Exception as error:
        db.session.rollback()

        print("Database error:", error)

        flash(
            "Unable to save patient record.",
            "danger"
        )

        return redirect(url_for("add_patient_form"))

    return redirect(url_for("dashboard"))


# ------------------------------------------
# EDIT PATIENT
# ------------------------------------------

@app.route(
    "/edit-patient/<int:patient_id>",
    methods=["GET", "POST"]
)
def edit_patient(patient_id):

    patient = Patient.query.get_or_404(patient_id)

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        dob = request.form.get("date_of_birth", "").strip()

        try:

            if not full_name:
                raise ValueError("Name is required")

            validate_email(
                email,
                check_deliverability=False
            )

            date_of_birth = datetime.strptime(
                dob, "%d/%m/%Y"
            ).date()

            if date_of_birth > date.today():
                raise ValueError("Future date is not allowed")

            glucose = float(request.form.get("glucose", ""))
            haemoglobin = float(request.form.get("haemoglobin", ""))
            cholesterol = float(request.form.get("cholesterol", ""))

            values = [
                glucose,
                haemoglobin,
                cholesterol
            ]

            if not all(
                math.isfinite(value) and value > 0
                for value in values
            ):
                raise ValueError("Invalid blood values")

        except (ValueError, EmailNotValidError):

            flash(
                "Please enter valid patient details.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_patient",
                    patient_id=patient.id
                )
            )

        # Check whether blood values changed
        blood_values_changed = (
            patient.glucose != glucose
            or patient.haemoglobin != haemoglobin
            or patient.cholesterol != cholesterol
        )

        # Update patient details
        patient.full_name = full_name
        patient.email = email
        patient.date_of_birth = date_of_birth
        patient.glucose = glucose
        patient.haemoglobin = haemoglobin
        patient.cholesterol = cholesterol

        # Regenerate AI remarks only when blood values change
        if blood_values_changed:

            patient.remarks = generate_health_remarks(
                glucose,
                haemoglobin,
                cholesterol
            )

        try:
            db.session.commit()

            flash(
                "Patient details updated successfully!",
                "success"
            )

        except Exception as error:
            db.session.rollback()

            print("Database error:", error)

            flash(
                "Unable to update patient record.",
                "danger"
            )

            return redirect(url_for("dashboard"))

        return redirect(url_for("dashboard"))

    return render_template(
        "edit_patient.html",
        patient=patient
    )


# ------------------------------------------
# DELETE PATIENT
# ------------------------------------------

@app.route(
    "/delete-patient/<int:patient_id>",
    methods=["POST"]
)
def delete_patient(patient_id):

    patient = Patient.query.get_or_404(patient_id)

    try:
        db.session.delete(patient)
        db.session.commit()

        flash(
            "Patient record deleted successfully!",
            "success"
        )

    except Exception as error:
        db.session.rollback()

        print("Database error:", error)

        flash(
            "Unable to delete patient record.",
            "danger"
        )

    return redirect(url_for("dashboard"))


# ------------------------------------------
# RUN APPLICATION
# ------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
