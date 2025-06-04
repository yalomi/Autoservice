from django.contrib import admin
from .models import User, MasterProfile, ClientProfile, Service, CarType, Specialization, Appointment, Article, CompanyInfo, FAQ, Contact, Vacancy, Review, PromoCode, ServiceCategory

admin.site.register(User)
admin.site.register(MasterProfile)
admin.site.register(ClientProfile)
admin.site.register(Service)
admin.site.register(CarType)
admin.site.register(Specialization)
admin.site.register(Appointment)
admin.site.register(Article)
admin.site.register(CompanyInfo)
admin.site.register(FAQ)
admin.site.register(Contact)
admin.site.register(Vacancy)
admin.site.register(Review)
admin.site.register(PromoCode)
admin.site.register(ServiceCategory)
