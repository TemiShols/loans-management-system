# loans-management-system
git clone https://github.com/TemiShols/loans-management-system.git

cd loans-management-system

create your environment.I used conda,you can use your preferred environment

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver


The following are the endpoints for Authentication:

| Method | URL              | Description          | Auth Required |
| ------ | ---------------- | -------------------- | ------------- |
| POST   | `/api/register/` | Register a new user  | ❌             |
| POST   | `/api/login/`    | Log in and get token | ❌             |



The following are Loan Application Endpoints:


| Method | URL                       | Description                                 | Auth Required | Access Level |
| ------ | ------------------------- | ------------------------------------------- | ------------- | ------------ |
| POST   | `/api/loans/apply/`       | Submit a loan application                   | ✅             | User         |
| GET    | `/api/loans/my/`          | Get current user's loan applications        | ✅             | User         |
| POST   | `/api/loans/<id>/status/` | Admin: Update loan status (`approve`, etc.) | ✅             | Admin only   |
| GET    | `/api/loans/flagged/`     | List all flagged loans                      | ✅             | Admin only   |


N.B: Fraud is detected when calling the POST /api/loans/apply/ and the loan is flagged if the folloowing are discovered:

1. User submits more than 3 loans in 24 hours

2. Loan amount > NGN 5,000,000

3. Email domain is used by more than 10 users

If flagged, loan is created with:

"status": "flagged"
