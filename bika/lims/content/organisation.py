from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordWidget
from Products.Archetypes.public import *
from bika.lims.config import PROJECTNAME
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from bika.lims.content.bikaschema import BikaSchema, BikaFolderSchema
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from plone.app.folder.folder import ATFolder
from bika.lims.browser.fields import AddressField
from bika.lims import PMF, bikaMessageFactory as _

schema = BikaFolderSchema.copy() + BikaSchema.copy() + ManagedSchema((
    StringField('Name',
        required = 1,
        searchable = True,
        validators = ('uniquefieldvalidator',),
        widget = StringWidget(
            label = _("Name"),
        ),
    ),
    StringField('TaxNumber',
        widget = StringWidget(
            label = _("VAT number"),
        ),
    ),
    StringField('Phone',
        widget = StringWidget(
            label = _("Phone"),
        ),
    ),
    StringField('Fax',
        widget = StringWidget(
            label = _("Fax"),
        ),
    ),
    StringField('EmailAddress',
        schemata = 'Address',
        widget = StringWidget(
            label = _("Email Address"),
        ),
        validators = ('isEmail',)
    ),
    AddressField('PhysicalAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = _("Physical address"),
        ),
    ),
    AddressField('PostalAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = _("Postal address"),
        ),
    ),
    AddressField('BillingAddress',
        schemata = 'Address',
        widget = RecordWidget(
           macro = 'bika_widgets/custom_address_widget',
           label = _("Billing address"),
        ),
    ),
    StringField('AccountType',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Account Type"),
        ),
    ),
    StringField('AccountName',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Account Name"),
        ),
    ),
    StringField('AccountNumber',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Account Number"),
        ),
    ),
    StringField('BankName',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Bank name"),
        ),
    ),
    StringField('BankBranch',
        schemata = 'Bank details',
        widget = StringWidget(
            label = _("Bank branch"),
        ),
    ),
),
)

IdField = schema['id']
IdField.widget.visible = {'edit': 'visible', 'view': 'invisible'}
# Don't make title required - it will be computed from the Organisation's
# Name
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class Organisation(ATFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(CMFCorePermissions.View, 'getSchema')
    def getSchema(self):
        return self.schema

    def Title(self):
        """ Return the Organisation's Name as its title """
        return self.getField('Name').get(self)

    def getPossibleAddresses(self):
        return ['PhysicalAddress', 'PostalAddress', 'BillingAddress']

    def getPrintAddress(self):
        address_lines = []
        use_address = None
        if self.getPostalAddress().has_key('city') \
        and self.getPostalAddress()['city']:
            use_address = self.getPostalAddress()
        elif self.getPhysicalAddress().has_key('city') \
        and self.getPhysicalAddress()['city']:
                use_address = self.getPhysicalAddress()
        elif self.getBillingAddress().has_key('city') \
        and self.getBillingAddress()['city']:
            use_address = self.getBillingAddress()
        if use_address:
            if use_address['address']:
                address_lines.append(use_address['address'])
            city_line = ''
            if use_address['city']:
                city_line += use_address['city'] + ' '
            if use_address['zip']:
                city_line += use_address['zip'] + ' '
            if use_address['state']:
                city_line += use_address['state']
            if city_line:
                address_lines.append(city_line)
            if use_address['country']:
                address_lines.append(use_address['country'])


        return address_lines

registerType(Organisation, PROJECTNAME)
