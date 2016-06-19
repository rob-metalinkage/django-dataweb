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
    uri         = models.CharField(blank=True,max_length=250,verbose_name=_(u'URI'),editable=True)   
    label  = models.CharField(_(u'label'),blank=True,max_length=255)
    slug        = exfields.AutoSlugField(populate_from=('uri'))
   
    def __unicode__(self):
        return self.label
        
    def natural_key(self):
        return( self.uri )
        

   
class QBDimension(URIResource):
    """
        A RDF-Datacube Dimension. If is_class is set True then this will be treated as a class and its declared sub_types will inherit the properties. 
        A Class will also be rendered using a rdfs and OWL class formalism unless a OWL class definition link is provided. If one is provided this will be loaded to the target triple store.
    """
    objects = URIResourceManager()
    is_class = models.BooleanField(help_text=_(u'Check if this is a class of Dimensions'))  
    owl = models.URLField(null=True, blank=True,help_text=_(u'Canonical OWL definition. With an RDF-IO mappings this may be propagated to the target RDF datastore, or generated automatically'))  
    sub_type_of = models.ForeignKey('self',null=True, blank=True,help_text=_(u'Specialises this as base definition.'), limit_choices_to={'is_class' : True})
    # core_type = models.ForeignKey('self', null=True, blank=True, limit_choices_to={'uri__startswith' : 'qb:' })
 
class QBCodedDimension(QBDimension):
    """
        A RDF-Datacube Coded Dimension. Binds the domain and range of a dimension to a SKOS resource with optional data typing.
    """
    codelist = models.ForeignKey(Scheme, null=True, blank=True,help_text=_(u'SKOS Concept Scheme'))
    concept = models.CharField(blank=True,max_length=250,help_text=_(u'RDFS Data Type. This specifies the domain - i.e. type of Concept from the target Concept Scheme needed.'))
    range = models.CharField(blank=True,max_length=250,help_text=_(u'RDFS Data Type. This specifies the allowable values)'))
    helptext = models.TextField(max_length=5000, help_text=_(u'Usage text for this dimension'))

    
class VoidTechnicalFeature(URIResource):
    is_class = models.BooleanField(help_text="Check if this is a abstract class of features")  
    sub_type_of = models.ForeignKey('self',null=True, blank=True,help_text=_(u'Specialises this as base definition.'))
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
    sub_type_of = models.ForeignKey('self',null=True, blank=True,help_text=_(u'Specialises this as base definition.'))
    urispace = models.CharField(blank=True,null=True,max_length=250,help_text=_(u'URI namespace of the members of this Dataset)'))

    feature = models.ManyToManyField(VoidTechnicalFeature,null=True, blank=True,symmetrical=False, 
                                            verbose_name=(_(u'Technical Feature')))
    sparql = models.URLField(null=True, blank=True,help_text=_(u'SPARQL endpoint for this dataset'))
    search = models.URLField(null=True, blank=True,help_text=_(u'Opensearch endpoint for this dataset'))                                          
    # vocabulary = models.ManyToManyField(Scheme,null=True,symmetrical=False,verbose_name=(_(u'vocabulary ')))

        
class VoidDatasetMeta(models.Model):
    """
        extensible metadata using rdf_io managed reusable generic metadata properties
    """
    dataset      = models.ForeignKey(VoidDataset) 
    metaprop   =  models.ForeignKey(GenericMetaProp) 
    value = models.CharField(_(u'value'),max_length=500)
 