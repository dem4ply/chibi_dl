import copy
import logging
import time

import requests

from .exceptions import Max_retries_reach, Cannot_pass_cloud_flare
from chibi_requests import Chibi_url

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc


logger = logging.getLogger( "chibi_dl.sites.base.site" )


class Site:
    url = None
    default_user_agent = (
        'Mozilla/5.0 (Windows NT 6.1; WOW64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/56.0.2924.87 Safari/537.36'
    )

    def __init__( self, url=None, *args, parent=None, **kw ):
        if url is None:
            url = self.url
        if not isinstance( url, Chibi_url ):
            url = Chibi_url( url.strip() )

        self.url = url
        self.enable_full_scan = False

        self.urls = []
        self.processing_order = []
        self.parent = parent

        for k, v in kw.items():
            setattr( self, k, v )

        if self.default_user_agent:
            self.user_agent = self.default_user_agent

        self._cloud_flare_passed = False

    @property
    def domain( self ):
        parts = self.url.parts
        parts[2] = ''
        parts[3] = ''
        parts[4] = ''
        url = Chibi_url( urlunparse( parts ) )
        url.session = self.session
        return url

    def build_url( self, url=None, params=None, headers=None, **kw ):
        if url is None:
            url = self.url
        if isinstance( url, str ):
            url = Chibi_url( url )
        url.session = self.session
        if params:
            url = url + params
        if headers:
            headers = dict( **url.headers, **headers )
            url._headers = headers
        return url

    def get(
            self, *args, url=None, delay=10, retries=0, max_retries=5,
            verify=True, timeout=500, **kw ):
        url = self.build_url( url=url, **kw )
        try:
            response = url.get( verify=verify, timeout=timeout )
        except requests.ConnectionError:
            if retries > max_retries:
                logger.exception( "maximo numero de reintentos para {url}" )
                raise
            logger.warning( (
                f"no se pudo connectar con el servicor "
                f"esperando {delay} segundos en {url}" ) )
            time.sleep( delay )
            return self.get(
                *args, url=url, delay=delay, retries=retries, **kw )
        if response.status_code not in self.status_code_ok:
            if retries > max_retries:
                logger.error( "maximo numero de reintentos para {url}" )
                raise Max_retries_reach( self, url )
            if response.status_code == 429:
                logger.warning( (
                    f"status code :{response.status_code} url: {url} "
                    f"se reintentara en 300" ) )
                time.sleep( 300 )
            else:
                logger.warning( (
                    f"status code :{response.status_code} url: {url} "
                    f"se reintentara en {delay}" ) )
                time.sleep( delay )
            return self.get(
                *args, url=url, delay=delay, retries=retries + 1, **kw )
        return response

    @property
    def status_code_ok( self ):
        return [ 200 ]

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

    def append( self, url ):
        url = Chibi_url( url )

        for proccesor in self.processing_order:
            result = proccesor.can_proccess( url )
            if result:
                self.urls.append( result )
                return result

    def __iter__( self ):
        for url in self.urls:
            yield url

    @classmethod
    def from_info( cls, url, data ):
        raise NotImplementedError( "no implementada la funcion from_info" )

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
        if hasattr( self, '_session' ) and not self.parent:
            logger.info( f"cerrando session de '{self!r}'" )
            self.session.close()
        if hasattr( self, '_browser' ):
            logger.info( "cerrando el navegador" )
            self.browser.quit()

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

    def wait( self, seconds=1 ):
        time.sleep( seconds )

    def login( self ):
        pass

    @property
    def firefox( self ):
        return self.browser
        """
        if hasattr( self, 'parent' ) and self.parent:
            return self.parent.firefox
        try:
            return self._firefox
        except AttributeError:
            logger.info( "abriendo firefox" )
            options = self.build_firefox_options()
            self._firefox = webdriver.Firefox( options=options )
            return self._firefox
        """

    @property
    def browser( self ):
        if self.parent:
            return self.parent.browser
        try:
            return self._browser
        except AttributeError:
            options = Options()
            desire_capabilities = DesiredCapabilities.CHROME
            desire_capabilities[ 'pageLoadStrategy' ] = 'eager'
            logger.info( "iniciando chrome" )
            a = uc.Chrome( desired_capabilities=desire_capabilities )
            self._browser = a
            return self._browser

    @property
    def _has_browser_init( self ):
        has_browser = hasattr( self, '_browser' )
        if not has_browser and self.parent:
            return self.parent._has_browser_init
        return has_browser

    def build_firefox_options( self ):
        options = Options()
        options.headless = True
        return options

    @property
    def cookies( self ):
        if self.parent:
            return self.parent.cookies
        try:
            return self._cookies
        except AttributeError:
            return None

    @cookies.setter
    def cookies( self, value ):
        if self.parent:
            self.parent.cookies = value
        else:
            self._cookies = {
                cookie[ 'name' ]: cookie[ 'value' ] for cookie in value }
            self.session.cookies.clear()
            for k, v in self._cookies.items():
                self.session.cookies.set( k, v )

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

    @property
    def cloud_flare_passed( self ):
        return (
            self._cloud_flare_passed
            or ( self.parent and self.parent.cloud_flare_passed ) )

    @cloud_flare_passed.setter
    def cloud_flare_passed( self, value ):
        self._cloud_flare_passed = value
        if self.parent:
            self.parent.cloud_flare_passed = value

    def cross_cloud_flare( self, delay=2 ):
        if not self.cloud_flare_passed:
            logger.info( f"obteniendo {self.url} usando el navegador" )
            self.browser.get( self.url )
            logger.info( f"esperando {delay} segundos a que pase cloud flare" )
            time.sleep( delay )

            self.cookies = self.firefox.get_cookies()
            self.user_agent = self.firefox.execute_script(
                "return navigator.userAgent;" )

            if self.get( url=self.url ).ok:
                logger.info(
                    "se puede usar requests con las cookies "
                    "del navegador para pasar cloudflare" )
                self.cloud_flare_passed = True
            else:
                raise Cannot_pass_cloud_flare

    @property
    def is_browser_open( self ):
        parent = self.parent
        while parent:
            browser = hasattr( parent, '_browser' )
            if browser:
                return True
            parent = parent.parent
        return hasattr( self, '_browser' )
