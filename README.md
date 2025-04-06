# Foodline: Smart Food Donation Platform

**Foodline** is a web application that connects food donors with recipients (like orphanages or NGOs) through a simple, location-based interface. It facilitates food gathering, claiming, and real-time coordination, making the donation process faster, smarter, and more transparent.

---

## Tech Stack

- **Frontend:** React + Vite + Tailwind CSS  
- **Backend:** FastAPI  
- **Database:** SQLite (via SQLAlchemy ORM)  
- **Authentication:** JWT-based using OAuth2PasswordBearer  
- **Hosting (optional):** [Add hosting platform if used]

---

## Features

### Donor
- Register and log in
- Add food gathering details (location, availability time, food type)
- View personal gathering history

### Recipient (e.g., orphanages)
- Register and log in
- View available food donations near their location
- Claim a food gathering
- Manage claim statuses (collected, cancelled)

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/foodline.git
cd foodline
```

---

### 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Start the Backend Server

```bash
uvicorn main:app --reload
```

By default, it runs on:  
`http://localhost:8000`

---

### 3. Frontend Setup (React + Vite)

```bash
cd ../frontend
npm install
```

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

#### Start the Frontend

```bash
npm run dev
```

Frontend runs on:  
`http://localhost:5173`

---

## API Endpoints

You can test all API endpoints using FastAPI docs:

`http://localhost:8000/docs`

---

## Folder Structure

```
foodline/
├── backend/
│   ├── main.py
│   ├── crud.py
│   ├── models.py
│   ├── schemas.py
│   └── database.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── api.js
│   └── .env
└── README.md
```

---

## Authentication

- JWT tokens are issued during login
- Token must be sent in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <your_token_here>
```

---

## Future Enhancements

- Add email verification and password reset functionality
- Admin dashboard for monitoring users, claims, and analytics
- Notification system for real-time updates
- **Machine Learning integration** to:
  - Predict food demand trends based on historical claims
  - Recommend optimal pickup timings to minimize wastage
  - Analyze donation patterns for smarter resource distribution

---

## Contributors

- **Sanjana S.**
- **Sejavarthana Anbalagan**
- **Pradeepaa M.**
- **Vaishnavi J.** 

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
