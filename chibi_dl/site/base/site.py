import logging
import time

import cfscrape
import requests

from .exceptions import Max_retries_reach
from chibi_requests import Chibi_url


logger = logging.getLogger( "chibi_dl.sites.base.site" )


class Site:
    def __init__( self, url, parent=None, *args, **kw ):
        self.url = Chibi_url( url.strip() )
        self.enable_full_scan = False
        self.parent = parent

        for k, v in kw.items():
            setattr( self, k, v )

    def get( self, *args, delay=10, retries=0, max_retries=5, **kw ):
        try:
            response = self.url.get()
        except requests.ConnectionError:
            if retries > max_retries:
                raise
            time.sleep( delay )
            logger.warning( (
                f"no se pudo connectar con el servicor esperando {delay} segundos "
                f"en {self.url}" ) )
            return self.get( *args, delay=delay, retries=retries, **kw )
        if response.status_code not in [ 200 ]:
            return self.get( *args, delay=delay, retries=retries + 1, **kw )
        return response

    @property
    def info( self ):
        try:
            return self._info
        except AttributeError:
            self._info = self.parse_info()
            return self._info

    @property
    def metadata( self ):
        try:
            return self._metadata
        except AttributeError:
            self._metadata = self.parse_metadata()
            return self._metadata

    @property
    def soup( self ):
        try:
            return self._response.native
        except AttributeError:
            self.load()
            return self._response.native

    def load( self ):
        response = self.get()
        self._response = response

    def parse_info( self ):
        raise NotImplementedError(
            "no implementada la funcion de parseo de info" )

    def parse_metadata( self ):
        raise NotImplementedError(
            "no implementada la funcion de parseo de metadata" )

    def download( self, path ):
        raise NotImplementedError(
            "no implementada la funcion de download" )

    def compress( self, path_output, path_input, format ):
        raise NotImplementedError(
            "no implementada la funcion de compress" )

    def _pre_to_dict( self ):
        return dict( url=self.url, )

    @classmethod
    def from_site( cls, site, **kw ):
        site_dict = site._pre_to_dict()
        site_dict.update( kw )
        return cls( **site_dict, parent=site )

    def __del__( self ):
        return None
        if self.parent is None:
            self.session.close()

    @property
    def session( self ):
        try:
            return self._session
        except AttributeError:
            if self.parent is None:
                self.build_session()
            else:
                self._session = self.parent.session
            return self._session

    @property
    def user_agent( self ):
        return self.session.headers[ 'User-Agent' ]

    @user_agent.setter
    def user_agent( self, value ):
        self.session.headers[ 'User-Agent' ] = value

    def build_session( self ):
        self._session = requests.session()
        self._session = cfscrape.create_scraper( self._session )
        self._session.headers.update( {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/56.0.2924.87 Safari/537.36',
        } )

    """
    def get(
            self, *args, delay=16, retries=0, max_retries=5,
            ignore_status_code=None, **kw ):
        try:
            response = self.session.get( *args, **kw )
        except requests.ConnectionError:
            time.sleep( delay )
            logger.warning( (
                "no se pudo connectar con el servicor esperando {} segundos "
                "en {}" ).format( delay, args[0], ) )
            return self.get(
                *args, delay=delay ** 2, retries=retries + 1, **kw )
        if ignore_status_code and response.status_code in ignore_status_code:
            logger.warning( (
                "se recibio {} se ignora" ).format( response.status_code, ) )
            return response
        if response.status_code not in [ 200 ]:
            if retries >= max_retries:
                raise Max_retries_reach
            logger.warning( (
                "se recibio {} ( {} ) esperando {} segundos "
                "en {}" ).format(
                    response.status_code,
                    requests.status_codes._codes[ response.status_code ][0],
                    delay, args[0], ) )
            time.sleep( delay )
            return self.get(
                *args, delay=delay ** 2, retries=retries + 1, **kw )
        return response
    """
