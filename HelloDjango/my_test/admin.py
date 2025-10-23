from django.contrib import admin
from my_test.models import Test, Contact, Tag

class TagInline(admin.TabularInline):
    model = Tag

class ContactAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    list_display = ["name", "email"]
    search_fields = ["name"]
    # fieldsets = (
    #     ['Advance',{
    #         'classes': ('collapse',), # CSS
    #         'fields': ('name', 'email',),
    #     }],
    # )

# Register your models here.
admin.site.register([Test, Tag])
admin.site.register(Contact, ContactAdmin)