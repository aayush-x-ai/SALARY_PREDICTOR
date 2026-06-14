# SalaryScope - Salary Predictor System

SalaryScope is a simple full-stack mini project built with Flask, HTML/CSS,
JavaScript and MySQL. A user can create an account, enter career information,
receive an annual salary estimate and review their own prediction history.

## Main features

- User signup, login, logout and password hashing
- Salary form for education, skills, experience, city, domain and role
- Random Forest regression using the local salary dataset
- Estimated annual salary and likely salary range
- Private prediction history for each logged-in user
- Responsive dark technology-themed interface
- MySQL storage for users and predictions

## Project flow

1. The landing page introduces the system.
2. The user signs up or logs in.
3. The user enters their career profile.
4. The Random Forest model analyzes salary patterns learned from
   `model/dataset.csv`.
5. The result is saved in MySQL and shown in the user's history.

## Setup

### 1. Create a virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Create the MySQL database

Open MySQL Workbench and run `database.sql`, or use:

```powershell
mysql -u root -p < database.sql
```

The default settings use MySQL user `root`, password `root` and database
`salary_predictor`. If your settings differ, set environment variables:

```powershell
$env:SECRET_KEY="a-long-random-value"
$env:DB_USER="root"
$env:DB_PASSWORD="your-mysql-password"
$env:DB_NAME="salary_predictor"
```

### 3. Run the project

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

## Prediction algorithm

The model uses Random Forest regression. Categorical fields such as city,
domain, role and education are converted using one-hot encoding. Experience
and skill count remain numeric. The model trains 250 decision trees and averages
their outputs to produce the final salary estimate. The variation among tree
predictions is used to calculate the displayed salary range.

The included data is intended for an academic demonstration. A production
system would use a larger, regularly updated and verified salary dataset.

The current dataset contains 1,512 unique synthetic salary profiles covering
all supported cities, roles, education levels and multiple experience levels.
It can be regenerated deterministically with:

```powershell
python model\generate_dataset.py
```

## Database tables

- `users`: account name, email, hashed password and creation date
- `predictions`: profile inputs, predicted salary, date and related user
