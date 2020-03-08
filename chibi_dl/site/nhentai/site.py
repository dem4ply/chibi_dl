import logging

from .regex import re_episode, re_main
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


class Nhentai( Site ):

    def __init__( self, url=None, *args, book=None, **kw ):
        self.urls = []
        if url is None:
            url = Chibi_url( 'https://nhentai.net' )
        self.url = url
        self.enable_full_scan = False

    def append( self, url ):
        url = Chibi_url( url )

        processing_order = [ self.episode_class ]
        for proccesor in processing_order:
            result = proccesor.can_proccess( url )
            if result:
                self.urls.append( result )
                return result
        if re_main.match( str( url.url ) ):
            self.enable_full_scan = True
        return result

    def __iter__( self ):
        if self.urls:
            for url in self.urls:
                yield url
        if self.enable_full_scan:
            current_page = int( self.url.params.get( "page", 1 ) )
            last_page = self.last_page
            book = Book(
                total_elements=last_page, page_size=1, page=current_page,
                offset_dict={ 'page': 'page' } )
            for galerie in self.info.galeries:
                yield galerie
            while True:
                try:
                    book.next()
                    page = type( self )( self.url + book )
                    for galerie in page.info.galeries:
                        yield galerie
                except End_book:
                    break

    def parse_info( self ):
        galeries = self.soup.find_all( "div", { "class": "gallery" } )
        links = [
            self.episode_class( self.url + g.a.attrs[ 'href' ] )
            for g in galeries ]
        return Chibi_atlas( galeries=links )

    @property
    def last_page( self ):
        page = self.soup.find( "a", { "class": "last" } ).attrs[ 'href' ]
        return int( page.split( '=' )[1] )

    @property
    def episode_class( self ):
        from .episode import Episode
        return Episode


    @classmethod
    def can_proccess( cls, url ):
        if re_main.match( str( url ) ):
            return cls( url )
