from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, CompanyInfo, FAQ, Contact, Vacancy, Review, PromoCode, ServiceCategory, Service, Appointment
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm, AppointmentForm
from django.contrib import messages
from .reviews import review_create, review_update, review_delete
from .statistics import get_clients_stats, get_services_sum_stats, get_age_stats, get_services_distribution_by_date
from django.contrib.admin.views.decorators import staff_member_required
from .external_api import get_weather, get_currency_rates
from django import forms
import requests

SUPPORTED_CURRENCIES = [('USD','USD'),('EUR','EUR'),('RUB','RUB'),('PLN','PLN')]

def home(request):
    last_article = Article.objects.order_by('-published_at').first()
    return render(request, 'core/home.html', {'last_article': last_article})

def about(request):
    info = CompanyInfo.objects.first()
    return render(request, 'core/about.html', {'info': info})

def news(request):
    articles = Article.objects.order_by('-published_at')
    return render(request, 'core/news.html', {'articles': articles})

def glossary(request):
    faqs = FAQ.objects.order_by('-added_at')
    return render(request, 'core/glossary.html', {'faqs': faqs})

def contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'core/contacts.html', {'contacts': contacts})

def privacy(request):
    return render(request, 'core/privacy.html')

def vacancies(request):
    vacancies = Vacancy.objects.order_by('-posted_at')
    return render(request, 'core/vacancies.html', {'vacancies': vacancies})

def reviews(request):
    reviews = Review.objects.order_by('-date')
    return render(request, 'core/reviews.html', {'reviews': reviews})

def promocodes(request):
    active = PromoCode.objects.filter(is_active=True)
    archive = PromoCode.objects.filter(is_active=False)
    return render(request, 'core/promocodes.html', {'active': active, 'archive': archive})

def services(request):
    categories = ServiceCategory.objects.all()
    services = Service.objects.all()
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if category_id:
        services = services.filter(category_id=category_id)
    if min_price:
        services = services.filter(price__gte=min_price)
    if max_price:
        services = services.filter(price__lte=max_price)
    return render(request, 'core/services.html', {
        'categories': categories,
        'services': services,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
    })

@login_required
def appointment_create(request):
    if not hasattr(request.user, 'client_profile'):
        return redirect('login')
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user.client_profile
            appointment.save()
            form.save_m2m()
            return redirect('my_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'core/appointment_form.html', {'form': form})

@login_required
def appointment_list(request):
    if not hasattr(request.user, 'client_profile'):
        return redirect('login')
    appointments = request.user.client_profile.appointments.select_related('master').prefetch_related('services')
    return render(request, 'core/appointment_list.html', {'appointments': appointments})

@login_required
def master_schedule(request):
    if not hasattr(request.user, 'master_profile'):
        return redirect('login')
    appointments = request.user.master_profile.appointments.select_related('client').prefetch_related('services')
    return render(request, 'core/master_schedule.html', {'appointments': appointments})

@login_required
def appointment_confirm(request, pk):
    if not hasattr(request.user, 'master_profile'):
        return redirect('login')
    app = get_object_or_404(Appointment, pk=pk, master=request.user.master_profile)
    app.status = 'confirmed'
    app.save()
    return redirect('master_schedule')

@login_required
def appointment_reject(request, pk):
    if not hasattr(request.user, 'master_profile'):
        return redirect('login')
    app = get_object_or_404(Appointment, pk=pk, master=request.user.master_profile)
    app.status = 'cancelled'
    app.save()
    return redirect('master_schedule')

@login_required
def appointment_delete(request, pk):
    if not hasattr(request.user, 'client_profile'):
        return redirect('login')
    app = get_object_or_404(Appointment, pk=pk, client=request.user.client_profile)
    if request.method == 'POST':
        app.delete()
        return redirect('my_appointments')
    return render(request, 'core/appointment_confirm_delete.html', {'appointment': app})

@login_required
def appointment_complete(request, pk):
    if not hasattr(request.user, 'master_profile'):
        return redirect('login')
    app = get_object_or_404(Appointment, pk=pk, master=request.user.master_profile)
    app.status = 'completed'
    app.save()
    return redirect('master_schedule')

@staff_member_required
def statistics_view(request):
    clients = get_clients_stats()
    sum_stats = get_services_sum_stats()
    age_stats = get_age_stats()
    dist = get_services_distribution_by_date()
    chart_labels = [str(x['day']) for x in dist]
    chart_data = [x['total'] for x in dist]
    return render(request, 'core/statistics.html', {
        'clients': clients,
        'sum_stats': sum_stats,
        'age_stats': age_stats,
        'dist': dist,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })

class CurrencyConvertForm(forms.Form):
    amount = forms.FloatField(label='Сумма', min_value=0.01)
    from_currency = forms.ChoiceField(choices=SUPPORTED_CURRENCIES)
    to_currency = forms.ChoiceField(choices=SUPPORTED_CURRENCIES)

@login_required
def user_dashboard(request):
    city = getattr(request.user, 'location', 'Минск')
    if city.strip().lower() == 'минск':
        city = 'Minsk'
    weather = get_weather(city)
    rates = get_currency_rates()
    convert_result = None
    form = CurrencyConvertForm(request.GET or None)
    if form.is_valid():
        amount = form.cleaned_data['amount']
        from_cur = form.cleaned_data['from_currency']
        to_cur = form.cleaned_data['to_currency']
        url = f'https://api.frankfurter.app/latest?amount={amount}&from={from_cur}&to={to_cur}'
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if 'rates' in data:
                convert_result = f"{amount} {from_cur} = {data['rates'][to_cur]} {to_cur}"
            else:
                convert_result = 'Ошибка конвертации'
        except Exception as e:
            convert_result = str(e)
    return render(request, 'core/dashboard.html', {
        'weather': weather,
        'rates': rates,
        'city': city,
        'form': form,
        'convert_result': convert_result,
    })
