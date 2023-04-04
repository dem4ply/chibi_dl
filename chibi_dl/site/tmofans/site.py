import logging
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc

from .exceptions import Cannot_pass_cloud_flare, Cannot_login
from .regex import re_show, re_follow, re_pending, re_read
from chibi_dl.site.base.site import Site as Site_base


logger = logging.getLogger( "chibi_dl.sites.tmo_fans" )


class Site( Site_base ):
    def __init__( self, *args, **kw ):
        self._cloud_flare_passed = False
        super().__init__( *args, **kw )

    def build_session( self ):
        self._session = requests.session()

    @property
    def cloud_flare_passed( self ):
        return (
            self._cloud_flare_passed
            or ( self.parent and self.parent.cloud_flared_passed ) )

    @cloud_flare_passed.setter
    def cloud_flare_passed( self, value ):
        self._cloud_flare_passed = value
        if self.parent:
            self.cloud_flare_passed = value

    def cross_cloud_flare( self ):
        if not self.cloud_flare_passed:
            logger.info( f"obteniendo {self.url} usando el navegador" )
            self.firefox.get( self.url )
            logger.info( "esperando 10 segundos a que pase cloud flare" )
            time.sleep( 10 )
            self.cookies = self.firefox.get_cookies()
            self.user_agent = self.firefox.execute_script(
                "return navigator.userAgent;" )


            if self.get( url=self.url ).ok:
                logger.info( "se pueden descargar las imagenes de TMOFans" )
                self.cloud_flare_passed = True
            else:
                raise Cannot_pass_cloud_flare

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
            self._cookies = value
            self.session.cookies.clear()
            for cookie in value:
                self.session.cookies.set( cookie[ 'name' ], cookie[ 'value' ] )

    @property
    def firefox( self ):
        return super().browser
        if self.parent:
            return self.parent.firefox
        try:
            return self._firefox
        except AttributeError:
            options = Options()

            """
            profile = webdriver.FirefoxProfile()
            profile.set_preference( "dom.webdriver.enabled", False )
            profile.set_preference( 'useAutomationExtension', False )
            profile.set_preference(
                "general.useragent.override",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/83.0.4103.61 Safari/537.36" )
            profile.update_preferences()
            desired = DesiredCapabilities.FIREFOX
            """


            """
            #options.headless = True
            logger.info( "abriendo firefox" )
            #self._firefox = webdriver.Firefox( options=options )
            self._firefox = webdriver.Firefox(
                firefox_profile=profile,
                desired_capabilities=desired
            )
            logger.info( "abrieno chrome" )
            self._firefox.execute_script(
                "Object.defineProperty(navigator, 'webdriver',"
                "{get: () => undefined})" )
            navigator_webdriver = self._firefox.execute_script(
                "return navigator.webdriver;" )
            logger.info( f"firefox.navigator.webdriver: {navigator_webdriver}" )
            """
            desire_capabilities = DesiredCapabilities.CHROME
            desire_capabilities[ 'pageLoadStrategy' ] = 'eager'
            logger.info( "iniciando chrome" )
            a = uc.Chrome( desired_capabilities=desire_capabilities );
            self._firefox = a
            return self._firefox

    def __del__( self ):
        if self.parent is None:
            try:
                self._firefox.quit()
                logger.info( "cerrando firefox" )
            except AttributeError:
                pass
        super().__del__()


class TMO_fans( Site ):
    def __init__( self, *args, user=None, password=None, **kw ):
        super().__init__( 'https://tmofans.com/login', *args, **kw )
        self.series = []
        self.user = user
        self.password = password
        self._login_ok = False

    def append( self, url ):
        from .serie import Serie
        self.cross_cloud_flare()
        if re_show.match( url ):
            self.series.append( Serie( url, parent=self ) )
        elif re_follow.match( url ):
            self.login()
            for l in self.get_all_follow():
                self.append( l )
        elif re_pending.match( url ):
            self.login()
            for l in self.get_all_pending():
                self.append( l )
        elif re_read.match( url ):
            self.login()
            for l in self.get_all_read():
                self.append( l )
        else:
            logger.error(
                "la url {} no se pudo identificar como serie".format( url ) )

    def login( self ):
        if self._login_ok:
            return
        if not self.cloud_flare_passed:
            self.cross_cloud_flare()

        email = self.firefox.find_element( By.ID, "email" )
        password = self.firefox.find_element( By.ID, "password" )
        submit = self.firefox.find_element(
            By.XPATH,
            "/html/body/div[1]/main/div/div/div/div[1]/form/div[4]"
            "/div[1]/button" )

        email.send_keys( self.user )
        password.send_keys( self.password )

        submit.click()
        logger.info( "esperando 10 segundos a que termine el login" )
        time.sleep( 10 )
        if self.firefox.current_url == self.url:
            raise Cannot_login
        else:
            self._login_ok = True
            self.cookies = self.firefox.get_cookies()
            self.user_agent = self.firefox.execute_script(
                "return navigator.userAgent;" )

        """
        page = self.get( self.url )
        soup = BeautifulSoup( page.content, 'html.parser' )
        form = soup.find( "form", { "class": "form-horizontal" } )
        token = form.find( "input", dict( name="_token" ) )[ "value" ]

        payload = dict(
            email=self.user, password=self.password, remember="on",
            _token=token )

        response = self.session.post(
            self.url, data=payload, headers={
                "Referer": str( self.url ),
                "Content-type": "application/x-www-form-urlencoded" } )

        if response.ok and response.url == self.url:
            raise Cannot_login
        else:
            self._login_ok = True
        """

    def get_all_follow( self ):
        page_number = 0
        url = "https://tmofans.com/profile/follow"
        while( True ):
            page_number += 1
            page = self.get( url=url, params={ "page": page_number } )
            soup = BeautifulSoup( page.content, 'html.parser' )

            links = self.get_manga_links( soup )
            if not links:
                return
            for l in links:
                yield l

    def get_all_pending( self ):
        page_number = 0
        url = "https://tmofans.com/profile/pending"
        while( True ):
            page_number += 1
            page = self.get( url=url, params={ "page": page_number } )
            soup = BeautifulSoup( page.content, 'html.parser' )

            links = self.get_manga_links( soup )
            if not links:
                return
            for l in links:
                yield l

    def get_all_read( self ):
        page_number = 0
        url = "https://tmofans.com/profile/read"
        while( True ):
            page_number += 1
            page = self.get( url=url, params={ "page": page_number } )
            soup = BeautifulSoup( page.content, 'html.parser' )

            links = self.get_manga_links( soup )
            if not links:
                return
            for l in links:
                yield l

    def get_manga_links( self, soup ):
        result = []
        for a in soup.find_all( "a" ):
            if "library/" in a[ "href" ]:
                result.append( a[ "href" ].strip() )
        return result

    def i_can_proccess_this( self, url ):
        regex = ( re_show, re_pending, re_read, re_follow )
        return any( ( r.match( url ) for r in regex ) )
