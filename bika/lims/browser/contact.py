from Acquisition import aq_parent, aq_inner, aq_base
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import json

class ContactLoginDetailsView(BrowserView):
    """ The contact login details edit
    """
    template = ViewPageTemplateFile("templates/contact_login_details.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.form.has_key("submitted"):
            return contact_logindetails_submit(self.context, self.request)
        else:
            return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

def contact_logindetails_submit(context, request):

    def missing(field):
        message = PMF("Input is required but not given.")
        errors.append(field + ': ' + message)

    def nomatch(field):
        message = PMF("Passwords do not match.")
        errors.append(field + ': ' + message)

    def minlimit(field):
        message = PMF("Passwords must contain at least 5 letters.")
        errors.append(field + ': ' + message)

    form = request.form

    if form.has_key("save_button"):
        contact = context
    password = form['password']
    username = form['username']
    confirm = form['confirm']
    email = form['email']
    errors = []

    if not username:
        missing('username')

    if not email:
        missing('email')

    reg_tool = context.portal_registration
    properties = context.portal_properties.site_properties
##    if properties.validate_email:
##        password = reg_tool.generatePassword()
##    else:
    if password!=confirm:
        nomatch('password')
        nomatch('confirm')

    if not password:
        missing('password')

    if not confirm:
        missing('confirm')

    if len(password) < 5:
        minlimit('password')
        minlimit('confirm')

    if errors:
        return json.dumps({'errors':errors})

    try:
        reg_tool.addMember(username,
                           password,
                           properties = {
                               'username': username,
                               'email': email,
                               'fullname': username})
    except ValueError, msg:
        return json.dumps({'errors': [str(msg),]})

    contact.setUsername(username)
    contact.setEmailAddress(email)
    contact.reindexObject()

    # Give contact an Owner local role on client
    contact.aq_parent.manage_setLocalRoles( username, ['Owner',] )
    if hasattr(aq_base(contact.aq_parent), 'reindexObjectSecurity'):
        contact.aq_parent.reindexObjectSecurity()

    # add user to Clients group
    group=context.portal_groups.getGroupById('Clients')
    group.addMember(username)

##    if properties.validate_email or request.get('mail_me', 0):
##        reg_tool.registeredNotify(username)

    message = "Registered"
    context.plone_utils.addPortalMessage(message, 'info')
    return json.dumps({'success':message})
