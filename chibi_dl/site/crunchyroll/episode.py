import logging

import ffmpeg
import m3u8
from chibi.atlas import loads, Chibi_atlas
from chibi.file import Chibi_path
from chibi_dl.config import configuration
from pymkv import MKVFile, MKVTrack

from .exceptions import Cannot_find_subtitles, Episode_not_have_media
from .site import Site
from .subtitles import Subtitle


logger = logging.getLogger( "chibi_dl.sites.crunchyroll.episode" )


class Episode( Site ):
    def parse_info( self ):
        result = Chibi_atlas()
        result.media_metadata = self._parse_media_metadata()
        result.number = self._parse_episode_number()
        result.serie_title = result.media_metadata.series_title
        result.title = result.media_metadata.episode_title
        result.subtitles = self._parse_subtitles( result.title )
        result.playlist = self._parse_playlist()
        return result

    def _parse_media_metadata( self ):
        soup = self.soup
        return soup.config_Config.default_preload.media_metadata

    def _parse_subtitles( self, title ):
        subtitles = self.soup.config_Config.default_preload.subtitles.subtitle
        if isinstance( subtitles, dict ):
            subtitles = [ subtitles ]
        return [
            Subtitle.from_info(
                self.url + s.link, name=title, parent=self, **s )
            for s in subtitles ]

    def _parse_episode_number( self ):
        media = self.soup.config_Config.default_preload.media_metadata
        number = media.episode_number
        if number:
            try:
                return int( number )
            except ValueError:
                try:
                    return float( number )
                except ValueError:
                    return number

    @property
    def subtitles( self ):
        return self.info.subtitles

    @property
    def media_id( self ):
        result = self.url.url.base_name.rsplit( '-', 1 )[-1]
        return result

    @property
    def url_data( self ):
        video_quality = configuration.chibi_dl.crunchyroll.video_quality
        video_format = configuration.chibi_dl.crunchyroll.video_format

        url_data = self.url + "http://www.crunchyroll.com/xml/?req=RpcApiVideoPlayer_GetStandardConfig"

        url_data = url_data + dict(
            media_id=self.media_id, current_page=self.url,
            video_quality=video_quality, video_format=video_format, )

        return url_data

    def load( self ):
        url = self.url_data
        response = self.get( url=url )
        self._response = response

    @property
    def stream( self ):
        resolution = configuration.chibi_dl.crunchyroll.resolution
        stream_with_my_resolution = filter(
            lambda x: x.stream_info.resolution == resolution,
            self.info.playlist )

        try:
            first_stream = next( stream_with_my_resolution )
        except StopIteration:
            resolutions = [ p.stream_info.resolution for p in self.info.playlist ]
            logger.exception(
                "no se encontro la resolucion {} resoluciones "
                "encontradas {}".format( resolution, resolutions ) )
            raise
        return first_stream

    def download_stream( self, path ):
        if path.is_a_folder:
            path += self.file_name
        stream = ffmpeg.input( self.stream.uri )
        stream = ffmpeg.output(
            stream, path, loglevel="quiet", codec="copy", )
        logger.info(
            f'inicia la descarga del video "{self.name}" en "{path}"'
        )
        ffmpeg.run( stream )
        return path

    def __str__( self ):
        return self.name

    def __repr__( self ):
        return f"Episode( {self} )"

    def _parse_playlist( self ):
        stream_info = self.soup.config_Config.default_preload.stream_info
        if 'error' in stream_info:
            raise Episode_not_have_media( stream_info )
        straming_list = m3u8.load( stream_info.file )
        return straming_list.playlists

    def download( self, path, download_subtitles=True ):
        logger.info( "inicio de la descarga de subtitulos"  )
        if download_subtitles:
            for subtitles in self.subtitles:
                subtitles.download( path )
        return self.download_stream( path )

    def pack( self, path ):
        mkv = MKVFile()
        mkv.add_track( MKVTrack( path + self.file_name, track_id=0 ) )
        mkv.add_track( MKVTrack( path + self.file_name, track_id=1 ) )
        for subtitle in self.subtitles:
            mkv.add_track( subtitle.to_mkv_track( path ) )
        output = path + self.file_name_mkv
        logger.info( "inicia el empaquetado a '{}'".format( self.file_name ) )
        mkv.mux( output, silent=False )
        return output

    @property
    def serie_title( self ):
        title = self.info.media_metadata.series_title
        title = title.replace( "/", " " )
        return title



    @property
    def name( self ):
        title = self.serie_title.replace( 'Season ', 'S' )
        if self.info.number:
            return f"{title} - {self.info.number}"
        else:
            return "{title}"

    @property
    def file_name( self ):
        ext = 'm4a'
        resolution = configuration.chibi_dl.crunchyroll.resolution
        resolution = "[{}x{}]".format( *resolution )
        result = f"{self.name} {resolution}.{ext}"
        return Chibi_path( result ).made_safe()

    @property
    def file_name_mkv( self ):
        ext = 'mkv'
        resolution = configuration.chibi_dl.crunchyroll.resolution
        resolution = "[{}x{}]".format( *resolution )
        result = f"{self.name} {resolution}.{ext}"
        return Chibi_path( result ).made_safe()
