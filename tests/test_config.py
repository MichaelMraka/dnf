# Copyright (C) 2012-2016 Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#

from __future__ import unicode_literals
from dnf.conf import Option, BaseConfig, Conf
from tests.support import TestCase
from tests.support import mock
from tests import support

import argparse
import dnf.conf
import dnf.exceptions
import unittest


class OptionTest(unittest.TestCase):

    class Cfg(BaseConfig):
        def __init__(self):
            super(OptionTest.Cfg, self).__init__()
            self.add_option('a_setting', Option("roundabout"))

    def test_option(self):
        cfg = self.Cfg()
        # default
        self.assertEqual(cfg.a_setting, "roundabout")
        # new value with high priority
        cfg.a_setting = "turn left"
        self.assertEqual(cfg.a_setting, "turn left")
        # new value with lower priority does nothing
        cfg.get_option('a_setting').set("turn right", dnf.conf.PRIO_DEFAULT)
        self.assertEqual(cfg.a_setting, "turn left")


class CacheTest(TestCase):

    @mock.patch('dnf.util.am_i_root', return_value=True)
    @mock.patch('dnf.const.SYSTEM_CACHEDIR', '/var/lib/spinning')
    def test_root(self, unused_am_i_root):
        conf = dnf.conf.Conf()
        self.assertEqual(conf.system_cachedir, '/var/lib/spinning')
        self.assertEqual(conf.cachedir, '/var/lib/spinning')

    @mock.patch('dnf.yum.misc.getCacheDir',
                return_value="/notmp/dnf-walr-yeAH")
    @mock.patch('dnf.util.am_i_root', return_value=False)
    @mock.patch('dnf.const.SYSTEM_CACHEDIR', '/var/lib/spinning')
    def test_noroot(self, fn_root, fn_getcachedir):
        self.assertEqual(fn_getcachedir.call_count, 0)
        conf = dnf.conf.Conf()
        self.assertEqual(conf.cachedir, '/notmp/dnf-walr-yeAH')
        self.assertEqual(fn_getcachedir.call_count, 1)


class ConfTest(TestCase):

    def test_bugtracker(self):
        conf = Conf()
        self.assertEqual(conf.bugtracker_url,
                         "https://bugzilla.redhat.com/enter_bug.cgi" +
                         "?product=Fedora&component=dnf")

    def test_overrides(self):
        conf = Conf()
        self.assertFalse(conf.assumeyes)
        self.assertFalse(conf.assumeno)
        self.assertEqual(conf.color, 'auto')

        opts = argparse.Namespace(assumeyes=True, color='never')
        conf.configure_from_options(opts)
        self.assertTrue(conf.assumeyes)
        self.assertFalse(conf.assumeno)  # no change
        self.assertEqual(conf.color, 'never')

    def test_prepend_installroot(self):
        conf = Conf()
        conf.installroot = '/mnt/root'
        conf.prepend_installroot('persistdir')
        self.assertEqual(conf.persistdir, '/mnt/root/var/lib/dnf')

    def test_ranges(self):
        conf = Conf()
        with self.assertRaises(dnf.exceptions.ConfigError):
            conf.debuglevel = '11'
