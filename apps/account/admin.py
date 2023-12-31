from django.contrib import admin
from apps.account.models import Account, VerifyPhoneNumber, Country, SportClub, SMSToken, City


class CityInline(admin.TabularInline):
    model = City
    extra = 1


class CountryAdmin(admin.ModelAdmin):
    inlines = (CityInline,)
    list_display = ('name', 'flag')


class AccountAdmin(admin.ModelAdmin):
    list_display = ('get_fullname', 'phone_number', 'gender', 'is_verified', 'date_login')
    list_filter = ('gender', 'date_created')
    date_hierarchy = 'date_created'
    readonly_fields = ('date_login', 'date_created')


admin.site.register(Account, AccountAdmin)
admin.site.register(VerifyPhoneNumber)
admin.site.register(SportClub)
admin.site.register(SMSToken)
admin.site.register(Country, CountryAdmin)
