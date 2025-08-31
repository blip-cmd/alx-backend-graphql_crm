#!/bin/bash

# Customer cleanup script - deletes customers with no orders since a year ago
# This script should be run via crontab

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to the Django project directory
cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Execute Django command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer, Order
from django.utils import timezone
from datetime import timedelta
import sys

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the last year
inactive_customers = Customer.objects.exclude(
    order__order_date__gte=one_year_ago
).distinct()

# Count before deletion
count = inactive_customers.count()

# Delete inactive customers
inactive_customers.delete()

# Print count for capture
print(count)
" 2>/dev/null)

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt

# Exit successfully
exit 0
