# django-dataweb
A django project to manage semantic descriptions of web resources, using RDF vocabularies such as VoiD, RDF-Datacube, SKOS, DCAT etc

This module is based on experiences building Linked Data around geographic information served by OGC web services (as opposed to pure RDF approaches) - but is generally applicable to any service description solution.

Defines classes and RDF serialisation mappings for metadata containers that can describe data accessible via Web services. This is consistent with, but not limited to, the concept of the "Semantic Web", in that there is no requirement for data itself to be delivered as RDF via SPARQL - all we are doing is describing resources using the flexibility of semantic technologies, which will allow complex reasoning to be performed.

The short-term goal is to serialise and push RDF to a triple-store (using the rdf_io module) so that futher reasoning, such as computing closures, can be performed and exposed via an API such as the Linked Data API that uses SPARQL. 
In future, the reasoning, SPARQL and Linked Data API may be performed within the django environment. 

The model consists of two meta-classes - profiles and instances.  Profiles are sets of constraints that an instance will conform to, and provide a means for an instance to declare that conformance (an interoperability contract). Profiles provide an polymorphic inheritance from underlying base standards - and in particular support binding of vocabularies to scheme elements via the use of RDF Datacube component model.

Profiles are defined for VoiD,  RDF-Datacube metadata objects. VoiD is used (in conjunction with Dublin core and DCAT) to describe datasets and their online access service endpoints. 

RDF-Datacube is used to descibe the details of how vocabularies are used in the access points, and how multiple API methods relate to the underlying data. 

Profiles exhibit multiple-inheritance - and the intention is to provide checking to make sure that constraints are conformant to inherited constraints.  Instances may conform to multiple profiles.  For convenience a new profile may be minted with multiple parents so that multiple instances can be used

## Status
Proof of concept as part of an investigation into interoperability profiles, and the QB4ST http://w3c.github.io/sdw/qb4st/ specification.

## Dependencies
* django-rdf_io : RDF namespaces and reusable property definition and RDF serialisation toolkit
* django-skosxl : SKOS vocabulary support with pre-configured rdf_io serialisation rules

in future a separate "Feature Type Catalog" module is required, to support using ontologies and Feature Types (i.e. schemas) used by service APIs would provide a logical extension to support mappiong between closely related information models. This module currently just uses URI references, assuming that some external capability is used to publish such models.

