# SiAPPMEN - Sistem Aplikasi Pengambilan dan Pendistribusian Instrumen Medis

SiAPPMEN is a web-based application designed to modernize and streamline the management of sterile medical instruments in a hospital setting. It replaces manual, paper-based tracking with a digital system that uses QR codes to monitor the entire lifecycle of instruments, from the Central Sterile Supply Department (CSSD) to various user units and back.

This system improves efficiency, accuracy, and accountability, ensuring that sterile instruments are tracked effectively, which directly contributes to patient safety.

## Features
- **User Authentication:** Secure registration and login for CSSD and hospital unit staff.
- **QR Code Tracking:** Unique QR codes are generated for each loan and distribution transaction, enabling real-time tracking and reducing the risk of lost instruments.
- **Instrument Lifecycle Management:** Complete digital workflows for:
    - Loaning instruments to user units.
    - Returning used instruments to the CSSD.
    - Distributing sterile instruments from the CSSD.
    - A formal handover process to confirm receipt of distributed items.
- **Reporting Dashboard:** A centralized dashboard provides key metrics on instrument status, daily movements, and outstanding items per unit, enhancing accountability and operational oversight.
- **Automated Notifications:** An automated system notifies users of overdue instruments to ensure timely returns and prevents them from borrowing new items until overdue ones are returned.

## Prerequisites
Before you begin, ensure you have the following installed on your system:
- Python (version 3.8 or higher)
- `pip` (Python package installer)

## Installation and Deployment Guide

Follow these steps to set up and run the SiAPPMEN application on a new device.

### 1. Set Up a Virtual Environment
It is highly recommended to run the application in a virtual environment to manage dependencies and avoid conflicts with other projects.

Open your terminal or command prompt and navigate to the project's root directory.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS and Linux:
source venv/bin/activate
```

### 2. Install Dependencies
With your virtual environment activated, install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
The application uses a SQLite database, which is a lightweight, file-based database. To create the database and populate it with initial data (such as a list of hospital units and available instruments), run the following command:

```bash
python create_db.py
```
This script will create a `site.db` file in the project's root directory and print a confirmation message once the database has been seeded.

### 4. Run the Application
Once the dependencies are installed and the database is initialized, you can start the Flask development server.

```bash
python run.py
```

The application will now be running. Open your web browser and navigate to the following address:

**http://127.0.0.1:5000**

### 5. Using the Application
- **Register a New User:** Go to the "Register" page to create a new user account.
- **Log In:** Use your newly created credentials to log in.
- **Explore:** Once logged in, you can explore the application's features, such as creating new loans, returning instruments, and viewing the dashboard.

To stop the application, return to your terminal and press `Ctrl+C`.