import logging

from .exceptions import Cannot_login
from .regex import re_show, re_video, re_lenguage, re_csrf_token
from chibi_dl.site.base.site import Site as Site_base
from chibi_requests import Chibi_url


logger = logging.getLogger( "chibi_dl.sites.crunchyroll" )


class Site( Site_base ):
    @property
    def token( self ):
        if self.parent:
            return self.parent.token
        return self._token

    @token.setter
    def token( self, value ):
        if self.parent:
            self.parent._token = value
        self._token = value

    def _pre_to_dict( self ):
        return dict(
            url=self.url, user=self.user, password=self.password,
            lenguage=self.lenguage, quality=self.quality )


class Crunchyroll( Site ):
    def __init__( self, *args, **kw ):
        super().__init__( '', *args, **kw )
        from .serie import Serie
        self.processing_order = [ Serie ]

    def append( self, url ):
        from .serie import Serie
        lenguage = re_lenguage.search( url )
        url = Chibi_url( url )
        if not lenguage:
            logger.error(
                "no se encontro el lenguaje en la url {}".format( url ) )
        lenguage = lenguage.group( 1 )
        self.lenguage = lenguage

        if re_show.match( url ):
            self.urls.append( Serie(
                url, user=self.user, password=self.password, parent=self,
                lenguage=lenguage, quality=self.quality ) )
            return True
        elif re_video.match( self.url ):
            raise NotImplementedError
        else:
            logger.error( "no se pudo identificar el tipo de la url" )
        return False

    def build_firefox_options( self ):
        options = super().build_firefox_options()
        options.headless = False
        return options

    def login( self ):
        login_url = Chibi_url( "https://www.crunchyroll.com/{country}/login" )
        headers = {
            'Referer': login_url,
        }
        login_url = login_url.format( country=self.lenguage, headers=headers )
        self.firefox.get( login_url )
        input( "preciona enter cuando termines de logearte" )


        self.cookies = self.firefox.get_cookies()
        self.user_agent = self.firefox.execute_script(
            "return navigator.userAgent;" )

        login_url.session = self.session
        login_response = login_url.get()
        logger.info( "intentanto logearse" )

        if login_response.ok:
            csrf_token =  login_response.native.find(
                'input', id='login_form__token' ).attrs[ 'value' ]
            """
            initial_cookies = self.session.cookies
            csrf_token = re_csrf_token.search(
                initial_page_fetch.text ).group( 1 )
            """

            payload = {
                'login_form[name]': self.user,
                'login_form[password]': self.password,
                'login_form[redirect_url]': '/',
                'login_form[_token]': csrf_token,
            }

            login_post_response = login_url.post( data=payload )
            logger.info( "termino de logerase" )
            """
            response = self.get(
                url=self.url, headers=headers,
                cookies=initial_cookies )
            """
            self.session.headers.update( {
                'Upgrade-Insecure-Requests': '1',
                'Accept-Encoding': 'gzip, deflate'
            } )
        else:
            raise Cannot_login(
                "no se pudo conectar a la pagina de loging",
                status_code=login_response.status_code )

    def i_can_proccess_this( self, url ):
        return re_show.match( url )
