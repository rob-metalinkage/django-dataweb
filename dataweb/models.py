# -*- coding:utf-8 -*-

# uses SKOS 
# with configurations for RDF mapping and export module django-rdf-io
# TODO - allow link to an existing model containing metadata (i.e. an original source we want to make further statements about, without duplication of metadata)

from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_lazy
from extended_choices import Choices
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
# update this to use customisable setting
# from django.contrib.auth.models import User
from django.conf import settings

#from taggit.models import TagBase, GenericTaggedItemBase
#from taggit.managers import TaggableManager
from rdf_io.models import Namespace, GenericMetaProp
from skosxl.models import Scheme, Concept

#from .base import URIResource, URIResourceManager

import json


DEFAULT_SCHEME_SLUG = 'general'
CRS_SCHEME = "http://www.opengis.net/def/crs"
UOM_SCHEME = "http://www.opengis.net/def/uom"

"""
Test Case:
unstats:mdgi a void:Dataset ;
    rdfs:label "Millenium Development Goal Indicators" ;
    void:exampleResource <http://mdgs.un.org/unsd/mdg/Handlers/ExportHandler.ashx?Type=Excel&Countries=360&Series=580> ;
    void:feature unstats:mdgDownload , unstats:mdgWeb ,  unstats:mdgSeries ;
    void:vocabulary un:UNSTATS-countries ;
    void:vocabulary mdgs: ;
   dcterms:subject sdmx-subject:3.3.5 ;
    # RDF datacube to describe URI
    qb:structure unstats:mdgqb ;
    .
unstats:mdgDownload a void:TechnicalFeature ;
	rdfs:label "Data download API";
	sirf:urlTemplate "http://mdgs.un.org/unsd/mdg/Handlers/ExportHandler.ashx?Type={type}&Countries={_item}&Series={dim:mdgindicator skos:notation^^unstats:seriescode}" ;
#	sirf:varbinding unstats:mdgformats ;
#	sirf:varbinding unstats:mdgindicators 
	.

unstats:mdgWeb a void:TechnicalFeature ;
	rdfs:label "MDG Country Summary";
	rdfs:comment "Millenium Development Goals Indicators from the UN" ;
	sirf:urlTemplate "http://mdgs.un.org/unsd/mdg/Data.aspx?cr={_item}" ;
	.

unstats:mdgSeries a void:TechnicalFeature ;
	rdfs:label "MDG Indicator Series";
	rdfs:comment "Millenium Development Goals Indicator Results" ;
	sirf:urlTemplate "http://unstats.un.org/unsd/mdg/SeriesDetail.aspx?srid={dim:mdgindicator}&crid={_item}" ;
	.

"""
   
class URIResourceManager(models.Manager):
    """
        Generic manager for any object identified by a URI iin a property called "uri"
    """
    def get_by_natural_key(self, uri):
        return self.get( uri = uri)
        
class URIResource(models.Model):

        
    objects = URIResourceManager()
    # URI doesnt need to be a registered Namespace unless you want to use prefix:term expansion for it
    uri         = models.CharField(blank=False,max_length=250,verbose_name=_(u'URI'),editable=True,help_text=_(u'You may use a short form (CURIE) such as eg:MyProfile if the namespace for eg: is registered'))   
    label  = models.CharField(_(u'label'),blank=False,max_length=255)
    comment  = models.TextField(_(u'description'),null=True,blank=True,max_length=2000, help_text=_(u'Describe the purpose of this resource (in English). Add other language descriptions using "Additional metadata properties" as rdfs:comment properties with the appropriate @xx language tag'))
    
    slug        = exfields.AutoSlugField(populate_from=('uri'))
   
    def __unicode__(self):
        return self.label
        
    def natural_key(self):
        return( self.uri )
        
      
class ResourceMeta(models.Model):
    """
        extensible metadata using rdf_io managed reusable generic metadata properties
    """
    resource      = models.ForeignKey(URIResource) 
    metaprop   =  models.ForeignKey(GenericMetaProp) 
    value = models.CharField(_(u'value'),max_length=500)
 

class QBDimension(URIResource):
    """
        A RDF-Datacube Dimension. If is_class is set True then this will be treated as a class and its declared sub_types will inherit the properties. 
        A Class will also be rendered using a rdfs and OWL class formalism unless a OWL class definition link is provided. If one is provided this will be loaded to the target triple store.
    """
    objects = URIResourceManager()
    is_class = models.BooleanField(help_text=_(u'Check if this is a abstract class of Dimensions'))  
    concept = models.CharField(blank=True,max_length=250,help_text=_(u'This specifies the nature of the phenomenon addressed by this dimension'))
    range = models.CharField(blank=True,max_length=250,help_text=_(u'The RDF type of allowable values. concepts in bound code lists need to declare this datatype if this is specified)'))
    helptext = models.TextField(max_length=5000, help_text=_(u'Usage instructions for this dimension'))
    sub_type_of = models.ForeignKey('self',null=True, blank=True,help_text=_(u'Specialises this as base definition.') )
    # core_type = models.ForeignKey('self', null=True, blank=True, limit_choices_to={'uri__startswith' : 'qb:' })
 
    owl = models.URLField(null=True, blank=True,help_text=_(u'Canonical OWL definition. With an RDF-IO mappings this may be propagated to the target RDF datastore, or generated automatically'))  
 
class QBCodedDimension(QBDimension):
    """
        A RDF-Datacube Coded Dimension. Binds the domain and range of a dimension to a SKOS resource with optional data typing.
    """
    objects = URIResourceManager()
    codelist = models.ForeignKey(Scheme, null=True, blank=True,help_text=_(u'SKOS Concept Scheme'))
    collection =  models.CharField(blank=True,max_length=500,help_text=_(u'URI of a SKOS Collection resource that defines an allowable sub-set of the bound code list'))
 
class QBSpatialDimension(QBDimension):
    """
        A RDF-Datacube Spatial coordinate Dimension. Provides properties to define CRS, precision etc
    """
    objects = URIResourceManager()
    crs = models.ForeignKey(Concept, null=True, blank=True,help_text=_(u'CRS - set only if naming a special dimension for a specific common CRS'),limit_choices_to={'scheme__uri' : CRS_SCHEME })
    axisName = models.CharField(blank=False,max_length=100,help_text=_(u'name of the coordinate axis or discrete cell type, e.g. latitude, easting, elevation, dggs, what3words  - should match the conventions for the CRS used.'))

class QBMeasure(URIResource):
    concept = models.CharField(blank=True,max_length=250,help_text=_(u'This specifies the subject domain (what is being measured'))
    datatype = models.CharField(blank=True,max_length=250,help_text=_(u'RDFS Data Type. This specifies the datatype of the measure'))
    range = models.CharField(blank=True,max_length=250,help_text=_(u'The RDF type of allowable values)'))
    helptext = models.TextField(max_length=5000, help_text=_(u'Usage instructions for this measure'))
    sub_type_of = models.ForeignKey('self',null=True, blank=True,help_text=_(u'Specialises this as base definition.'))

class QBCodedMeasure(QBMeasure):
    codelist = models.ForeignKey(Scheme, null=True, blank=True,help_text=_(u'SKOS Concept Scheme'))
    collection =  models.CharField(blank=True,max_length=500,help_text=_(u'URI of a SKOS Collection resource that defines an allowable sub-set of the bound code list'))
    
class QBRealNumberMeasure(QBMeasure):
   uom = models.ForeignKey(Concept, null=True, blank=True,help_text=_(u'CRS'),limit_choices_to={'scheme__uri' : UOM_SCHEME })
   
class QBSpatialMeasure(QBMeasure):
    """
        A RDF-Datacube Spatial coordinate measure. Provides properties to define CRS, precision etc
    """
    objects = URIResourceManager()
    crs = models.ForeignKey(Concept, null=True, blank=True,help_text=_(u'CRS - set only if naming a special dimension for a specific common CRS'),limit_choices_to={'scheme__uri' : CRS_SCHEME })

    
class DimComponent(URIResource):
    class Meta:
        abstract = True
        
    isConstant  = models.BooleanField(help_text="Check if this dimension is bound to a single valued range")  
    range = models.CharField(blank=True,max_length=250,help_text=_(u'range of Dimension - a data type or constant value using RDF syntax - <URI> or "literal"^^datatype eg "1"^^xsd:int '))

    element = models.CharField(blank=True,max_length=500,help_text=_(u'name of the target schema element this component is bound to. Use Xpath notation a/b/c if the element is nested. element names are relative to the schema of the data structure. in RDF, using RDF-QB the element is the name of the dimensionProperty, and the DimensionBinding is a qb:ComponentSpecification')) 

class DimensionBinding(DimComponent) :
    implements = models.ForeignKey(QBDimension, help_text=_(u'The abstract dimension property used')) 

class CodedDimensionBinding(DimComponent) :
    implements = models.ForeignKey(QBCodedDimension, help_text=_(u'The coded dimension property used')) 
    collection =  models.CharField(blank=True,max_length=500,help_text=_(u'URI of a SKOS Collection resource that defines an allowable sub-set of the bound code list'))

 
    
class CoordDimensionBinding(DimComponent):
    implements = models.ForeignKey(QBSpatialDimension, help_text=_(u'The spatial coordinate dimension property used')) 
    crs = models.ForeignKey(Concept, null=True, blank=True,help_text=_(u'CRS (if not set by the dimension used)'),limit_choices_to={'scheme__uri' : CRS_SCHEME })
    startRange = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=12,help_text=_(u'Smallest value of dimension'))
    endRange = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=12,help_text=_(u'Smallest value of dimension'))
    step = models.DecimalField(max_digits=12, decimal_places=12,help_text=_(u'Discrete step size in this dimension - (if this is not relevant a SpatialMeasure is probably required'))

class MeasureComponent(URIResource):
    class Meta:
        abstract = True
        
    element = models.CharField(blank=True,max_length=500,help_text=_(u'name of the target schema element this component is bound to. Use Xpath notation a/b/c if the element is nested. element names are relative to the schema of the data structure. in RDF, using RDF-QB the element is the name of the measureProperty, and the MeasureComponent is a qb:ComponentSpecification')) 
    range = models.CharField(blank=True,max_length=250,help_text=_(u'range of Dimension - a data type or constant value using RDF syntax - <URI> or "literal"^^datatype eg "1"^^xsd:int '))

    
class MeasureBinding(MeasureComponent):
    """ 
        undifferentiated measure - should restrict choices to not spatial or code
    """
    implements = models.ForeignKey(QBMeasure) 
    uom = models.ForeignKey(Concept, null=True, blank=True,help_text=_(u'CRS'),limit_choices_to={'scheme__uri' : UOM_SCHEME })
    precision = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=12,help_text=_(u'Precision'))

class SpatialMeasureBinding(MeasureComponent):
    implements = models.ForeignKey(QBSpatialMeasure) 
    crs = models.ForeignKey(Concept, null=True, blank=True,help_text=_(u'CRS'),limit_choices_to={'scheme__uri' : CRS_SCHEME })
    precision = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=12,help_text=_(u'Precision'))

class CodedMeasureBinding(MeasureComponent):
    implements = models.ForeignKey(QBCodedMeasure) 
    codelist = models.ForeignKey(Scheme, null=True, blank=True,help_text=_(u'SKOS Concept Scheme'))
    concept = models.CharField(blank=True,max_length=250,help_text=_(u'RDFS Data Type. This specifies the domain - i.e. type of Concept from the target Concept Scheme needed.'))
  
class ProfileNotRelatedManager(models.Manager):
    """ this doesnt work.. """
    def get_query_set(self):
        return super(ProfileNotRelatedManager, self).get_query_set().exclude(id=self.id)

class Profile(URIResource) :
    """
        Defines an interoperability profile by binding constraints to a base conformance Class. Note that Profiles may themselves be extended - so a null profile can be attached to
        any interoperability standard with no additional constraints defined.
    """
    # gets list of profiles not already related as parent, self or child
    # disjoint = ProfileNotRelatedManager()
    
    is_class = models.BooleanField(help_text=_(u'Check if this is a abstract class of features. These are not directly implementable, but may be used to characterise levels of interoperability between specific profiles'))  
    definedBy = models.CharField(blank=True,max_length=500,help_text=_(u'Link to normative specification document'))
    implements = models.ManyToManyField('self',symmetrical = False, verbose_name=_(u'Base Profiles'),null=True, blank=True,help_text=_(u'base Profiles specialised by this profile'))
    dimensions_st =  models.ManyToManyField(CoordDimensionBinding, null=True, blank=True, help_text=_(u'Spatio Temporal dimensions')) 
    dimensions_coded =  models.ManyToManyField(CodedDimensionBinding, null=True, blank=True, help_text=_(u'Coded dimensions'))                                   
    dimensions_other =  models.ManyToManyField(DimensionBinding,null=True, blank=True, help_text=_(u'Other dimensions'))
    measures_st =  models.ManyToManyField(SpatialMeasureBinding, null=True, blank=True, help_text=_(u'Spatio Temporal Measures')) 
    measures_coded =  models.ManyToManyField(CodedMeasureBinding, null=True, blank=True, help_text=_(u'Coded Measures'))                                   
    measures_other =  models.ManyToManyField(MeasureBinding,null=True, blank=True, help_text=_(u'Other measures'))


    
class VoidTechnicalFeature(URIResource):
    is_class = models.BooleanField(help_text="Check if this is a abstract class of features")  
    sub_type_of = models.ForeignKey('self',  null=True, blank=True,help_text=_(u'Specialises this as base definition.'))
    URL_template_help = _(u'URL template - variables are bound to QBDimensions. TODO - link to detailed doc')
    url_template  = models.CharField(blank=True,null=True, help_text=URL_template_help, max_length=2000,verbose_name=_(u'URI template for HTTP GET protocol'),editable=True)   
    #dct:hasFormat = manytomany to mime types in urlrewriter.
    
class VoidDataset(URIResource):
    """
        A model to define a class of VoiD Datasets, or a specific instance bound to a URI space. 
        Note that VoiD Datasets may be defined automatically by providing appropriate rules to be applied by a RDF environment linked using the django-rdf-io module.
        This module may be used to define additional properties of these Datasets by using the same URI identifier for the VoiD Dataset. Care should be taken to make sure that URI namespace governance does not allow the same URI to be reused for a different purpose.
    """
    is_class = models.BooleanField(help_text="Check if this is a abstract class of datasets")  
    sub_type_of = models.ForeignKey('self', null=True, blank=True,help_text=_(u'Specialises this as base definition.'))
    urispace = models.CharField(blank=True,null=True,max_length=250,help_text=_(u'URI namespace of the members of this Dataset)'))
    
    implements = models.ManyToManyField(Profile,verbose_name=_(u'Interoperability Profiles'),null=True, blank=True,help_text=_(u'Interoperability Profiles implemented by this dataset. Defines common elements of data structure and standard "technical features" such as APIs to support'))

    feature = models.ManyToManyField(VoidTechnicalFeature,null=True, blank=True,symmetrical=False, 
                                            verbose_name=(_(u'Additional Technical Features')))
    sparql = models.URLField(null=True, blank=True,help_text=_(u'Optional: SPARQL endpoint for this dataset'))
    search = models.URLField(null=True, blank=True,help_text=_(u'Optional: OpenSearch endpoint for this dataset'))                                          
    # vocabulary = models.ManyToManyField(Scheme,null=True,symmetrical=False,verbose_name=(_(u'vocabulary ')))

    
  
