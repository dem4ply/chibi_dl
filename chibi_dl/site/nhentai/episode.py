import datetime
import logging
import re
import shutil

from bs4 import BeautifulSoup
from chibi.file import Chibi_path
from chibi.atlas import Chibi_atlas

from chibi_dl.site.base.site import Site
from chibi_requests import Chibi_url
from .image import Image
from .regex import re_episode


logger = logging.getLogger( "chibi_dl.sites.ehentai.episode" )


class Episode( Site ):
    @classmethod
    def can_proccess( cls, url ):
        if re_episode.match( str( url ) ):
            return cls( url )

    @property
    def cover( self ):
        return self.info.cover

    @property
    def images( self ):
        return self.info.images

    @property
    def upload_at( self ):
        return self.info.upload_at

    def parse_info( self ):
        info = self.soup.find( "div", id="info" )
        tags = self._parse_tags( info )
        cover = self._parse_cover()
        images = self._parse_images()
        upload_at = datetime.datetime.fromisoformat(
            self.soup.time.attrs[ "datetime" ] )

        return Chibi_atlas(
            title=info.h1.text, tags=tags, cover=cover, images=images,
            upload_at=upload_at )

    def parse_metadata( self ):
        return Chibi_atlas(
            cover_url=self.cover,
            #images_urls=[ image.image for image in self.images ],
            images_len = len( self.images ),
            scan_at=datetime.datetime.utcnow(),
            tags=self.info.tags,
            title=self.info.title,
            upload_at=self.upload_at,
            url=self.url,
            id=self.url.base_name,
        )

    def _parse_tags( self, info ):
        tags = {}
        for section in info.find_all( "div", { "class": "tag-container" } ):
            name = section.find( text=True, recursive=False )
            name = name.strip().lower().replace( ':', '' )
            tags[ name ] = []
            for a in section.find_all( 'a' ):
                text = a.find( text=True )
                text = text.strip()
                tags[ name ].append( text )
        return tags

    def _parse_cover( self ):
        container = self.soup.find( "div", id="bigcontainer" )
        url = Chibi_url( container.img.attrs[ "data-src" ] )
        # url += self.url.session
        return url

    def _parse_images( self ):
        container = self.soup.find( "div", id="thumbnail-container" )
        return [
            Image( self.url + a.attrs[ 'href' ] )
            for a in container.find_all( "a" ) ]

    def download( self, path ):
        if path.is_a_file:
            raise NotImplementedError(
                "no se a implementado la descarga cuando path es un archivo" )
        logger.info(
            f"inicia descarga de {len(self.images)} de {self.info.title}" )

        for image in self.images:
            image.download( path )
        return path

    def compress( self, path_output, path_input, format="zip" ):
        if path_output.is_a_folder:
            path_output += self.info.title
        logger.info( f"comprimiendo con {format}" )
        logger.info( f'comprimiendo en "{path_output}"' )
        result = Chibi_path( shutil.make_archive(
            path_output, format, path_input ) )
        expected = result.replace_extensions( "cbz" )
        result.move( expected )
        return expected

    @property
    def file_name( self ):
        return "{}.{}".format( self.number, "cbz" )
