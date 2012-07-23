from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from salest.subscriptions.forms import MemberForm, DurationForm
from salest.subscriptions.views import NotMemberFormWizard

not_member_vivard = NotMemberFormWizard.as_view([MemberForm,
                                                 DurationForm])

admin.autodiscover()

urlpatterns = patterns('salest.subscriptions.views',
    url(r'^$', 'member', name='test'),
    url(r'^member_error$', not_member_vivard, name='not_member')
)
