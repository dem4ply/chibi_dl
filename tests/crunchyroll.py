import time
from unittest import TestCase, skip
from chibi_dl.site.crunchyroll import Crunchyroll
from chibi_dl.site.crunchyroll.exceptions import Episode_not_have_media
from vcr_unittest import VCRTestCase
from chibi.file.temp import Chibi_temp_path

#class Test_crunchyroll( TestCase ):
class Test_crunchyroll:
    def test_should_get_the_lenguage_form_the_url( self ):
        self.assertEqual( 'es', self.site.lenguage )

    def test_should_have_a_show( self ):
        self.assertTrue( self.site.shows )
        self.assertEqual( 1, len( self.site.shows ) )

    def test_should_have_episodes( self ):
        self.assertTrue( self.site.shows[0].episodes )
        self.assertGreater( len( self.site.shows[0].episodes ), 1 )

    @skip( "slow" )
    def test_should_get_all_the_subtitles_of_the_show( self ):
        try:
            for show in self.site.shows:
                for episode in show.episodes:
                    for subtitle in episode.subtitles:
                        self.assertTrue( subtitle.data )
        except Exception as e:
            import pdb
            pdb.post_mortem( e.__traceback__ )
            raise

    @skip( "slow" )
    def test_should_get_the_steaming_file( self ):
        episodes_with_media = 0
        try:
            for show in self.site.shows:
                for episode in show.episodes:
                    try:
                        self.assertTrue( episode.stream.uri )
                        episodes_with_media += 1
                    except Episode_not_have_media:
                        pass
        except Exception as e:
            import pdb
            pdb.post_mortem( e.__traceback__ )
            raise
        if episodes_with_media < 1:
            self.fail( "no se encontraron stream uri" )

    @skip( "slow" )
    def test_should_download_episodes( self ):
        folder = Chibi_temp_path()
        result = self.site.shows[0].episodes[0].download( folder )
        m4a = next( folder.find( r".*.m4a" ) )
        self.assertTrue( m4a )
        subtitles = list( folder.find( r".*.ass" ) )
        self.assertGreater( len( subtitles ), 1 )

    @skip( "slow" )
    def test_should_pack_the_episode_with_the_subtitles( self ):
        folder = Chibi_temp_path()
        result = self.site.shows[0].episodes[0].download( folder )
        m4a = next( folder.find( r".*.m4a" ) )
        self.assertTrue( m4a )
        subtitles = list( folder.find( r".*.ass" ) )
        self.assertGreater( len( subtitles ), 1 )
        pack = self.site.shows[0].episodes[0].pack( folder )
        mkv = next( folder.find( r".*.mkv" ) )

    @skip( "slow" )
    def test_should_download_episode_withtous_subtitles( self ):
        folder = Chibi_temp_path()
        result = self.site.shows[0].episodes[0].download(
            folder, download_subtitles=False )
        m4a = next( folder.find( r".*.m4a" ) )
        self.assertTrue( m4a )
        subtitles = list( folder.find( r".*.ass" ) )
        self.assertFalse( subtitles )

    @skip( "slow" )
    def test_the_subtitles_should_have_the_episode_like_parent( self ):
        folder = Chibi_temp_path()
        for episode in self.site.shows[0].episodes:
            for subtitle in episode.subtitles:
                self.assertEqual( subtitle.parent, episode )

    @skip( "slow" )
    def test_should_create_the_expected_subtitles_in_the_folder( self ):
        folder = Chibi_temp_path()
        result = self.site.shows[0].episodes[0].subtitles[0].download( folder )
        files = list( folder.ls() )
        self.assertEqual( 1, len( files ) )

    @skip( "slow" )
    def test_should_download_all_the_show( self ):
        folder = Chibi_temp_path()
        self.site.shows[0].download( folder )
        self.assertTrue( list( folder.ls() ) )


class Test_crunchyroll_no_dub( VCRTestCase, Test_crunchyroll ):
    def setUp( self ):
        super().setUp()
        self.site = Crunchyroll(
            user='asdf',
            password='1234',
            quality=240 )

        self.site.append( 'https://www.crunchyroll.com/es/yuruyuri' )
        self.site.login()


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
