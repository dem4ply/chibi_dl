import logging
import re
import shutil

from bs4 import BeautifulSoup
from chibi.file import Chibi_path
from chibi.atlas import Chibi_atlas

from chibi_dl.site.base.site import Site
from chibi_requests import Chibi_url
from .regex import re_image


logger = logging.getLogger( "chibi_dl.sites.ehentai.episode" )


class Image( Site ):
    @classmethod
    def can_proccess( cls, url ):
        if re_image.match( str( url ) ):
            return cls( url )

    def parse_info( self ):
        image = Chibi_url( self.soup.find(
            "section", id="image-container" ).img.get( 'src' ) )
        return Chibi_atlas( image=image, )

    @property
    def image( self ):
        return self.info.image

    def download( self, path ):
        if path.is_a_folder:
            path += self.image.base_name
        logger.info( f"descargnado {path.base_name} en {path.dir_name}" )
        self.image.download( path )
        return path
