from chibi_requests.chibi_url import Chibi_url
from chibi_requests.other import Force_json
from chibi_dl.site.ehentai.serializers import Metadata


class Metadata_response( Force_json ):
    serializer = Metadata


metadata = Chibi_url(
    "https://api.e-hentai.org/api.php", response_class=Metadata_response )
