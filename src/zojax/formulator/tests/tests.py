##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" zojax.formulator tests

$Id$
"""
import os, unittest, doctest
from zope import interface, component, event
from zope.app.component.hooks import setSite
from zope.app.testing import functional
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.security.interfaces import IAuthentication
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.container.contained import ObjectAddedEvent
from zope.app.rotterdam import Rotterdam
from zope.app.component.site import LocalSiteManager, SiteManagementFolder

from zojax.authentication.interfaces import IAuthenticationConfiglet
from zojax.personal.space.manager import PersonalSpaceManager
from zojax.principal.profile.interfaces import IProfilesCategory
from zojax.catalog.catalog import Catalog, ICatalog
from zojax.layoutform.interfaces import ILayoutFormLayer

from content import Portal


zojaxFormulatorLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxFormulatorLayer', allow_teardown=True)


class PrincipalInformation(object):

    readonly = True
    firstname = u''
    lastname = u''
    email = u''

    def __init__(self, principal):
        self.principal = principal


def FunctionalDocFileSuite(*paths, **kw):
    layer = zojaxFormulatorLayer

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        root = functional.getRootFolder()
        portal = Portal()
        event.notify(ObjectCreatedEvent(portal))
        root['portal'] = portal
        sm = LocalSiteManager(portal)
        portal.setSiteManager(sm)
        setSite(portal)
        sm = portal.getSiteManager()
        portal['ids'] = IntIds()
        sm.registerUtility(portal['ids'], IIntIds)

        portal['catalog'] = Catalog()
        sm.registerUtility(portal['catalog'], ICatalog)

        authconfiglet = sm.getUtility(IAuthenticationConfiglet)
        authconfiglet.installUtility()

        sm.getUtility(IAuthentication)._caching = False




    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old|doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


def test_suite():
    return unittest.TestSuite((
            FunctionalDocFileSuite("testbrowser.txt"),
            ))
