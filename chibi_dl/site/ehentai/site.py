import time
import logging

from .regex import re_main, banned_time, banned_time_2
from chibi_dl.site.base.site import Site as Site_base
from chibi_requests import Chibi_url
from chibi.metaphors import Book
from chibi.metaphors.book import End_book
from chibi.atlas import Chibi_atlas


logger = logging.getLogger( "chibi_dl.sites.ehentai" )


class Site( Site_base ):
    def _pre_to_dict( self ):
        return dict(
            url=self.url, user=self.user, password=self.password,
            lenguage=self.lenguage, quality=self.quality )


class Ehentai( Site ):
    def __init__( self, url=None, *args, book=None, **kw ):
        self.urls = []
        if url is None:
            url = Chibi_url( 'https://e-hentai.org/' )
        self.url = url
        self.enable_full_scan = False
        self.processing_order = [ self.episode_class ]

    def append( self, url ):
        result = super().append( url )
        if result:
            return result
        url = Chibi_url( url )

        if re_main.match( str( url.url ) ):
            self.enable_full_scan = True
        return result

    def __iter__( self ):
        if self.urls:
            for url in self.urls:
                time.sleep( 1 )
                yield url
        if self.enable_full_scan:
            for galerie in self.info.galeries:
                time.sleep( 1 )
                yield galerie
            for page in self.pages:
                for galerie in page.info.galeries:
                    time.sleep( 1 )
                    yield galerie

    def parse_info( self ):
        table = self.soup.find(
            'table', { 'class': 'itg gltc' } )
        rows = table.find_all( 'td', { "class": "gl3c glname" } )
        links = [
            self.episode_class( r.a.attrs[ 'href' ], parent=self )
            for r in rows ]
        return Chibi_atlas( galeries=links )

    @property
    def pages( self ):
        book = Book(
            total_elements=self.last_page, page_size=1,
            page=self.current_page,
            offset_dict={ 'page': 'page', 'page_size': 'page_size' } )
        while True:
            try:
                book.next()
                page = type( self )( self.url + book )
                yield page
            except End_book:
                break
    @property
    def current_page( self ):
        return int( self.url.params.get( "page", 1 ) )

    @property
    def last_page( self ):
        page = self.soup.find( 'table', { 'class': 'ptt' } )
        links = page.find_all( 'a' )
        max_page = 0
        for a in links:
            url = Chibi_url( a.attrs[ 'href' ] )
            number = int( url.params.get( 'page', 0 ) )
            if number > max_page:
                max_page = number
        return max_page

    @property
    def episode_class( self ):
        from .episode import Episode
        return Episode

    @classmethod
    def can_proccess( cls, url ):
        if re_main.match( str( url ) ):
            return cls( url )

    def get( self, *args, **kw ):
        response = super().get( *args, **kw )
        match = banned_time.search( response.native.text )
        if match:
            minutes, seconds = match.groups()
            minutes, seconds = int( minutes ), int( seconds ) + 1
            logger.warning( f"banned en {self.url} por 00:{minutes}:{seconds}" )
            time.sleep( minutes * 60 + seconds )
        match = banned_time_2.search( response.native.text )
        if match:
            hours, minutes = match.groups()
            hours, minutes = int( hours ), int( minutes ) + 1
            logger.warning( f"banned en {self.url} por {hours}:{minutes}:00" )
            time.sleep( hours * 60 * 60 + minutes * 60 )
        return response

    def __bool__( self ):
        return bool( self.url )
