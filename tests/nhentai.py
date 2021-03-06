import itertools
import datetime
from unittest import TestCase, skip

from chibi.file import Chibi_path
from chibi.file.temp import Chibi_temp_path
from vcr_unittest import VCRTestCase

from chibi_dl.site.nhentai import Episode, Image
from chibi_dl.site.nhentai.site import Nhentai


class Test_ehentai( TestCase ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.helper = None
        if self.__class__ != Test_ehentai:
            self.run = TestCase.run.__get__( self, self.__class__ )
        else:
            self.run = lambda self, *args, **kwargs: None

    def test_the_urls_should_no_be_empty( self ):
        self.assertTrue( self.site.urls )

    def test_the_site_have_urls_and_be_a_episode( self ):
        for url in self.site.urls:
            self.assertIsInstance( url, Episode )

    def test_the_url_should_have_info( self ):
        for url in self.site.urls:
            data = url.info
            self.assertIn( 'title', data )
            self.assertIn( 'tags', data )

    def test_the_url_should_have_cover( self ):
        for url in self.site.urls:
            self.assertTrue( url.cover )

    def test_the_url_should_have_images( self ):
        for url in self.site.urls:
            self.assertTrue( url.images )
            for image in url.images:
                self.assertIsInstance( image, Image )

    def test_the_url_should_have_images( self ):
        for url in self.site.urls:
            self.assertTrue( url.upload_at )
            self.assertIsInstance( url.upload_at, datetime.datetime )

    def test_the_url_should_have_metadata( self ):
        self.assertTrue( self.site.urls )
        for url in self.site.urls:
            self.assertTrue( url.metadata )
            self.assertTrue( url.metadata.scan_at )
            self.assertTrue( url.metadata.title )
            self.assertTrue( url.metadata.url )
            #self.assertTrue( url.metadata.images_urls )
            self.assertTrue( url.metadata.tags )
            self.assertTrue( url.metadata.cover_url )

    def test_each_image_should_get_the_real_url_for_the_image( self ):
        self.assertTrue( self.site.urls )
        for url in self.site.urls:
            self.assertTrue( url.images )
            for image in url.images:
                self.assertNotEqual( image.url,  image.image )

    def test_download_episode_should_download_the_images( self ):
        self.assertTrue( self.site.urls )
        for url in self.site.urls:
            path = Chibi_temp_path()
            path_output = url.download( path )
            self.assertEqual( path, path_output )
            ls = list( path.ls() )
            self.assertEqual( len( url.images ), len( ls ) )
            for img in ls:
                self.assertGreater( img.properties.size, 10000 )

    def test_compress_episode_should_create_a_new_file( self ):
        self.assertTrue( self.site.urls )
        for url in self.site.urls:
            path = Chibi_temp_path()
            path_output = Chibi_temp_path()
            url.download( path )
            path_result = url.compress( path_output, path )
            self.assertTrue( path_result.endswith( 'cbz' ) )
            self.assertTrue( path_result.properties.mime, 'application/zip' )
            self.assertGreater( path_result.properties.size, 100000 )


class Test_negev_x_kar98k( Test_ehentai, VCRTestCase ):
    def setUp( self ):
        super().setUp()
        self.site = Nhentai()
        self.site.append(
            'https://nhentai.net/g/283721/' )

    def _get_vcr_kwargs( self, **kw ):
        result = super()._get_vcr_kwargs( **kw )
        result[ 'ignore_localhost' ] = True
        return result


class Test_main( VCRTestCase ):
    def setUp( self ):
        super().setUp()
        self.site = Nhentai()

    def test_when_have_url_should_iter_the_urls( self ):
        self.site.append( 'https://nhentai.net/g/283721/' )
        i = iter( self.site )
        episodes = list( itertools.islice( i, 2 ) )
        self.assertTrue( episodes )
        self.assertIsInstance( episodes[0], Episode )

    def test_when_no_have_url_should_no_do_full_scan( self ):
        i = itertools.islice( self.site, 50 )
        episodes = list( i )
        self.assertFalse( episodes )

    def test_when_have_main_url_should_do_a_full_scan( self ):
        self.site.append( 'https://nhentai.net' )
        i = itertools.islice( self.site, 50 )
        episodes = list( i )
        self.assertTrue( episodes )
        for episode in episodes:
            self.assertIsInstance( episode, Episode )
