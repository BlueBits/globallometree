import csv
import json

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.mail import mail_managers
from django.conf import settings

from haystack.views import SearchView
from haystack.query import SearchQuerySet

from .forms import DataSubmissionForm
from .models import TreeEquation, Country, DataSubmission
from django.db import connection
from .kill_gremlins import kill_gremlins

import cStringIO as StringIO
import xhtml2pdf.pisa as pisa



class DataSubmissionView(FormView):
    template_name = 'data/template.submit_data.html'
    form_class = DataSubmissionForm
    success_url = '/data/submit-data/complete/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/')
        return super(DataSubmissionView, self).dispatch(request, *args, **kwargs)


    def form_valid(self, form):      
        ds = DataSubmission()
        ds.submitted_file = form.cleaned_data['file']
        ds.submitted_notes = form.cleaned_data['notes']
        ds.user = self.request.user
        ds.imported = False
        ds.save()

        mail_managers('New GlobAllomeTree Data Submission', """

A new data file has been submitted to http://www.globallometree.org/ 

It was submitted by the user %s

To review this file and import it, please go to:

http://www.globallometree.org/admin/data/datasubmission/%s/
            """ % (ds.user, ds.id)) 


        return super(DataSubmissionView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(DataSubmissionView, self).get_context_data(**kwargs)
        context['is_page_data'] = True
        context['export_encoding'] = settings.DATA_EXPORT_ENCODING_NAME
        return context




class DataSubmissionCompleteView(TemplateView):
    template_name = 'data/template.submit_data_complete.html'

    def get_context_data(self, **kwargs):
        context = super(DataSubmissionCompleteView, self).get_context_data(**kwargs)
        context['is_page_data'] = True

        return context



def continents_map(request):
    return render_to_response('continents_map.html',
                              context_instance = RequestContext(request,
                              {'is_page_data': True, }))

def tree_equation_id(request, id):
    tree_equation = TreeEquation.objects.get(ID=id)
    return render_to_response('data/template.tree_equation.html', 
                              context_instance = RequestContext(request,
                              {'tree_equation': tree_equation, 
                               'is_page_data' : True})) 

def tree_equation_id_pdf(request, id):
    tree_equation = TreeEquation.objects.get(ID=id)

    template = get_template('data/template.tree_equation.pdf.html')

   
    html = template.render(Context({
        'tree_equation': tree_equation
    }))

    def fetch_resources(uri, rel):
        path = 'ERROR'
        if uri[0:6] == 'static':
            path = settings.STATIC_ROOT + uri[6:]
        elif uri[0:5] == 'media':
            path = settings.MEDIA_ROOT + uri[5:]
        print uri, path
        return path

    buffer = StringIO.StringIO()
    pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")),
                      buffer,
                      link_callback=fetch_resources)

    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=TreeEquation_%s.pdf' % tree_equation.ID

    response.write(pdf)
    return response


def geo_map(request):
    query = 'SELECT "Country_id", COUNT(1) AS id_count FROM data_treeequation GROUP BY "Country_id"';
    cursor = connection.cursor()
    cursor.execute(query)
    countries = cursor.fetchall()

    country_list = []

    for country_id, count in countries:
        if country_id is not None:
            country = Country.objects.get(pk=country_id)
            name = country.formal_name or country.common_name
            country_list.append({ 'name' : name,
                                  'count' : int(count),
                                  'code' : country.iso_3166_1_2_letter_code.upper()
                                })

    return render_to_response('geo_map.html',
                               context_instance = RequestContext(request,
                                {'country_list': country_list,
                                 'is_page_data' : True,
                                 }))

def geo_map_id(request, geo_id):
    country = Country.objects.get(iso_3166_1_2_letter_code = geo_id)
    return HttpResponseRedirect('/data/search/?Country=' + country.common_name)
    
def database(request):
    return render_to_response('database.html',
                              context_instance = RequestContext(request,
                             {'is_page_data' : True}))


def species(request, selected_Genus=None):
    
    #Call sorl for a faceted list of Genus
    sqs = SearchQuerySet().facet('genus')
    genus_list = []
    for genus_count in sqs.facet_counts()['fields']['Genus']:
        genus_list.append({
            'name'  : genus_count[0],
            'count' : genus_count[1]
        
        })
    
    #Sort the list alphabetically by name
    genus_list.sort(key=lambda x : x['name'])
    
    return render_to_response('data/template.species.html', 
                               context_instance = RequestContext(request,
                               {'genus_list': genus_list,
                               'is_page_data' : True }))




class EquationSearchView(SearchView):
    
    def __name__(self):
        return "EquationSearchView"

    def extra_context(self):

        no_query_entered = not bool(len(self.request.GET.keys()))

        return {'is_page_data' : True,
                'no_query_entered' : no_query_entered}

    def create_response(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/')
        return super(EquationSearchView, self).create_response( *args, **kwargs)

def autocomplete(request, field): 
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/')
        
    term    = request.GET.get('term') 
    sqs     = SearchQuerySet()
    
    kwargs = {field + '_auto':term} #ex) country_auto for the autocomplete index of country
    sqs    = SearchQuerySet().facet(field).filter(**kwargs)

    result_counts = sqs.facet_counts()['fields'][field]
    
    result = {'options':[]}

    for result_count in result_counts:
        result['options'].append(result_count[0])

    return HttpResponse(json.dumps(result), mimetype='application/json; charset=utf8')

from .forms import EquationSearchForm


def export(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/')

    ignore_fields = ['data_submission',]

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/')

    form = EquationSearchForm(request.GET)
    sqs = form.search()
   
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=db-equations.txt'
    writer = csv.writer(response, delimiter='\t')
    # Write headers to CSV file
    headers = []
    for field in TreeEquation._meta.fields:
        if field.name in ignore_fields:
            continue
        headers.append(field.name.encode(settings.DATA_EXPORT_ENCODING))
    writer.writerow(headers)
    # Write data to CSV file
    
    for result in sqs:
        obj = TreeEquation.objects.get(pk=result.id)
        row = []
        for field in TreeEquation._meta.fields:
            if field.name in ignore_fields:
                continue
            val = getattr(obj, field.name)

            if type(val) == bool:
                if val:
                    val = 'True'
                else:
                    val = 'False'
            elif val in [None, '']:
                val = 'None'
           
            if type(val) != unicode:
                val = unicode(val)

            try:
                val_encoded = val.encode(settings.DATA_EXPORT_ENCODING)
            except:
                val = kill_gremlins(val)
                try:
                    val_encoded = val.encode(settings.DATA_EXPORT_ENCODING)
                except:

                    val_encoded = ''
                    for letter in val:
                        try:
                            letter = letter.encode(settings.DATA_EXPORT_ENCODING)
                        except:
                            letter = '?'
                        val_encoded += letter

            row.append(val_encoded)
        writer.writerow(row)
    return response