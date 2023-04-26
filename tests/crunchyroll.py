from collections import Counter
from unittest.mock import patch
import itertools
import time
from unittest import TestCase, skip
from chibi_dl.site.crunchyroll import Crunchyroll, Serie, Episode
from chibi_dl.site.crunchyroll.subtitles import Subtitle
from chibi_dl.site.crunchyroll.exceptions import Episode_not_have_media
from vcr_unittest import VCRTestCase
from chibi.file.temp import Chibi_temp_path
from chibi.atlas import Chibi_atlas


class Test_crunchyroll( TestCase ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.helper = None
        if self.__class__ != Test_crunchyroll:
            self.run = TestCase.run.__get__( self, self.__class__ )
        else:
            self.run = lambda self, *args, **kwargs: None

    def test_iter_a_serie( self ):
        with self.subTest( "should have urls" ):
            self.assertTrue( self.site.urls )
        series = list( filter(
            lambda x: isinstance( x, Serie ), self.site.urls ) )
        with self.subTest( "at least should have one serie" ):
            self.assertTrue( series )

        serie = series[0]
        episodes = list( itertools.islice( serie, 2 ) )
        with self.subTest( "the series should have episodes" ):
            self.assertTrue( episodes )
            for episode in episodes:
                self.assertIsInstance( episode, Episode )

        subtitles = []
        for episode in episodes:
            with self.subTest( "each episode should have info" ):
                self.assertTrue( episode.info )
                self.assertIsInstance( episode.info, Chibi_atlas )

            with self.subTest( "each episode should have stream" ):
                self.assertTrue( episode.stream )
                self.assertTrue( episode.stream.uri )

            with self.subTest(
                    "the episode should have subtitles", episode=episode ):
                self.assertTrue( episode.subtitles )
                subtitles += episode.subtitles[:2]

            for subtitle in episode.subtitles:
                with self.subTest(
                        "subtitle should have a iso lang", subtitle=subtitle ):
                    iso_lang = subtitle.lang_ISO_639_2
                    self.assertTrue( iso_lang )

        subtitles = subtitles[:2]
        with self.subTest( "the subtitles should have info" ):
            for subtitle in subtitles:
                self.assertTrue( subtitle.info )
                self.assertIsInstance( subtitle.info, Chibi_atlas )

        with self.subTest( "the subtitles should have be tranformed ot ass" ):
            for subtitle in subtitles:
                ass = subtitle.ass
                self.assertIsInstance( ass, str )
                self.assertTrue( ass )

        with self.subTest( "subtitle download should write the ass file" ):
            for subtitle in subtitles:
                download_path = Chibi_temp_path()
                subtitle_path = subtitle.download( download_path )
                self.assertTrue( subtitle_path.exists )
                self.assertEqual( subtitle_path.open().read(), subtitle.ass )

        with self.subTest( "episode should have a stream" ):
            for episode in episodes:
                stream = episode.stream
                self.assertIsNotNone( stream )
                self.assertTrue( stream.uri )

        with self.subTest( "when download the stream should run ffmpeg" ):
            for episode in episodes:
                with patch( 'ffmpeg.run' ) as run:
                    download_path = Chibi_temp_path()
                    stream_path = episode.download_stream( download_path )
                    self.assertIsNotNone( stream_path )
                    run.assert_called()

        for episode in episodes:
            with self.subTest(
                    "download episode without subs", episode=episode ):
                with patch( 'ffmpeg.run' ) as run:
                    download_path = Chibi_temp_path()
                    stream_path = episode.download(
                        download_path, download_subtitles=False )
                    self.assertFalse( list( download_path.ls() ) )

        for episode in episodes:
            with self.subTest(
                    "download episode with subs", episode=episode ):
                with patch( 'ffmpeg.run' ) as run:
                    download_path = Chibi_temp_path()
                    stream_path = episode.download(
                        download_path, download_subtitles=True )
                    subtitles = list( download_path.ls() )
                    self.assertEqual(
                        len( episode.subtitles ), len( subtitles ) )

        for episode in episodes:
            with self.subTest(
                    "only one subtitle by episode should have default",
                    episode=episode ):
                defaults = Counter( s.default for s in episode.subtitles  )
                self.assertEqual( defaults[ True ], 1 )


    @skip( "slow" )
    def test_should_pack_the_episode_with_the_subtitles( self ):
        folder = Chibi_temp_path()
        result = self.site.series[0].episodes[0].download( folder )
        m4a = next( folder.find( r".*.m4a" ) )
        self.assertTrue( m4a )
        subtitles = list( folder.find( r".*.ass" ) )
        self.assertGreater( len( subtitles ), 1 )
        pack = self.site.series[0].episodes[0].pack( folder )
        mkv = next( folder.find( r".*.mkv" ) )


@skip( "quiero migrar esta mierda a otro paquete" )
class Test_crunchyroll_no_dub( VCRTestCase, Test_crunchyroll ):
    def setUp( self ):
        super().setUp()
        self.site = Crunchyroll()
        self.site.append( 'https://www.crunchyroll.com/es/yuruyuri' )
        #self.site.login()

    def tearDown( self ):
        super().tearDown()


"""
class Test_crunchyroll_with_dub( VCRTestCase, Test_crunchyroll ):
    def setUp( self ):
        super().setUp()
        self.site = Crunchyroll(
            url='http://www.crunchyroll.com/es/miss-kobayashis-dragon-maid',
            user='asdf',
            password='1234',
            quality=240 )
"""
