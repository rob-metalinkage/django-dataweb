from django import forms
from dataweb.models import *
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.urlresolvers import reverse


from django.core.exceptions import MultipleObjectsReturned
from django.utils.safestring import mark_safe

def add_link_field(target_model=None, field='', app='', field_name='link',
                   link_text=unicode, short_description=None):
    """
    decorator that automatically links to a model instance in the admin;
    inspired by http://stackoverflow.com/questions/9919780/how-do-i-add-a-link-from-the-django-admin-page-of-one-object-
    to-the-admin-page-o
    :param target_model: modelname.lower or model
    :param field: fieldname
    :param app: appname
    :param field_name: resulting field name
    :param link_text: callback to link text function
    :param short_description: list header
    :return:
    """
    def add_link(cls):
        reverse_name = target_model or cls.model.__name__.lower()

        def link(self, instance):
            app_name = app or instance._meta.app_label
            reverse_path = "admin:%s_%s_change" % (app_name, reverse_name)
            link_obj = getattr(instance, field, None) or instance

            # manyrelatedmanager with one result?
            if link_obj.__class__.__name__ == "RelatedManager":
                try:
                    link_obj = link_obj.get()
                except MultipleObjectsReturned:
                    return u"multiple, can't link"
                except link_obj.model.DoesNotExist:
                    return u""

            url = reverse(reverse_path, args = (link_obj.id,))
            return mark_safe(u"<a href='%s'>%s</a>" % (url, link_text(link_obj)))
        link.allow_tags = True
        link.short_description = short_description or (reverse_name + ' link')
        setattr(cls, field_name, link)
        cls.readonly_fields = list(getattr(cls, 'readonly_fields', [])) + \
            [field_name]
        return cls
    return add_link
    
class MetaInline(admin.TabularInline):
    name = "Extra Metadata"
    help_text = 'Additional statement about this object. Place comments and labels here with language tags eg @fr. <some URI> denotes a resource value.'
    verbose_name = "Additional metadata property"
    model = ResourceMeta
    #filter_horizontal = ('metaprop',)
    # readonly_fields = ('slug','created')
    #fields = ('code','namespace')
    search_fields = {'metaprop' : ('definition','propname','namespace__prefix')}
    extra=1

class InheritanceInline(admin.TabularInline):
    """
        an incomplete attempt to show details of the inherited profiles, and a place to potentially to 
        traverse the inheritance hierarchy. may replace with a widget accessing SPARQL endpoint
    """
    verbose_name = 'Profiles inherited'
    model = Profile
    fields= ('label','uri')
    show_change_link = True  # django 1.8 only :-(
    list_display = ('link',)
    readonly_fields = ['label','uri','link']
    
    def link(self, object):
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.model_name),  args=[object.id] )
        return mark_safe(u'<a href="%s">Show %s</a>' %(url,  object.__unicode__()))

    
@add_link_field()
class CodedDimensionBindingInline(admin.TabularInline):
    verbose_name = 'Coded dimension binding'
    model = CodedDimensionBinding
    readonly_fields =('label',)
    #extra=0 
    
class SpatialDimensionBindingInline(admin.TabularInline):
    verbose_name = 'Spatial Dimension added or specialised by this profile'
    model = CoordDimensionBinding
    # readonly_fields = ('slug','created')
    #fields = ('code','namespace')
    # related_search_fields = {'label' : ('name','slug')}
    extra=0 

class CodedMeasureBindingInline(admin.TabularInline):
    verbose_name = 'Coded Measure added or specialised by this profile'
    model = CodedMeasureBinding
    # readonly_fields = ('slug','created')
    #fields = ('code','namespace')
    # related_search_fields = {'label' : ('name','slug')}
    extra=0
    
class SpatialMeasureBindingInline(admin.TabularInline):
    verbose_name = 'Spatial Measure added or specialised by this profile'
    model = SpatialMeasureBinding
    # readonly_fields = ('slug','created')
    #fields = ('code','namespace')
    # related_search_fields = {'label' : ('name','slug')}
    extra=0

class MeasureBindingInline(admin.TabularInline):
    verbose_name = 'Other measured properties'
    model = MeasureBinding
    # readonly_fields = ('slug','created')
    #fields = ('code','namespace')
    # related_search_fields = {'label' : ('name','slug')}
    extra=0

class ImplementsForm(forms.ModelForm):
    class Meta:
        model = Profile
        
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['implements'].queryset = Profile.objects.exclude(id__exact=self.instance.id)

        
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
      ('Details', {
          'fields': ('uri', 'label', 'comment', 'is_class',  'definedBy')
      }),
      ('Inherits from', {
          'fields': ('implements',)
      }),
      ('Dimension Bindings', {
          'description' : '''Bindings to "data dimensions", allowing constraints on parameters of that dimension to reflect allowable values for this profile. Dimensions are values that are discrete, fixed and can be used to identify piece of data (i.e. part of an index). They reflect data organised - for example by year, or a spatial grid cell. Use a "Measure" if the value is determined as part of the record, not part of the identification of a record <P><img src='dataweb/profiles_help.png'>''',
          'fields': ('dimensions_st','dimensions_coded','dimensions_other')
      }),
      ('Measure Bindings', {
          'description' : 'Bindings to "data measures" allowing constraints on parameters of measures to reflect allowable values for this profile. Values recorded. A profile only needs to specify those properties whose values are intended to be used consistently across multiple data sets.',
          'fields': ('measures_st','measures_coded','measures_other')
      }),
    )
    #inlines = [ MetaInline, SpatialDimensionBindingInline,CodedDimensionBindingInline, CodedMeasureBindingInline, MeasureBindingInline, SpatialMeasureBindingInline ]
    inlines = [ MetaInline ]
    form = ImplementsForm
    filter_horizontal = ('implements','dimensions_other','dimensions_st','dimensions_coded', 'measures_coded', 'measures_other', 'measures_st')
    #exclude = ('dimensions_coded','measures')
    
class CoordDimensionBindingAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass

class DimensionBindingAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass

class CodedDimensionBindingAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass
    

class MeasureBindingAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass

class CodedMeasureBindingAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass    

class SpatialMeasureBindingAdmin(admin.ModelAdmin):
    # inlines = [GenericMetaPropInline ]
    pass
    
admin.site.register(Profile, ProfileAdmin)
admin.site.register(DimensionBinding, DimensionBindingAdmin)
admin.site.register(CoordDimensionBinding, CoordDimensionBindingAdmin)
admin.site.register(CodedDimensionBinding, CodedDimensionBindingAdmin)
admin.site.register(MeasureBinding, MeasureBindingAdmin)
admin.site.register(CodedMeasureBinding, CodedMeasureBindingAdmin)
admin.site.register(SpatialMeasureBinding, SpatialMeasureBindingAdmin)
