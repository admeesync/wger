# Running the Project

This guide outlines the steps required to run the Backend and Frontend of this project.

---

## 1. Backend (BE) Setup

Navigate to the backend directory:
```bash
cd BE
```

### Create and Activate Virtual Environment (Optional but Recommended)
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Initialize and Seed Database
Run the seed script once to create the database tables, upload directory, and the initial `superadmin` user:
```bash
python seed.py
```

### Run Backend Server
Start the development server with Uvicorn on port 8001:
```bash
uvicorn main:app --reload --port 8001
```

---

## 2. Frontend (FE) Setup

Navigate to the frontend directory:
```bash
cd FE
```

### Run Frontend Server
Start a local static server to serve the frontend files:
```bash
npx live-server
```
*(Alternatively, you can use any other static server or open `index.html` directly in your browser.)*

