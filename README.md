# django-dataweb
A django project to manage semantic descriptions of web resources, using RDF vocabularies such as VoiD, RDF-Datacube, SKOS, DCAT etc

Defines classes and RDF serialisation mappings for metadata containers that can describe data accessible via Web services. This is consistent with, but not limited to, the concept of the "Semantic Web", in that there is no requirement for data itself to be delivered as RDF via SPARQL - all we are doing is describing resources using the flexibility of semantic technologies, which will allow complex reasoning to be performed.

The short-term goal is to serialise and push RDF to a triple-store (using the rdf_io module) so that futher reasoning, such as computing closures, can be performed and exposed via an API such as the Linked Data API that uses SPARQL. 
In future, the reasoning, SPARQL and Linked Data API may be performed within the django environment. 

The model consists of two meta-classes - profiles and instances.  Profiles are sets of constraints that an instance will conform to, and provide a means for an instance to declare that conformance (an interoperability contract)

Profiles are defined for VoiD,  RDF-Datacube metadata objects. VoiD is used (in conjunction with Dublin core and DCAT) to describe datasets and there online access points. RDF-Datacube is used to descibe the details of how vocabularies are used in the access points, and how multiple API methods relate to the underlying data.

Profiles exhibit multiple-inheritance - and the intention is to provide checking to make sure that constraints are conformant to inherited constraints.  Instances may conform to multiple profiles.  For convenience a new profile may be minted with multiple parents so that multiple instances can be used

## Status
in development 

## Dependencies
* django-rdf_io : RDF namespaces and reusable property definition and RDF serialisation toolkit
* django-skosxl : SKOS vocabulary support with pre-configured rdf_io serialisation rules
