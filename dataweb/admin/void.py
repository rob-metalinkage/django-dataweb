from dataweb.models import *
from django.contrib import admin
    
class VoidTechnicalFeatureInline(admin.TabularInline):
    model = VoidTechnicalFeature
    # readonly_fields = ('slug','created')
    #fields = ('code','namespace')
    # related_search_fields = {'label' : ('name','slug')}
    extra=1 

class VoidDatasetAdmin(admin.ModelAdmin):
    search_fields = ['label','feature','comment']
    inlines = [ VoidTechnicalFeatureInline ]
    
class VoidTechnicalFeatureAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass
    
admin.site.register(VoidDataset, VoidDatasetAdmin)
admin.site.register(VoidTechnicalFeature, VoidTechnicalFeatureAdmin)