from django.db.models import F
from core.models import ClientProfile, Appointment, User
from statistics import mean, median, mode
from datetime import date

def get_clients_stats():
    clients = ClientProfile.objects.select_related('user').all().order_by('user__last_name', 'user__first_name')
    data = []
    for client in clients:
        appointments = Appointment.objects.filter(client=client, status='completed').prefetch_related('services')
        total = sum(service.price for app in appointments for service in app.services.all())
        data.append({
            'name': f"{client.user.last_name} {client.user.first_name}",
            'email': client.user.email,
            'total': total
        })
    return data

def get_services_sum_stats():
    sums = []
    for client in ClientProfile.objects.all():
        appointments = Appointment.objects.filter(client=client, status='completed').prefetch_related('services')
        total = sum(service.price for app in appointments for service in app.services.all())
        sums.append(total)
    if not sums:
        return {'mean': 0, 'median': 0, 'mode': 0}
    try:
        m = mode(sums)
    except:
        m = None
    return {
        'mean': round(mean(sums), 2),
        'median': round(median(sums), 2),
        'mode': m
    }

def get_age_stats():
    ages = []
    today = date.today()
    for client in ClientProfile.objects.select_related('user').all():
        birth = client.user.birth_date
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        ages.append(age)
    if not ages:
        return {'mean': 0, 'median': 0}
    return {
        'mean': round(mean(ages), 2),
        'median': round(median(ages), 2)
    }

def get_services_distribution_by_date():
    # Считаем вручную сумму по датам
    from collections import defaultdict
    result = defaultdict(float)
    appointments = Appointment.objects.filter(status='completed').prefetch_related('services')
    for app in appointments:
        day = app.date
        for service in app.services.all():
            result[day] += float(service.price)
    return [ {'day': str(day), 'total': total} for day, total in sorted(result.items()) ] 