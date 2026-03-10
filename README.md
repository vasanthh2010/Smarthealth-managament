# Smart Hospital Token & Bed Management System

A full-stack real-time healthcare platform with token queuing, bed management, and emergency routing.

## Tech Stack
- **Frontend**: HTML5 + CSS3 + JavaScript (vanilla, mobile-first)
- **Backend**: Python Flask + Flask-SocketIO
- **Database**: MySQL
- **Maps**: Leaflet.js (OpenStreetMap)

## Quick Start

### Step 1: Setup MySQL Database
```bash
# Open MySQL (adjust password flag if needed)
mysql -u root -p < backend/schema.sql
```
This creates the `smart_hospital` database with sample data (City General Hospital + demo users).

### Step 2: Configure Environment (optional)
Edit `backend/.env` if your MySQL password differs:
```
DB_PASSWORD=your_password_here
```

### Step 3: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run the Server
```bash
cd backend
python app.py
```
Or double-click **`start.bat`** from the project root.

### Step 5: Open in Browser
Go to: **http://localhost:5000**

---

## Demo Credentials

| Role | Login | Password |
|------|-------|----------|
| Super Admin | `superadmin` | `Admin@123` |
| Hospital Admin (demo) | `HOSP001` | `Admin@123` |
| Patient | Register via signup page | - |

---

## Project Structure
```
antiproject/
├── backend/
│   ├── app.py              # Main Flask app
│   ├── config.py           # Configuration
│   ├── db.py               # Database helper
│   ├── middleware.py        # JWT auth decorators
│   ├── schema.sql           # MySQL schema + seed data
│   ├── requirements.txt
│   ├── .env                # DB credentials
│   └── routes/
│       ├── auth.py         # Login/signup for all 3 roles
│       ├── hospitals.py    # Hospital listing & management
│       ├── tokens.py       # Token booking & tracking
│       ├── beds.py         # Bed management
│       ├── ambulance.py    # Emergency / ambulance
│       ├── doctors.py      # Doctor management
│       └── admin.py        # Super admin operations
└── frontend/
    ├── index.html          # Landing/role selection
    ├── css/style.css       # Complete design system
    ├── js/api.js           # API client + auth utils
    ├── patient/            # 7 patient pages
    ├── hospital-admin/     # 4 hospital admin pages
    └── super-admin/        # 4 super admin pages
```

## Key Flows

### Patient
1. Sign up (full profile: name, DOB, blood group, address, etc.)
2. Login → Browse hospitals → Pick a hospital
3. View doctors + real-time queue/bed status
4. Book token → See success animation → Track live
5. Emergency button → Book ambulance / Call 108

### Hospital Admin
1. Login with Login ID assigned by Super Admin
2. View only their hospital's data (beds, queue, doctors)
3. Toggle bed status (real-time update via WebSocket)
4. Call patients into service, mark as completed
5. Manage doctors + toggle availability

### Super Admin
1. Login with system credentials
2. View all system stats (hospitals, patients, beds, tokens)
3. See hospital registration requests → Approve → System generates Login ID + Password
4. Delete hospitals or patients if misuse detected
