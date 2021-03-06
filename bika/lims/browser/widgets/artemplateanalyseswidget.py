# ../../skins/bika/bika_widgets/artemplatepartitionswidget.pt
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from zope.i18n.locales import locales
from operator import itemgetter
import json

class ARTemplateAnalysesView(BikaListingView):
    """ bika listing to display Analyses table for an ARTemplate.
    """

    def __init__(self, context, request, fieldvalue, allow_edit):
        super(ARTemplateAnalysesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title',
                              'inactive_state': 'active',}
        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.setoddeven = False
        self.pagesize = 1000
        self.allow_edit = allow_edit
        self.form_id = "analyses"

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title',
                      'sortable': False,},
            'Price': {'title': _('Price'),
                      'sortable': False,},
            'Partition': {'title': _('Partition'),
                          'sortable': False,},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Price',
                         'Partition',
                         ],
             'transitions': [{'id':'empty'}, ], # none
             },
        ]

        self.fieldvalue = fieldvalue
        self.selected = [x['service_uid'] for x in fieldvalue]

    def folderitems(self):
        self.categories = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles

        items = BikaListingView.folderitems(self)

        part_ids = ['part-1']
        for s in self.fieldvalue:
            if s['partition'] not in part_ids:
                part_ids.append(s['partition'])
        partitions = [{'ResultValue':p, 'ResultText':p} for p in part_ids]

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            cat = obj.getCategoryTitle()
            items[x]['category'] = cat
            if cat not in self.categories:
                self.categories.append(cat)

            analyses = dict([(a['service_uid'], a)
                             for a in self.fieldvalue])

            items[x]['selected'] = items[x]['uid'] in analyses.keys()

            items[x]['class']['Title'] = 'service_title'

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()

            locale = locales.getLocale('en')
            currency = self.context.bika_setup.getCurrency()
            symbol = locale.numbers.currencies[currency].symbol
            items[x]['Price'] = "%s %s" % (symbol, obj.getPrice())
            items[x]['class']['Price'] = 'nowrap'
            items[x]['allow_edit'] = ['Partition']
            if not items[x]['selected']:
                items[x]['edit_condition'] = {'Partition':False}

            items[x]['required'].append('Partition')
            items[x]['choices']['Partition'] = partitions

            if obj.UID() in self.selected:
                items[x]['Partition'] = analyses[obj.UID()]['partition']
            else:
                items[x]['Partition'] = ''

            after_icons = ''
            if obj.getAccredited():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/accredited.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Accredited"))
            if obj.getReportDryMatter():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/dry.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Can be reported as dry matter"))
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_reqd.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Attachment required"))
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_no.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _('Attachment not permitted'))
            if after_icons:
                items[x]['after']['Title'] = after_icons
        self.categories.sort()
        return items

class ARTemplateAnalysesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/artemplateanalyseswidget",
        'helper_js': ("bika_widgets/artemplateanalyseswidget.js",),
        'helper_css': ("bika_widgets/artemplateanalyseswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """ Return a list of dictionaries fit for ARTemplate/Analyses field
            consumption.
        """
        bsc = getToolByName(instance, 'bika_setup_catalog')
        value = empty_marker
        service_uids = form.get('uids', None)
        Partitions = form.get('Partition', None)

        if Partitions and service_uids:
            Partitions = Partitions[0]
            for service_uid in service_uids:
                if service_uid in Partitions.keys() \
                   and Partitions[service_uid] != '':
                    value.append({'service_uid':service_uid,
                                  'partition':Partitions[service_uid]})
        if value:
            return value, {}

    security.declarePublic('Analyses')
    def Analyses(self, field, allow_edit = False):
        """ Print analyses table
        """
        fieldvalue = getattr(field, field.accessor)()
        view = ARTemplateAnalysesView(self,
                                      self.REQUEST,
                                      fieldvalue = fieldvalue,
                                      allow_edit = allow_edit)
        return view.contents_table(table_only = True)

    security.declarePublic('ARProfiles')
    def ARProfiles(self):
        """generate the ARProfiles hidden field value
        contains service details for each ARProfile
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = {}
        for p in bsc(portal_type='ARProfile',
                      inactive_state='active',
                      sort_on = 'sortable_title'):
            p = p.getObject()
            service_uids = [x.UID() for x in p.getService()]
            items[p.UID()] = service_uids
        return json.dumps(items)

registerWidget(ARTemplateAnalysesWidget,
               title = 'AR Template Analyses Layout',
               description = ('AR Template Analyses Layout'),
               )
