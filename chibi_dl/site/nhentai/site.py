import logging

from .regex import re_episode, re_main
from chibi_dl.site.base.site import Site as Site_base
from chibi_requests import Chibi_url
from chibi.metaphors import Book
from chibi.metaphors.book import End_book
from chibi.atlas import Chibi_atlas


logger = logging.getLogger( "chibi_dl.sites.nhentai" )


class Site( Site_base ):
    pass


class Nhentai( Site ):
    def __init__( self, url=None, *args, book=None, **kw ):
        if url is None:
            url = Chibi_url( 'https://nhentai.net' )
        super().__init__( url, *args, book=book, **kw )
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
                yield url
        if self.enable_full_scan:
            for galerie in self.info.galeries:
                yield galerie
            for page in self.pages:
                for galerie in page.info.galeries:
                    yield galerie

    @property
    def pages( self ):
        book = Book(
            total_elements=self.last_page, page_size=1,
            page=self.current_page, offset_dict={ 'page': 'page' } )
        for page in book:
            yield type( self )( self.url + page, parent=self )

    def parse_info( self ):
        galeries = self.soup.find_all( "div", { "class": "gallery" } )
        links = [
            self.episode_class(
                self.url + g.a.attrs[ 'href' ], parent=self )
            for g in galeries ]
        return Chibi_atlas( galeries=links )

    @property
    def current_page( self ):
        return int( self.url.params.get( "page", 1 ) )

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

    def __bool__( self ):
        return bool( self.url )

    def i_can_proccess_this( self, url ):
        regex = ( re_episode, re_main )
        return any( ( r.match( url ) for r in regex ) )
