from django.contrib.auth.models import User
from django.contrib.sites.models import Site

import test_utils
from nose.tools import eq_

from input.urlresolvers import reverse


class ViewTestCase(test_utils.TestCase):
    def setUp(self):
        Site.objects.get_or_create(pk=1)
        u = User.objects.create(is_superuser=True, is_staff=True, username='a')
        u.set_password('b')
        u.save()

        assert self.client.login(username='a', password='b')

    def test_export_tsv(self):
        r = self.client.get(reverse('admin:myadmin.export_tsv'))
        eq_(r.status_code, 200)

    def test_export_tsv_post(self):
        r = self.client.post(reverse('admin:myadmin.export_tsv'))
        eq_(r.status_code, 200)

    def test_recluster(self):
        r = self.client.get(reverse('admin:myadmin.recluster'))
        eq_(r.status_code, 200)

    def test_recluster_post(self):
        r = self.client.post(reverse('admin:myadmin.recluster'))
        eq_(r.status_code, 302)

    def test_settings(self):
        r = self.client.get(reverse('admin:myadmin.settings'))
        eq_(r.status_code, 200)
