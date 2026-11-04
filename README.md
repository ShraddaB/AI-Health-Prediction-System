
# AI Health Prediction System

A Python Flask-based web application for managing patient records and generating AI-powered health insights from blood test values using the Google Gemini API.

## Project Overview

The AI Health Prediction System helps users register patients, store their blood test information, manage patient records, and generate AI-based health remarks.

The application uses Flask for the backend, SQLite for data storage, Bootstrap for the user interface, and Google Gemini API for AI-generated health information.

## Features

- Patient registration and management
- View all registered patient records
- Edit and delete patient details
- Email validation
- Date of birth validation
- Blood test value validation
- Separate storage for rejected patient entries
- AI-generated health remarks using Google Gemini API
- SQLite database for persistent storage
- Responsive Bootstrap interface

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- Bootstrap 5
- Google Gemini API

## Patient Information

The application collects:

- Full Name
- Date of Birth
- Email Address
- Glucose
- Haemoglobin
- Cholesterol
- AI-generated Health Remarks

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ShraddaB/AI-Health-Prediction-System.git
```

### 2. Open the project folder

```bash
cd AI-Health-Prediction-System
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the Gemini API key

Create a `.env` file in the main project folder.

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
FLASK_SECRET_KEY=your_secret_key
```

Replace the placeholder values with your own keys.

Never upload your `.env` file to GitHub.

### 7. Run the application

```bash
python app.py
```

Open the application in your browser:

http://127.0.0.1:5000/

## AI Integration

The application uses the Google Gemini API to generate health-related remarks based on the patient's glucose, haemoglobin, and cholesterol values.

The generated remarks provide general health information and are not a medical diagnosis.

## Database

SQLite is used to store patient records and rejected patient submissions.

The database is automatically created when the application starts.

## Important Disclaimer

This application is developed for educational and demonstration purposes. AI-generated remarks are not a substitute for professional medical advice, diagnosis, or treatment.

## Author

**Shradda B Suvarna**

Master of Computer Applications (MCA)
