from django.contrib import admin

from .models import Insured


class BirthYearFilter(admin.SimpleListFilter):
    title = "birth year"
    parameter_name = "birth_year"

    def lookups(self, request, model_admin):
        years = Insured.objects.dates("birth_date", "year")
        return [(year.year, year.year) for year in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(birth_date__year=self.value())
        return queryset


@admin.register(Insured)
class InsuredAdmin(admin.ModelAdmin):
    list_display = ("code", "full_name", "cnib", "birth_date")
    search_fields = ("first_name", "last_name", "cnib")
    list_filter = (BirthYearFilter,)
