========
Chibi_dl
========


is a command line tool for download series from crunchyroll.com and tmofans.com

in the case of crunchyroll is going to download the video and the subtitles
and joined in a mkv

for the mangas from tmofans is going to compress all the images in a
zip and rename the extencion to cbz


=======
install
=======


.. code-block:: bash

	pip install chibi_dl

is going to add the command chibi_dl


===========
how to used
===========


.. code-block:: none

	usage: chibi_dl [-h] [--user USER] [--password PASSWORD]
						[--resoulution QUALITY]
						site [site ...] download_path

	descarga mangas

	positional arguments:
	site                  urls de las series que se quieren descargar
	download_path         lugar de descarga

	optional arguments:
	-h, --help            show this help message and exit
	--user USER, -u USER  usuario del sitio
	--password PASSWORD, -p PASSWORD
									contrasenna del sitio
	--resoulution QUALITY, -q QUALITY
									resolucion a descargar

for download a serie from crunchyroll need the user and password if you what
downlaod the serie in 720p o 1080p

.. code-block:: bash

	chibi_dl -q 720 --user user -p password "https://www.crunchyroll.com/es/yuruyuri" /path/to/save/serie


if you are ok with the lower resolution you not need the user and password

.. code-block:: bash

	chibi_dl -q 240 "https://www.crunchyroll.com/es/yuruyuri" /path/to/save/serie

in the case of tmo fans

.. code-block:: bash

	chibi_dl "https://tmofans.com/library/manga/13698/komi-san-wa-komyushou-desu" /path/to/save/serie
