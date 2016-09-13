from dataweb.models import *
from rdf_io.models import Namespace, ObjectType, ObjectMapping,AttributeMapping 
from django.contrib.contenttypes.models import ContentType
from skosxl.models import Scheme


def load_base_namespaces():
    """
        load namespaces for the meta model
    """
    
    Namespace.objects.get_or_create( uri='http://resources.opengeospatial.org/def/ontology/prof/', defaults = { 'prefix' : 'prof' , 'notes': 'Interoperability Profiles model' } )
 
    print "loading base namespaces"
    

def load_base_qb():
    """
        load base QB components
    """
    pass
    
def load_rdf_mappings():
    """
        load base QB components
    """
    print "loading RDF_IO mappings"
    content_type = ContentType.objects.get(app_label="dataweb",model="profile")
    object_type = ObjectType.objects.get_or_create(uri="prof:Profile", defaults = { "label" : "Interoperability Profile" })
    (pm,created) =   ObjectMapping.objects.get_or_create(name="Interoperability Profile RDF mapping", defaults =
        { "auto_push" : True , 
          "id_attr" : "uri",
          "target_uri_expr" : "uri",
          "obj_type" : object_type,
          "content_type" : content_type
        })
    if not created :
        AttributeMapping.objects.filter(scope=pm).delete()
    am = AttributeMapping(scope=pm, attr="comment", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="label", predicate="rdfs:label", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="is_class", predicate="prof:is_abstract", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="definedBy", predicate="rdfs:definedBy", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="implements.uri", predicate="prof:implements", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="dimensions_coded.uri", predicate="prof:dimBinding", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="dimensions_st.uri", predicate="prof:dimBinding", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="dimensions_other.uri", predicate="prof:dimBinding", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="measures_coded.uri", predicate="prof:measureBinding", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="measures_st.uri", predicate="prof:measureBinding", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="measures_other.uri", predicate="prof:measureBinding", is_resource=True).save()

    (object_type,created) = ObjectType.objects.get_or_create(uri="prof:DimensionBinding", defaults = { "label" : "Specification of a dimension component in a profile" })
    
    pm = commondim(object_type, "CodedDimensionBinding", "Interop Profile coded Dimension binding" )
    # specific mapping
    am = AttributeMapping(scope=pm, attr="collection", predicate="prof:collection", is_resource=True).save()

    pm = commondim(object_type, "CoordDimensionBinding", "Interop Profile Coordinate Dimension binding" )
    # specific mapping
    am = AttributeMapping(scope=pm, attr="crs", predicate="qb4st:crs", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="startRange", predicate="qb4st:start_range", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="endRange", predicate="qb4st:end_range", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="step", predicate="qb4st:step", is_resource=False).save()

    pm = commondim(object_type, "DimensionBinding", "Interop Profile coded Dimension binding" )
    # specific mapping


 
 
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
    am = AttributeMapping(scope=pm, attr="range", predicate="rdfs:range", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="implements.uri", predicate="qb:dimension", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="element", predicate="prof:element", is_resource=False).save()
    return pm   