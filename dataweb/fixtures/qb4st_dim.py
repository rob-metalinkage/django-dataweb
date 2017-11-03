from dataweb.models import *
from rdf_io.models import Namespace, ObjectType,ObjectMapping,AttributeMapping 
from django.contrib.contenttypes.models import ContentType
from skosxl.models import Scheme


def load_base_namespaces():
    """
        load namespaces for the meta model
    """
    Namespace.objects.filter(prefix='qb4st').delete()
    Namespace.objects.get_or_create( uri='http://resources.opengeospatial.org/def/qbcomponents/qb4st/', defaults = { 'prefix' : 'qb4st' , 'notes': 'RDF Datacube for Spatio Temporal extensions - model' } )
    # Namespace.objects.get_or_create( uri='http://resources.opengeospatial.org/def/qbcomponents/', defaults = { 'prefix' : 'qbreg' , 'notes': 'QB component definitions register' } )    
    Namespace.objects.get_or_create( uri='http://purl.org/linked-data/cube#', defaults = { 'prefix' : 'qb' , 'notes': 'RDF Datacube' } )
    print "loading base namespaces"
    
def load_urirules() :
    """
        Load uriredirect rules for these object types.
    """
    try:
        __import__('uriredirect')
        from uriredirect.models import *
        # configs to load 
        # note we could in future possibly hit the VoiD model for the resources and bind to all the declared APIs
        #
        defaultroot = "http://resources.opengeospatial.org/def"
        api_bindings = { 'qbcomponents' : [ 
            { 'root' : defaultroot, 'apilabel' : "API - default redirects for register root", 'pattern' : None , 'term' : 'None', 'ldamethod' : 'skos/resource' } ,
            { 'root' : defaultroot, 'apilabel' : "API - default redirects for subregisters", 'pattern' : '^(?P<subregister>[^/]+)$' ,  'term' : 'None' , 'ldamethod' : 'skos/resource' } ,
            { 'root' : defaultroot, 'apilabel' : "API - default redirects for register items", 'pattern' : '^.*/(?P<term>[^\?]+)' , 'term' : '${term}', 'ldamethod' : 'qbcomponent' } ],
            'profiles' : [ 
            { 'root' : defaultroot, 'apilabel' : "API - default redirects for register root", 'pattern' : None , 'term' : 'None' , 'ldamethod' : 'skos/resource' } ,
            { 'root' : defaultroot, 'apilabel' : "API - default redirects for subregisters", 'pattern' : '^(?P<term>[^/]+)$' , 'term' : 'None',  'ldamethod' : 'skos/resource' } ,
            { 'root' : defaultroot, 'apilabel' : "API - default redirects for register items", 'pattern' : '^.*/(?P<term>[^\?]+)' , 'term' : '${term}', 'ldamethod' : 'profile' } ]
            }
        load_key = 'QB4ST API rule: '    
        RewriteRule.objects.filter(description__startswith=load_key).delete()   
        for label in api_bindings.keys() :
            for api in api_bindings[label] :
                (reg,created) = UriRegister.objects.get_or_create(label=label, defaults = { 'url' : '/'.join((api['root'],label)) , 'can_be_resolved' : True} )
                (apirule,created) = RewriteRule.objects.get_or_create(label=' : '.join((api['apilabel'],label)) , defaults = {
                    'description' : ' : '.join((load_key ,api['apilabel'],label)),
                    'parent' : None ,
                    'register' : None ,
                    'service_location' : None ,
                    'service_params' : None ,
                    'pattern' : api['pattern'] ,
                    'use_lda' : True ,
                    'view_param' : '_view' ,
                    'view_pattern' : None } )
                if not created :
                    AcceptMapping.objects.filter(rewrite_rule=apirule).delete()
                    
                if api['pattern'] :
                    path = '/${path}'
                    path_base = '/${path_base}'
                    term=api['term']
                else:
                    path = ''
                    path_base = ''
                    term='None'
                    
                for ext in ('ttl','json','rdf','xml','html') :
                    mt = MediaType.objects.get(file_extension=ext)
                    (accept,created) = AcceptMapping.objects.get_or_create(rewrite_rule=apirule,media_type=mt, defaults = {
                        'redirect_to' : "".join(('${server}/', api['ldamethod'],'?uri=',defaultroot,'/',label,path,'&_format=',ext)) } )
                # sub rules for views
                viewlist = [ {'name': 'alternates', 'apipath': ''.join(('lid/resourcelist','?baseuri=',api['root'],'/',label,path_base,'&item=',term))},  ]
                if label == 'qbcomponents' :
                    viewlist = viewlist + [ {'name': 'qb', 'apipath': ''.join(('qbcomponent','?uri=',api['root'],'/',label,'/${path}'))}, ]
                elif label == 'profiles' :
                    viewlist = viewlist + [ {'name': 'profile', 'apipath': ''.join(('profile','?uri=',api['root'],'/',label,'/${path}'))}, ]
                for view in viewlist:
                    id = ' : '.join((label,api['apilabel'],"view",view['name']))
                    (api_vrule,created) = RewriteRule.objects.get_or_create(
                        label=id,
                        defaults = {
                        'description' : ' : '.join((load_key ,api['apilabel'],label,view['name'])) ,
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
                (rule,created) = RewriteRule.objects.get_or_create(label=' : '.join(("Register",label,api['apilabel'])) , defaults = {
                    'description' : ' : '.join((load_key ,'binding to register for ',api['apilabel'],label)) ,
                    'parent' : apirule ,
                    'register' : reg ,
                    'service_location' : 'http://resources.opengeospatial.org/dna' ,
                    'service_params' : None ,
                    'pattern' : None ,
                    'use_lda' : True ,
                    'view_param' : '_view' ,
                    'view_pattern' : None } )

                
    except ImportError:
        return "Uriredirect module not available - not configured "
    except Exception as e:
        return "error configuring URI rules: %s" % e
        
def load_base_qb():
    """
        load base QB components
    """
    print "base QB4ST loaded via static ontology file"

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
    am = AttributeMapping(scope=pm, attr="sub_type_of.uri", predicate="skos:broader", is_resource=True).save()
    
    (object_type,created) = ObjectType.objects.get_or_create(uri="qb:CodedProperty", defaults = { "label" : "RDF Datacube Coded Property" })
    pm = commondim(object_type, "QBCodedDimension", "QB Coded Dimension Specific Elements" )
    am = AttributeMapping(scope=pm, attr="codelist.uri", predicate="qb:codeList", is_resource=True).save()

    #(object_type,created) = ObjectType.objects.get_or_create(uri="qb4st:CoordDimension", defaults = { "label" : "RDF Datacube Spatial Coordinate DimensionProperty" })
    #pm = commondim(object_type, "QBSpatialDimension", "QB Spatial Dimension Specific Elements" )
    #am = AttributeMapping(scope=pm, attr="crs", predicate="qb:codeList", is_resource=True).save()
 
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

