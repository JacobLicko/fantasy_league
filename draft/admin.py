from django.contrib import admin
from .models import League

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'creator', 'member_count')
    filter_horizontal = ('members',)

    def member_count(self,obj):
        return obj.members.count()
    
    member_count.short_description = 'Member Count'

# Register your models here.
admin.site.register(League, LeagueAdmin)