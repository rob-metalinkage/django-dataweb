from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from itertools import islice
from django.http import HttpResponse, Http404
from geonode.utils import json_response
import json
from skosxl.models import Notation, Concept

from django.views.decorators.csrf import csrf_exempt



from importlib import import_module
from dataweb.models import URIResource


def flush_all(req) :
    URIResource.objects.all().delete()
    return HttpResponse("deleted all")  


def loadbase(req) :
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()
    cfgname='cobweb_dim'
    cm = import_module("".join(('dataweb.fixtures.',cfgname)), 'gazetteer.fixtures')
    cm.load_base_namespaces()
    cm.load_base_qb()
    cm.load_rdf_mappings()
    return HttpResponse("loaded base components")  

def loadsamples(req) :
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()
    cfgname='cobweb_dim'
    cm = import_module("".join(('dataweb.fixtures.',cfgname)), 'gazetteer.fixtures')
    cm.load_sample_namespaces()
    cm.load_sample_qb()
    cm.load_sample_profiles()
    return HttpResponse("Loaded samples %s" % cfgname)       

