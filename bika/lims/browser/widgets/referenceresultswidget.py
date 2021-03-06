from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
import json

class ReferenceResultsView(BikaListingView):
    """ bika listing to display reference results for a
        Reference Sample referenceresults parameter must
        be list of dict(ReferenceResultsField value)
    """

    def __init__(self, context, request, fieldvalue, allow_edit):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.contentFilter = {'review_state': 'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.setoddeven = False
        self.pagesize = 1000
        self.allow_edit = allow_edit

        self.referenceresults = {}
        # we want current field value as a dict
        # key:uid, value:{dictionary from field list of dict}
        for refres in fieldvalue:
            self.referenceresults[refres['uid']] = refres

        self.columns = {
            'service': {'title': _('Service')},
            'result': {'title': _('Expected Result')},
            'error': {'title': _('Permitted Error %')},
            'min': {'title': _('Min')},
            'max': {'title': _('Max')}
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns':['service', 'result', 'error', 'min', 'max'],
            },
        ]

    def folderitems(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.categories = []
        services = bsc(portal_type = 'AnalysisService',
                       inactive_state = 'active',
                       sort_on = 'sortable_title')
        items = []
        for service in services:
            cat = service.getCategoryTitle
            if cat not in self.categories:
                self.categories.append(cat)
            if service.UID in self.referenceresults:
                refres = self.referenceresults[service.UID]
            else:
                refres = {'uid': service.UID,
                          'result':'',
                          'min':'',
                          'max':''}

            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                'obj': service,
                'id': service.id,
                'uid': service.UID,
                'title': service.Title,
                'category': cat,
                'selected': service.UID in self.referenceresults.keys(),
                'type_class': 'contenttype-ReferenceResult',
                'url': service.absolute_url(),
                'relative_url': service.absolute_url(),
                'view_url': service.absolute_url(),
                'service': service.Title,
                'result': refres['result'],
                'error': '',
                'min': refres['min'],
                'max': refres['max'],
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': ['result', 'error','min', 'max'],
            }
            items.append(item)

        self.categories.sort()
        for i in range(len(items)):
            items[i]['table_row_class'] = "even"

        return items

class TableRenderShim(BrowserView):
    """ This view renders the actual table.
        It's in it's own view so that we can tie it to a URL
        for javascript to re-render the table during ReferenceSample edit.
    """

    def __init__(self, context, request, fieldvalue = {}, allow_edit = True):
        """ If uid is in request, we use that reference definition's reference
            results value.  Otherwise the parameter specified here.
        """
        super(TableRenderShim, self).__init__(context, request)
        self.allow_edit = allow_edit
        if 'uid' in request:
            uc = getToolByName(context, 'uid_catalog')
            refres = uc(UID=request['uid'])[0].getObject().getReferenceResults()
            self.fieldvalue = refres
        else:
            self.fieldvalue = fieldvalue

    def __call__(self):
        """ Prints a bika listing with categorized services.
            field contains the archetypes field with a list of services in it
        """
        view = ReferenceResultsView(self.context,
                                    self.request,
                                    fieldvalue = self.fieldvalue,
                                    allow_edit = self.allow_edit)
        return view.contents_table(table_only = True)

class ReferenceResultsWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/referenceresultswidget",
        'helper_js': ("bika_widgets/referenceresultswidget.js",),
        'helper_css': ("bika_widgets/referenceresultswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None, emptyReturnsMarker = False):
        """ Return a list of dictionaries fit for ReferenceResultsField
            consumption.  Only services which have float()able entries in
            result,min and max field will be included.
        """
        value = []
        if 'service' in form:
            for uid, service in form['service'][0].items():
                try:
                    float(form['result'][0][uid])
                    float(form['min'][0][uid])
                    float(form['max'][0][uid])
                except:
                    continue
                value.append({'uid':uid,
                              'result':form['result'][0][uid],
                              'min':form['min'][0][uid],
                              'max':form['max'][0][uid]})
        return value, {}

    security.declarePublic('ReferenceResults')
    def ReferenceResults(self, field, allow_edit = False):
        """ Prints a bika listing with categorized services.
            field contains the archetypes field with a list of services in it
        """
        fieldvalue = getattr(field, field.accessor)()
        view = TableRenderShim(self,
                               self.REQUEST,
                               fieldvalue = fieldvalue,
                               allow_edit = allow_edit)
        return view()

registerWidget(ReferenceResultsWidget,
               title = 'Reference definition results',
               description = ('Reference definition results.'),
               )
