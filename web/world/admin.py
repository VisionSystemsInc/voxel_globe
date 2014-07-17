from django.contrib import admin
from world.models import  TestTable, Favorites, WorldBorder


class FavoritesInline(admin.TabularInline):
  model = Favorites;
  extra = 2

class TestTableAdmin(admin.ModelAdmin):
  inlines=[FavoritesInline]

class FavoritesAdmin(admin.ModelAdmin):
  fieldsets= [ (None, {'fields': ['name']}),
               ('Favs', {'fields': ['favoriteBook']})]
  list_display = ('name', 'favoriteBook')

class WorldBorderAdmin(admin.ModelAdmin):
  list_display = ('name', 'lat', 'lon', 'closeToUS');

# Register your models here.
admin.site.register(TestTable, TestTableAdmin)
admin.site.register(Favorites, FavoritesAdmin)

admin.site.register(WorldBorder, WorldBorderAdmin)
