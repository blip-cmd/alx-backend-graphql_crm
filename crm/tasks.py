from datetime import datetime
import requests
from celery import shared_task
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

@shared_task
def generate_crm_report():
    url = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=url, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    query = gql('''
        query {
            allCustomers {
                totalCount
            }
            allOrders {
                totalCount
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
    ''')
    result = client.execute(query)
    customers = result.get('allCustomers', {}).get('totalCount', 0)
    orders = result.get('allOrders', {}).get('totalCount', 0)
    revenue = 0
    for edge in result.get('allOrders', {}).get('edges', []):
        node = edge.get('node', {})
        revenue += float(node.get('totalAmount', 0))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"
    try:
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(log_line)
    except Exception:
        # Fallback for Windows
        import os
        from django.conf import settings
        fallback = os.path.join(settings.BASE_DIR, 'crm_report_log.txt')
        with open(fallback, 'a') as f:
            f.write(log_line)
    return log_line
