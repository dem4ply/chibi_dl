from marshmallow import Schema, pre_load, fields, EXCLUDE, post_load
from chibi_marshmallow import fields as chibi_fields


class Torrent( Schema ):
    add_at = chibi_fields.Timestamp( data_key='added' )
    file_size = fields.Integer( data_key='fsize' )
    size = fields.Integer( data_key='tsize' )
    name = fields.String()
    hash = fields.String()


class Metadata( Schema ):
    category = chibi_fields.String_lower()
    expunged = fields.Bool()
    images_len = fields.Integer( data_key='filecount' )
    images_size = fields.Integer( data_key='filesize' )
    id = fields.Integer( data_key='gid' )
    upload_at = chibi_fields.Timestamp( data_key='posted' )
    rating = fields.Float()
    title = fields.String()
    titles__jpn = fields.String( data_key='title_jpn' )
    token = fields.String()
    torrent_count = fields.Integer( data_key='torrentcount' )
    torrents = fields.Nested( Torrent, many=True )
    uploader = fields.String()

    cover_url = fields.String( data_key='thumb' )
    archiver_key = fields.String()

    tags = fields.List( chibi_fields.String_lower() )

    @pre_load
    def ignore_gmetadata( self, data, *args, many=False, **kw ):
        if many:
            return data[ 'gmetadata' ]
        return data[ 'gmetadata' ][0]

    @post_load
    def rename_title_jpn( self, data, *args, **kw ):
        title_jpn = data.pop( 'titles__jpn' )
        data[ 'alternative_titles' ] = dict( jpn=title_jpn )
        return data
