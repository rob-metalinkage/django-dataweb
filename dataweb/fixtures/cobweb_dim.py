from dataweb.models import *
from rdf_io.models import Namespace, ObjectMapping,AttributeMapping 

from skosxl.models import Scheme


def load_base_namespaces():
    """
        load namespaces for the meta model
    """
    Namespace.objects.get_or_create( uri='http://resources.opengeospatial.org/def/bp/cobweb/', defaults = { 'prefix' : 'cobweb' , 'notes': 'COBWEB project citizen science proof of concept' } )
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

def load_sample_namespaces():
    """
        load namespaces for the samples
    """
    print "loading samnple namespaces"

def load_sample_qb():
    """
        load namespaces for the samples
    """
    print "loading sample QB components"
    
    (gbif_sch,created) = Scheme.objects.get_or_create(uri="proxy:gbif/taxon", defaults = { 'pref_label' :"GBIF Taxon Scheme" })
    (cobweb_user_sch,created) = Scheme.objects.get_or_create(uri="http://resources.opengeospatial.org/def/voc/examples/cobwebusers",
        defaults = { 'pref_label' :"COBWEB Users" })

    
    (d1,created) = QBCodedDimension.objects.get_or_create(uri = "cobweb:biotaDimension", defaults = 
            { 'label' : "Abstract Dimension for Biota bound to a controlled vocabulary",
               'is_class': True,
               "concept" : "http://lod.taxonconcept.org/ontology/void.rdf#TaxonConcept",
               "helptext" : "This dimension declares the semantic content - to be used a specialised subtype must be defined binding the dimension to a specific codelist, such as GBIF taxon keys" 
            })

    (d2,created) = QBCodedDimension.objects.get_or_create(uri = "cobweb:Biota_GBIF", defaults = 
            { 'label' : "Biota dimension using the GBIF taxon vocabulary",
               'is_class': False,
               'sub_type_of': d1,
               'codelist' : gbif_sch,
               "helptext" : "Requires that a binding to the GBIF taxon dimension is provided (concrete bindings only need to define the element that is bound to this dimension)",
               "comment" : "This Dimension is to be used for a service or dataset that uses any GBIF taxa as search/query parameters. pecialised subdimensions are defined for typical cases such as species, etc. Further specialisations may be defined for specific ranges of such keys." 
            })   

    (d3,created) = QBCodedDimension.objects.get_or_create(uri = "cobweb:Species_GBIF", defaults = 
            { 'label' : "Species Specific Dimension using GBIF taxon keys",
               'is_class': False,
               'sub_type_of': d2,
               'concept' : "proxy:gbif/taxontypes/Species",
               "helptext" : "A dimension using only species level codes from the GBIF taxon hierarchy." 
            })       
         
    (d4,created) = QBCodedDimension.objects.get_or_create(uri = "cobweb:user_dim", defaults = 
            { 'label' : "COBWEB User Identification",
               'is_class': False,
               "concept" : "cobweb:User",
               "range" : "cobweb:User",
               "codelist" : cobweb_user_sch,
               "comment" : "Must be bound to a specific element in a technology-specific profile to be implemented.",
               "helptext" : "COBWEB requires that all observers are registered users. This includes any anonymous users established for specific surveys, which should survey-specific reasons for supporting anonymous users." ,
            })  

def load_sample_profiles():
    """
        load namespaces for the samples
    """
    d_species = QBCodedDimension.objects.get(uri = "cobweb:Species_GBIF")
    d_taxon = QBCodedDimension.objects.get(uri = "cobweb:Biota_GBIF")
    d_user =  QBCodedDimension.objects.get(uri = "cobweb:user_dim")  

    
    (db_jkw,created) = CodedDimensionBinding.objects.get_or_create(uri = "cobweb:jkw", defaults = 
        { 'label' : "Japanese Knotweed specific observation",
           'implements': d_species,
           "range" : "http://resources.opengeospatial.org/def/proxy/gbif/taxon/5334357",
           "isConstant" : True, 
           "comment" : "Example dimension bound to a single valued range",
        }) 
    
    (db_invasive_species,created) = CodedDimensionBinding.objects.get_or_create(uri = "cobweb:invasive_species", defaults = 
        { 'label' : "Registered Invasive Species",
           'implements': d_species,
           "isConstant" : False, 
           "comment" : "Example dimension bound to a collection which defines a subset of terms from the underlying codelist",
           "collection" : "<http://prophet.ucd.ie/ontology/cobweb/skos_gbif#Invasive_Plant_Species>",
        }) 
    
    (db_gbif_species,created) = CodedDimensionBinding.objects.get_or_create(uri = "cobweb:species", defaults = 
        { 'label' : "GBIF Species specific taxon codes",
           'implements': d_species,
           "isConstant" : False, 
           "comment" : "component binding a species dimension to a data structure (i.e. the property name)",
       }) 
    
    (db_gbif_species_swe,created) = CodedDimensionBinding.objects.get_or_create(uri = "cobweb:species_swe", defaults = 
        { 'label' : "SWE record species binding",
           'implements': d_species,
           "isConstant" : False, 
           "comment" : "binds species ID to the SWE data record structure",
           'element' : "om:Observation/om:result/swe:DataRecord/swe:field[@name='taxon']/swe:identifier" ,
           
       }) 
    
    (db_user,created) = CodedDimensionBinding.objects.get_or_create(uri = "cobweb:user", defaults = 
        { 'label' : "COBWEB User Id",
           'implements': d_user,
           "isConstant" : False, 
           "comment" : "Binds abstract user dimension to a profile.",
        })

    (db_user_swe,created) = CodedDimensionBinding.objects.get_or_create(uri = "cobweb:user_swe", defaults = 
        { 'label' : "COBWEB User Id - SWE binding",
           'implements': d_user,
           "isConstant" : False, 
           "comment" : "Binds user dimension to SWE standard data model.",
           "element" : "om:Observation/om:metadata/md:CI_ResponsibleParty"
        })

    (p_cobweb,created) = Profile.objects.get_or_create(uri = "cobweb:observation", defaults = 
        { 'label' : "COBWEB general observation metadata",
           "comment" : "An interoperability profile for all COBWEB observations. Defines the user identification requirement but could be extended to include classifications, procedures, survey types",
           'is_class': False,
           })
    p_cobweb.dimensions_coded.add( db_user )

    (p_cobweb_swe,created) = Profile.objects.get_or_create(uri = "cobweb:observation_swe", defaults = 
        { 'label' : "COBWEB SWE binding for user identification",
           "comment" : "Profile for all data using a COBWEB identifier in a SWE record to identify the observer",
           'is_class': False,
           })
    p_cobweb_swe.implements.add( p_cobweb)
    p_cobweb_swe.dimensions_coded.add( db_user_swe )
    
    (p_gbif_species,created) = Profile.objects.get_or_create(uri = "cobweb:gbif_species_occurrence", defaults = 
        { 'label' : "GBIF compatible species occurence",
          'definedBy' : "http://www.gbif.org/publishing-data/quality#occurrence",
           "comment" : "Describes all the necessary fields for a species survey to be compatible with the Global Biodiversity Information Facilty. this is not complete - just an example to show how external requirements can be partially described",
           'is_class': False,
        })
    p_gbif_species.dimensions_coded.add( db_gbif_species )
    
    (p_jkw,created) = Profile.objects.get_or_create(uri = "cobweb:prof_jkw_survey", defaults = 
        { 'label' : "Japanese Knotweed specific observation",
           'is_class': False,
           'definedBy' : "http://cobweb.org/methods/surveys/invasive_species/japanese_knotweed",
           "comment" : "The interoperability profile for a specific single species survey",
        })
    p_jkw.implements.add( p_cobweb, p_gbif_species)
    p_jkw.dimensions_coded.add( db_jkw )
 
    (p_gbif_swe,created) = Profile.objects.get_or_create(uri = "cobweb:prof_species_swe4cs", defaults = 
        { 'label' : "COBWEB species survey SWE",
           'is_class': False,
           "comment" : "Profile for a SWE encoded GBIF species occurences using COBWEB - binds the taxon code to a specific SWE record data element",
        })
    p_gbif_swe.implements.add( p_cobweb_swe, p_gbif_species)
    p_gbif_swe.dimensions_coded.add( db_gbif_species_swe )
     
    (p_jkw_swe,created) = Profile.objects.get_or_create(uri = "cobweb:prof_jkw_swe4cs", defaults = 
        { 'label' : "COBWEB Japanese Knotweed survey SWE",
          'is_class': False,
           "comment" : "Shows how a profile can be defined down to the level of a specific term - ie. holding a dimension constant for the entire dataset, but allowing it to be combined with other data with different values",
        })
    p_jkw_swe.implements.add( p_jkw, p_cobweb_swe, p_gbif_swe)
 
    print "loading sample profiles"
     

