from django.contrib import admin

from .models import SampleBook, SampleQuote


class SampleBookAdmin(admin.ModelAdmin):
    fields = ["title", "excerpt", "author"]


admin.site.register(SampleBook, SampleBookAdmin)


class SampleQuoteAdmin(admin.ModelAdmin):
    fields = ["book", "quote"]


admin.site.register(SampleQuote, SampleQuoteAdmin)
