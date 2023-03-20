import base64
import logging
import zlib

import pycountry
from chibi.atlas import loads, Chibi_atlas
from chibi.atlas import loads
from chibi.file import Chibi_path
from chibi.parser import to_bool
from pymkv import MKVTrack

from .external.aes import aes_cbc_decrypt
from .external.utils import obfuscate_key, bytes_to_intlist, intlist_to_bytes
from .site import Site


logger = logging.getLogger( "chibi_dl.sites.crunchyroll.subtitle" )


class Subtitle( Site ):
    @classmethod
    def from_info( cls, url, parent=None, **data ):
        data = Chibi_atlas( data )
        result = cls( url, parent=parent )
        result.info.title = data.title
        result.info.name = data.name
        result.info.id = data.id
        result.info.default = data.default
        return result

    def parse_info( self ):
        data = self.soup.subtitle
        return data

    @property
    def subtitle_xml( self ):
        try:
            return self._subtitle_xml
        except:
            data = self.soup.subtitle
            data = loads( self.decrypt_subtitles(
                data.data, data.iv, data.id ) )
            self._subtitle_xml = data.subtitle_script
            return self._subtitle_xml

    def download( self, path ):
        if path.is_a_folder:
            path += self.file_name
        f = path.open()
        f.write( self.ass )
        logger.info( f'write subtitulo "{path}"' )
        return path

    @property
    def default( self ):
        return to_bool( self.info.default )

    @property
    def lang( self ):
        return "{}-{}".format(
            self.subtitle_xml.lang_code[:2], self.subtitle_xml.lang_code[-2:] )

    @property
    def lang_ISO_639_2( self ):
        try:
            return pycountry.languages.get(
                alpha_2=self.lang[:2] ).bibliographic
        except AttributeError:
            return pycountry.languages.get( alpha_2=self.lang[:2] ).alpha_3

    @property
    def name( self ):
        return f"{self.info.name}.{self.lang}"

    @property
    def file_name( self ):
        ext = 'ass'
        result = Chibi_path( "{name}.{ext}".format( name=self.name, ext=ext ) )
        result = result.made_safe()
        return result

    def __str__( self ):
        return self.name

    def __repr__( self ):
        return f"Subtitle( {self} )"

    def to_mkv_track( self, path ):
        track = MKVTrack(
            path + self.file_name, language=self.lang_ISO_639_2,
            default_track=self.default, track_name=self.data.title )
        return track

    @property
    def ass( self ):
        data = self.subtitle_xml
        output = ''

        def ass_bool(strvalue):
            assvalue = '0'
            if strvalue == '1':
                assvalue = '-1'
            return assvalue

        output = '[Script Info]\n'
        output += f'Title: {data.title}\n'
        output += 'ScriptType: v4.00+\n'
        output += f'WrapStyle: {data.wrap_style}\n'
        output += f'PlayResX: {data.play_res_x}\n'
        output += f'PlayResY: {data.play_res_y}\n'
        output += "[V4+ Styles]\n"
        output += (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour,"
            " OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,"
            " ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow,"
            " Alignment, MarginL, MarginR, MarginV, Encoding" )
        if not isinstance( data.styles.style, list ):
            data.styles.style = [ data.styles.style ]
        for style in data.styles.style:
            output += 'Style: ' + style['name']
            output += ',' + style['font_name']
            output += ',' + style['font_size']
            output += ',' + style['primary_colour']
            output += ',' + style['secondary_colour']
            output += ',' + style['outline_colour']
            output += ',' + style['back_colour']
            output += ',' + ass_bool(style['bold'])
            output += ',' + ass_bool(style['italic'])
            output += ',' + ass_bool(style['underline'])
            output += ',' + ass_bool(style['strikeout'])
            output += ',' + style['scale_x']
            output += ',' + style['scale_y']
            output += ',' + style['spacing']
            output += ',' + style['angle']
            output += ',' + style['border_style']
            output += ',' + style['outline']
            output += ',' + style['shadow']
            output += ',' + style['alignment']
            output += ',' + style['margin_l']
            output += ',' + style['margin_r']
            output += ',' + style['margin_v']
            output += ',' + style['encoding']
            output += '\n'

        output += (
            "\n[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, "
            "MarginR, MarginV, Effect, Text\n"
        )

        if not isinstance( data.events.event, list ):
            data.events.event = [ data.events.event ]
        for event in data.events.event:
            output += 'Dialogue: 0'
            output += ',' + event['start']
            output += ',' + event['end']
            output += ',' + event['style']
            output += ',' + event['name']
            output += ',' + event['margin_l']
            output += ',' + event['margin_r']
            output += ',' + event['margin_v']
            output += ',' + event['effect']
            output += ',' + event['text']
            output += '\n'

        return output

    def decrypt_subtitles( self, data, iv, _id ):
        data = bytes_to_intlist( base64.b64decode( data ) )
        iv = bytes_to_intlist( base64.b64decode( iv ) )
        id = int( _id )
        key = obfuscate_key( id )
        decrypted_data = intlist_to_bytes(
            aes_cbc_decrypt( data, key, iv ) )
        return zlib.decompress( decrypted_data )
