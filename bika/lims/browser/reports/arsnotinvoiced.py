from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import formatDateQuery, formatDateParms, TimeOrDate
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from decimal import Decimal
import json
import plone

class ARsNotInvoiced(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("report_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        bc = getToolByName(self.context, 'bika_catalog')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Analysis requests not invoiced")
        headings['subheader'] = _("Published Analysis Requests which have not been invoiced")

        count_all = 0

        query = {'portal_type': 'AnalysisRequest',
                 'getInvoiced': False,
                 'review_state': 'published',
                 'sort_order': 'reverse'}

        date_query = formatDateQuery(self.context, 'c_DatePublished')
        if date_query:
            query['getDatePublished'] = date_query
            pubished = formatDateParms(self.context, 'c_DatePublished') 
        else:
            pubished = 'Undefined'
        parms.append(
            { 'title': _('Published'),
             'value': pubished,
             'type': 'text'})

        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            cancellation_state = wf_tool.getTitleForStateOnType(
                        self.request.form['cancellation_state'], 'AnalysisRequest')
        else:
            cancellation_state = 'Undefined'
        parms.append(
            { 'title': _('Active'),
             'value': cancellation_state,
             'type': 'text'})



        # and now lets do the actual report lines
        formats = {'columns': 6,
                   'col_heads': [ _('Client'), \
                                  _('Request'), \
                                  _('Sample type'), \
                                  _('Sample point'), \
                                  _('Published'), \
                                  _('Amount'), \
                                  ],
                   'class': '',
                  }

        datalines = []
        clients = {}
        sampletypes = {}
        samplepoints = {}
        categories = {}
        services = {}
        
        for ar_proxy in bc(query):
            ar = ar_proxy.getObject()

            dataline = []

            dataitem = {'value': ar.aq_parent.Title()}
            dataline.append(dataitem)

            dataitem = {'value': ar.getRequestID()}
            dataline.append(dataitem)

            dataitem = {'value': ar.getSampleTypeTitle()}
            dataline.append(dataitem)

            dataitem = {'value': ar.getSamplePointTitle()}
            dataline.append(dataitem)

            dataitem = {'value': TimeOrDate(self.context, ar.getDatePublished())}
            dataline.append(dataitem)

            dataitem = {'value': ar.getTotalPrice()}
            dataline.append(dataitem)


            datalines.append(dataline)

            count_all += 1

        # table footer data
        footlines = []
        footline = []
        footitem = {'value': _('Number of analyses retested for period'),
                    'colspan': 5,
                    'class': 'total_label'} 
        footline.append(footitem)
        footitem = {'value': count_all} 
        footline.append(footitem)
        footlines.append(footline)


        self.report_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines}


        return self.template()

    

