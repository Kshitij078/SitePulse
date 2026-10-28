# SitePulse — Website Health Monitor

SitePulse is a Python-based website monitoring platform that checks website availability, tracks response times, calculates uptime statistics, and records incidents when a website goes down or recovers.

## Features

- **Website Monitoring:** Add and monitor custom website URLs.
- **Availability Checks:** Check whether websites are up or down.
- **Response Time Tracking:** Measure website response times in milliseconds.
- **Uptime Analytics:** Calculate uptime percentages from recorded checks.
- **Incident Detection:** Record website downtime incidents.
- **Incident Resolution:** Track when a website recovers.
- **Interactive Dashboard:** Visualize website status, response times, reliability, and incident history.
- **Persistent Storage:** Store monitoring results in a database.
- **Dynamic Website Management:** Add, pause, and resume websites through the dashboard.

## Tech Stack

- **Language:** Python
- **Dashboard:** Streamlit
- **Database ORM:** SQLAlchemy
- **Database:** SQLite
- **HTTP Requests:** Requests
- **Data Analysis:** Pandas
- **Visualizations:** Plotly

## Project Structure

```text
SitePulse/
├── app/
│   ├── main.py
│   ├── dashboard.py
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   └── services/
│       ├── checker.py
│       └── monitor.py
├── tests/
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Kshitij078/SitePulse.git
cd SitePulse
```


### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, you can run the environment's Python executable directly instead.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Initialize the database

```powershell
python -c "from app.database.connection import Base, engine; from app.database.models import WebsiteCheck, Incident, MonitoredWebsite; Base.metadata.create_all(bind=engine); print('Database initialized')"
```

### 5. Start the monitoring service

Open a terminal in the project root and run:

```powershell
python -u -m app.services.monitor
```

The monitor checks active websites every 60 seconds.

### 6. Launch the dashboard

Open a second terminal in the project root, activate the virtual environment, and run:

```powershell
python -m streamlit run app/dashboard.py
```

Streamlit will provide a local URL for opening the dashboard in your browser.

## How to Use

1. Start the monitoring service.
2. Open the Streamlit dashboard.
3. Add a website URL, such as `https://example.com`.
4. View its latest status and response time.
5. Review uptime statistics and response-time charts.
6. Check incident history when a monitored website goes down or recovers.
7. Pause or resume websites as needed.

## How Uptime Is Calculated

Uptime percentage is calculated from the recorded checks:

```text
Uptime (%) = (Successful Checks / Total Checks) × 100
```

The percentage reflects the checks available in the database and is not a direct measurement of every second of availability.

## Future Improvements

- Email and Telegram notifications
- SSL certificate expiration monitoring
- Automated testing with pytest
- API endpoints with FastAPI
- Improved uptime reporting and filtering
- Deployment to a cloud platform

## Learning Outcomes

This project demonstrates practical experience with Python application development, HTTP requests, database operations, scheduled monitoring, incident management, data analysis, and interactive dashboard development.

## Author

**Kshitij Kukreti**

GitHub: https://github.com/Kshitij078

---

*SitePulse is an educational project. Monitoring frequency and results depend on network conditions, timeouts, and the websites being checked.*
