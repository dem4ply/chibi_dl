from chibi.config import configuration, Configuration


class Crunchyroll( Configuration ):
    @property
    def video_quality( self ):
        return self[ 'video_quality' ]

    @video_quality.setter
    def video_quality( self, value ):
        if value == 1080:
            value = 80
        elif value == 720:
            value = 62
        elif value == 480:
            value = 61
        elif value == 360:
            value = 60
        elif value == 240:
            value = 60
        else:
            raise NotImplementedError
        self[ 'video_quality' ] = value

    @property
    def resolution( self ):
        return self[ 'resolution' ]

    @resolution.setter
    def resolution( self, value ):
        if value == 1080:
            value = ( 1920, 1080 )
        elif value == 720:
            value = ( 1280, 720 )
        elif value == 480:
            value = ( 848, 480 )
        elif value == 360:
            value = ( 640, 360 )
        elif value == 240:
            value = ( 428, 240 )
        else:
            raise NotImplementedError
        self[ 'resolution' ] = value


configuration.chibi_dl.crunchyroll = Crunchyroll()
configuration.chibi_dl.crunchyroll.resolution = 240
configuration.chibi_dl.crunchyroll.video_format = 108
