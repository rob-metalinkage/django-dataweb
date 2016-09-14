from dataweb.models import *
from rdf_io.models import Namespace, ObjectType,ObjectMapping,AttributeMapping 
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

    (object_type,created) = ObjectType.objects.get_or_create(uri="qb:DimensionProperty", defaults = { "label" : "RDF Datacube DimensionProperty" })
    
    pm = commondim(object_type, "QBDimension", "QB Dimension Common Elements" )
    # specific mapping
    # am = AttributeMapping(scope=pm, attr="collection", predicate="prof:collection", is_resource=True).save()

    (object_type,created) = ObjectType.objects.get_or_create(uri="qb:CodedDimensionProperty", defaults = { "label" : "RDF Datacube Coded DimensionProperty" })
    pm = commondim(object_type, "QBCodedDimension", "QB Coded Dimension Specific Elements" )
    am = AttributeMapping(scope=pm, attr="codelist.uri", predicate="qb:codelist", is_resource=True).save()

    #(object_type,created) = ObjectType.objects.get_or_create(uri="qb4st:CoordDimension", defaults = { "label" : "RDF Datacube Spatial Coordinate DimensionProperty" })
    #pm = commondim(object_type, "QBSpatialDimension", "QB Spatial Dimension Specific Elements" )
    #am = AttributeMapping(scope=pm, attr="crs", predicate="qb:codelist", is_resource=True).save()
 
def commondim(object_type,content_type_label, title):
    content_type = ContentType.objects.get(app_label="dataweb",model=content_type_label.lower())
 
    (pm,created) =   ObjectMapping.objects.get_or_create(name=title, defaults =
        { "auto_push" : True , 
          "id_attr" : "uri",
          "target_uri_expr" : "uri",
          "content_type" : content_type
        })
    if not created :
        AttributeMapping.objects.filter(scope=pm).delete()
    
    pm.obj_type.add(object_type)
        
    am = AttributeMapping(scope=pm, attr="comment", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="label", predicate="rdfs:label", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="comment", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="helptext", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="range", predicate="rdfs:range", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="concept", predicate="qb:concept", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="sub_type_of.uri", predicate="rdfs:subPropertyOf", is_resource=True).save()
    return pm   

