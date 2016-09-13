from dataweb.models import *
from rdf_io.models import Namespace, ObjectMapping,AttributeMapping 
from django.contrib.contenttypes.models import ContentType
from skosxl.models import Scheme


def load_base_namespaces():
    """
        load namespaces for the meta model
    """
    
    Namespace.objects.get_or_create( uri='http://resources.opengeospatial.org/def/ontology/stqb/', defaults = { 'prefix' : 'qb4st' , 'notes': 'RDF Datacube for Spatio Temporal extensions' } )
    Namespace.objects.get_or_create( uri='http://purl.org/linked-data/cube#', defaults = { 'prefix' : 'qb' , 'notes': 'RDF Datacube' } )
    print "loading base namespaces"
    

def load_base_qb():
    """
        load base QB components
    """
    (d1,created) = QBSpatialDimension.objects.get_or_create(uri = "qb4st:spatialDim", defaults = 
            { 'label' : "Abstract Dimension for spatial reference",
               'is_class': True,
               "concept" : "",
               "comment" : "An abstract spatial dimension. Using any subclass of this in a specification indicates a data is a spatial dataset",
               "helptext" : "Must be implemented by binding to a particular datatype as the range" ,
            })
    (d2,created) = QBSpatialDimension.objects.get_or_create(uri = "qb4st:abstractcoord", defaults = 
        { 'label' : "Abstract Spatial Coordinate Dimension",
           'is_class': True,
           'sub_type_of': d1,
           "comment" : "Abstract Dimension for spatial reference using coordinate system. Coordinate operations may be performed on such a dimension. Note that this is a statistical dimension - with a set of identified values, as opposed to a measure, which may have any value within a certain level of precision.",
           "helptext" : "Must be bound to a specific CRS to be used" ,
        })
    print "loading base QB4ST"

def load_rdf_mappings():
    """
        load base QB components
    """
    print "loading RDF_IO mappings"


