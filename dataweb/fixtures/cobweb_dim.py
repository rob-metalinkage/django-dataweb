from dataweb.models import QBDimension, QBCodedDimension
from skosxl.models import Scheme

QB.Dimension.objects.all().delete()
d1 = QBDimension(uri = "cobweb:biotaDimension", label = "Abstract Dimension for Biota bound to a controlled vocabulary", is_class=True)
d1.save()
d2 = QBCodedDimension(uri = "cobweb:Biota_GBIF", label = "Biota dimension using the GBIF taxon vocabulary", codelist = Scheme.objects.get_by_natural_key("proxy:gbif"),
			helptext = "This Dimension is to be used for a service or dataset that uses any GBIF taxa as search/query parameters. \r\nSpecialised subdimensions are defined for typical cases such as species, etc. \r\nFurther specialisations may be defined for specific ranges of such keys.",sub_type_of=d1, is_class=True)
d2.save()
d3 = QBCodedDimension(uri = "cobweb:Species_GBIF", label = "Species Specific Dimension using GBIF taxon keys", concept = "proxy:gbif/taxontypes/Species", sub_type_of=d2, is_class=True, helptext = "A dimension using only species level codes from the GBIF taxon hierarchy.")
d3.save()
"""
 {
		"pk" : null,
		"model" : "dataweb.uriresource",
		"fields" : {
			"uri" : "sdmx:refArea",
			"label" : "reference Area Dimension as used by the SDMX "
		}
	}, {
		"pk" : null,
		"model" : "dataweb.uriresource",
		"fields" : {
			"uri" : "ogc:SpatialDimension",
			"label" : "An abstract dimension for described spatial location"
		}
	},
    {{, {
		"pk" : null,
		"model" : "dataweb.qbcodeddimension",
		"fields" : {
			"concept" : "proxy:gbif/taxontypes/Species",
			"range" : "",
			"codelist" : null,
			"helptext" : "A dimension using only species level codes from the GBIF taxon hierarchy."
		}
	}, {
		"pk" : null,
		"model" : "dataweb.voidtechnicalfeature",
		"fields" : {
			"sub_type_of" : "ip:urltemplate",
			"url_template" : "http://mdgs.un.org/unsd/mdg/Data.aspx?cr={_item}",
			"is_class" : false
		}
	}, {
		"pk" : null,
		"model" : "dataweb.voidtechnicalfeature",
		"fields" : {
			"sub_type_of" : null,
			"url_template" : "",
			"is_class" : true
		}
	}
]
"""