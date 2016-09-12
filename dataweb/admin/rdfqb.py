from dataweb.models import *
from django.contrib import admin
    
class QBDimensionInline(admin.TabularInline):
    model = QBDimension
    # readonly_fields = ('slug','created')
    #fields = ('code','namespace')
    # related_search_fields = {'label' : ('name','slug')}
    extra=1 

class QBDimensionAdmin(admin.ModelAdmin):
    #inlines = [ QBDimensionInline ]
    pass

class QBMeasureAdmin(admin.ModelAdmin):
    #inlines = [ QBDimensionInline ]
    pass
    
class QBRealNumberMeasureAdmin(admin.ModelAdmin):
    #inlines = [ QBDimensionInline ]
    pass
    
class QBCodedMeasureAdmin(admin.ModelAdmin):
    #inlines = [ QBDimensionInline ]
    pass
    
class QBCodedDimensionAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass

class QBSpatialDimensionAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass
    
admin.site.register(QBDimension, QBDimensionAdmin)
admin.site.register(QBCodedDimension, QBCodedDimensionAdmin)
admin.site.register(QBSpatialDimension, QBSpatialDimensionAdmin)
admin.site.register(QBMeasure, QBMeasureAdmin)
admin.site.register(QBRealNumberMeasure, QBRealNumberMeasureAdmin)
admin.site.register(QBCodedMeasure, QBCodedMeasureAdmin)
