import logging

from bs4 import BeautifulSoup
from chibi.file.temp import Chibi_temp_path
from chibi.atlas import Chibi_atlas

from .episode import Episode
from .regex import re_episodes
from .regex import re_show, re_video, re_lenguage, re_csrf_token
from .site import Site
from chibi_dl.site.crunchyroll.exceptions import Episode_not_have_media
from chibi.atlas import Chibi_atlas


logger = logging.getLogger( "chibi_dl.sites.crunchyroll.show" )


class Serie( Site ):

    @classmethod
    def can_proccess( cls, url ):
        if re_show.match( str( url ) ):
            return cls( url )


    def parse_info( self ):
        result = Chibi_atlas()
        result.title = self.soup.select( "h1.ellipsis" )[0].text.strip()
        description = self.soup.find( "p", { "class": "description" } )
        result.description = description.find(
            "span", { "class": "more" } ).text.strip()

        seasons = self.soup.find( "ul", { "class": "list-of-seasons cf" } )
        result.seasons = []
        for season in seasons.find_all( "li", recursive=False ):
            _season = Chibi_atlas()
            result.seasons.append( _season )
            _season.name = season.a.text.strip()
            _season.episodes = []
            episodes = season.find_all( "a", { "class": "episode" } )
            for episode in episodes:
                e = Episode( url = self.url + episode.attrs[ "href" ] )
                _season.episodes.append( e )
        return result

    def __iter__( self ):
        for season in self.info.seasons:
            for episode in season.episodes:
                yield episode




    def download( self, path ):
        logger.info(
            'iniciando descarga de la serie "{}" de "{}"'.format(
                self.title, self.url ) )
        path += self.title
        path = path.made_safe()
        path.mkdir()
        for episode in self.episodes:
            episode_path = path + episode.file_name_mkv
            if ( episode_path.exists ):
                logger.info( (
                    "ignorando el episodio {} se encontro "
                    "en el destino" ).format( episode.name ) )
                continue
            temp_folder = Chibi_temp_path()
            try:
                episode.download( temp_folder )
            except Episode_not_have_media:
                logger.error( (
                    "el episodio {} no esta disponible posiblemente el "
                    "login no esta correcto" ).format(
                        episode.name ) )
                continue
            mkv = episode.pack( temp_folder )
            mkv.move( path )

    @property
    def metadata( self ):
        try:
            raise NotImplementedError
            return self._metadata
        except AttributeError:
            self._metadata = Chibi_atlas()

    @property
    def title( self ):
        try:
            return self._title
        except AttributeError:
            self.load_episodes()
            return self._title

    @property
    def episodes( self ):
        try:
            return self._episodes
        except AttributeError:
            self.load_episodes()
            return self._episodes

    def load_episodes( self ):
        page = self.get( self.url, )
        soup = BeautifulSoup( page.content, 'html.parser' )
        self._title = soup.select( "h1.ellipsis" )[0].text.strip()

        self._episodes = []
        episodes_links = re_episodes.findall( page.text )
        for episode_link, episode_type in episodes_links:
            episode_link = episode_link.rsplit( '/', 1 )[1]
            episode_url = "{url}/{episode}".format(
                url=self.url, episode=episode_link )
            if episode_link:
                self._episodes.append( Episode.from_site(
                    self, url=episode_url ) )
