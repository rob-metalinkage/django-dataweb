from dataweb.models import *
from rdf_io.models import Namespace, ObjectType,ObjectMapping,AttributeMapping 
from django.contrib.contenttypes.models import ContentType
from skosxl.models import Scheme


def load_base_namespaces():
    """
        load namespaces for the meta model
    """
    
    Namespace.objects.get_or_create( uri='http://resources.opengeospatial.org/def/ontology/qb4st/', defaults = { 'prefix' : 'qb4st' , 'notes': 'RDF Datacube for Spatio Temporal extensions - model' } )
    Namespace.objects.get_or_create( uri='http://resources.opengeospatial.org/def/qbcomponents/', defaults = { 'prefix' : 'qbreg' , 'notes': 'QB component definitions register' } )    
    Namespace.objects.get_or_create( uri='http://purl.org/linked-data/cube#', defaults = { 'prefix' : 'qb' , 'notes': 'RDF Datacube' } )
    print "loading base namespaces"
    
def load_urirules() :
    """
        Load uriredirect rules for these object types.
    """
    try:
        __import__('uriredirect')
        from uriredirect.models import *
        for label in ('qbcomponents','profiles') :
            (reg,created) = UriRegister.objects.get_or_create(label=label, defaults = { 'url' : '/'.join(("http://resources.opengeospatial.org/def",label)) , 'can_be_resolved' : True} )
            (apirule,created) = RewriteRule.objects.get_or_create(label=':'.join(("API - default redirects for register",label)) , defaults = {
                'description' : '' ,
                'parent' : None ,
                'register' : None ,
                'service_location' : None ,
                'service_params' : None ,
                'pattern' : '^.*/(?P<term>[^\?]+)' ,
                'use_lda' : True ,
                'view_param' : '_view' ,
                'view_pattern' : None } )
            if not created :
                AcceptMapping.objects.filter(rewrite_rule=apirule).delete()
            for ext in ('ttl','json','rdf','xml','html') :
                mt = MediaType.objects.get(file_extension=ext)
                (accept,created) = AcceptMapping.objects.get_or_create(rewrite_rule=apirule,media_type=mt, defaults = {
                    'redirect_to' : "".join(('${server}/', label[:-1],'?uri=http://resources.opengeospatial.org/def/',label,'/${path}&_format=',ext)) } )
            # sub rules for views
            viewlist = [ {'name': 'alternates', 'apipath': ''.join(('lid/resourcelist','?baseuri=http://resources.opengeospatial.org/def/',label,'/${path_base}&item=${term}'))},  ]
            if label == 'qbcomponents' :
                viewlist = viewlist + [ {'name': 'qb', 'apipath': ''.join(('qbcomponent','?uri=http://resources.opengeospatial.org/def/',label,'/${path}'))}, ]
            elif label == 'profiles' :
                viewlist = viewlist + [ {'name': 'profile', 'apipath': ''.join(('profile','?uri=http://resources.opengeospatial.org/def/',label,'/${path}'))}, ]
            for view in viewlist:
                id = ''.join(("API for ",label," : view ",view['name']))
                (api_vrule,created) = RewriteRule.objects.get_or_create(
                    label=id,
                    defaults = {
                    'description' : '' ,
                    'parent' : apirule ,
                    'register' : None ,
                    'service_location' : None ,
                    'service_params' : None ,
                    'pattern' : None ,
                    'use_lda' : True ,
                    'view_param' : '_view' ,
                    'view_pattern' : view['name'] } )
                for ext in ('ttl','json','rdf','xml','html') :
                    mt = MediaType.objects.get(file_extension=ext)
                    (accept,created) = AcceptMapping.objects.get_or_create(rewrite_rule=api_vrule,media_type=mt, defaults = {
                    'redirect_to' : "".join(('${server}/', view['apipath'],'&_format=',ext)) } )
 
            # bind to API
            (rule,created) = RewriteRule.objects.get_or_create(label=':'.join(("API - binding for :",label)) , defaults = {
                'description' : '' ,
                'parent' : apirule ,
                'register' : reg ,
                'service_location' : 'http://192.168.56.151:8080/dna' ,
                'service_params' : None ,
                'pattern' : None ,
                'use_lda' : True ,
                'view_param' : '_view' ,
                'view_pattern' : None } )

                
    except ImportError:
        print "Uriredirect module not available - not configured "
    except Exception as e:
        print "error configuring URI rules: %s" % e
        
def load_base_qb():
    """
        load base QB components
    """
    (d1,created) = QBSpatialDimension.objects.get_or_create(uri = "qbreg:qb4st/spatialDim", defaults = 
            { 'label' : "Abstract Dimension for spatial reference",
               'is_class': True,
               "concept" : "",
               "comment" : "An abstract spatial dimension. Using any subclass of this in a specification indicates a data is a spatial dataset",
               "helptext" : "Must be implemented by binding to a particular datatype as the range" ,
            })
    (d2,created) = QBSpatialDimension.objects.get_or_create(uri = "qbreg:qb4st/abstractcoord", defaults = 
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
    am = AttributeMapping(scope=pm, attr="comment", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="label", predicate="rdfs:label", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="comment", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="helptext", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="range", predicate="rdfs:range", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="concept", predicate="qb:concept", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="sub_type_of.uri", predicate="qb4st:implements", is_resource=True).save()
    
    (object_type,created) = ObjectType.objects.get_or_create(uri="qb:CodedProperty", defaults = { "label" : "RDF Datacube Coded Property" })
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
        

    return pm   

