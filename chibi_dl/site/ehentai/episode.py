import datetime
import json
import logging
import re
import shutil
import time

from chibi.atlas import Chibi_atlas_default
from bs4 import BeautifulSoup
from chibi.file import Chibi_path
from chibi.atlas import Chibi_atlas
from .others import metadata
from .regex import banned_time

from chibi_dl.site.base.site import Site
from chibi_requests import Chibi_url
#from .image import Image
from .regex import re_episode
from chibi_dl.site.base.exceptions import Max_retries_reach


logger = logging.getLogger( "chibi_dl.sites.ehentai.episode" )


class Episode( Site ):

    @property
    def id( self ):
        return self.url.path.split( '/' )[2]

    @property
    def token( self ):
        return self.url.base_name

    @classmethod
    def can_proccess( cls, url ):
        if re_episode.match( str( url ) ):
            return cls( url )

    @property
    def cover( self ):
        return self.info.cover_url

    @property
    def images( self ):
        raise NotImplementedError
        return self.info.images

    @property
    def upload_at( self ):
        return self.info.upload_at

    def parse_info( self ):
        return self.metadata

    def parse_metadata( self ):
        meta = self.get_metadata()
        meta.scan_at = datetime.datetime.utcnow()
        meta.url = self.url
        meta.tags = self._parse_tags( meta )
        return meta

    def _parse_tags( self, metadata ):
        tags = Chibi_atlas_default( default_factory=list )
        for tag in metadata.tags:
            if ':' in tag:
                tag, value = tag.split( ':' )
                if tag == 'parody':
                    tag = 'parodie'
                tags[ f"{tag}s" ].append( value )
            else:
                tags[ 'tags' ].append( tag )
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
        raise NotImplementedError()
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

    def get_metadata( self, retries=0, max_retries=5 ):
        if retries >= max_retries:
            raise Max_retries_reach( self, metadata )
        self.wait( 1.5 )
        try:
            meta = metadata.post( json={
                "method": "gdata",
                "gidlist": [
                    [ self.id, self.token ]
                ],
                "namespace": 1
            } )
            result = meta.native
        except json.decoder.JSONDecodeError:
            match = banned_time.search( meta.native.text )
            if match:
                minutes, seconds = match.groups()
                minutes, seconds = int( minutes ), int( seconds ) + 1
                logger.warning( f"banned en {metadata} por {minutes}:{seconds}" )
                time.sleep( minutes * 60 + seconds )
                return self.get_metadata(
                    retries=retries + 1, max_retries=max_retries )
        return result
