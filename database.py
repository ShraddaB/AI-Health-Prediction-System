
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ------------------------------------------
# VALID PATIENT TABLE
# ------------------------------------------

class Patient(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    date_of_birth = db.Column(db.Date, nullable=False)

    email = db.Column(db.String(120), nullable=False)

    glucose = db.Column(db.Float, nullable=False)

    haemoglobin = db.Column(db.Float, nullable=False)

    cholesterol = db.Column(db.Float, nullable=False)

    remarks = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Patient {self.full_name}>"


# ------------------------------------------
# REJECTED PATIENT TABLE
# ------------------------------------------

class RejectedPatient(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    # Store as text because the date may be invalid
    date_of_birth = db.Column(db.String(50), nullable=True)

    email = db.Column(db.String(120), nullable=True)

    # Store as text to preserve even invalid numeric input
    glucose = db.Column(db.String(50), nullable=True)

    haemoglobin = db.Column(db.String(50), nullable=True)

    cholesterol = db.Column(db.String(50), nullable=True)

    rejection_reason = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<RejectedPatient {self.full_name}>"
