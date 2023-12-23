import time

from chibi.file import Chibi_path
from chibi.file.temp import Chibi_temp_path
from chibi_dl.site import Site
from unittest import TestCase
from unittest import TestCase, skip
from vcr_unittest import VCRTestCase


class Test_base:
    def _get_vcr_kwargs( self, **kw ):
        result = super()._get_vcr_kwargs( **kw )
        result[ 'ignore_localhost' ] = True
        return result

    def test_site_should_get_all_the_links_in_a_page( self ):
        links = list( self.site.links )
        self.assertTrue( self.site.links )


class Test_google( Test_base, VCRTestCase ):
    def setUp( self ):
        super().setUp()
        self.site = Site( url='https://www.google.com' )
