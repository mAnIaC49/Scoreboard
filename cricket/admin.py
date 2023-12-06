from django.contrib import admin

from .models import User, Players, Team, Game, Bowls, Playing, TeamsPlaying

# Register your models here.

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Players)
admin.site.register(Game)
admin.site.register(Bowls)
admin.site.register(Playing)
admin.site.register(TeamsPlaying)