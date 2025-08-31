# CRM Celery Report Setup

## Requirements
- Redis server running on `localhost:6379`
- All Python dependencies in `requirements.txt`

## Setup Steps

1. **Install Redis**
   - Download and install Redis from https://redis.io/download or use a package manager.

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Django migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start Celery worker**
   ```bash
   celery -A crm worker -l info
   ```

5. **Start Celery Beat**
   ```bash
   celery -A crm beat -l info
   ```

6. **Verify logs**
   - Check `/tmp/crm_report_log.txt` (or `crm_report_log.txt` in your project folder on Windows) for weekly reports.

## Notes
- The report runs every Monday at 6:00 AM by default.
- You can change the schedule in `crm/settings.py` under `CELERY_BEAT_SCHEDULE`.
