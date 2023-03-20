#!/usr/bin/env python3
import json
import sys
import logging
import random
from argparse import ArgumentParser

from chibi.file import Chibi_path
from chibi.config import basic_config, load as load_config

from chibi_dl.site import Site

from chibi_dl.site.nhentai.site import Nhentai
from chibi_dl.site.crunchyroll.site import Crunchyroll
from chibi_dl.site.tmofans import TMO_fans


logger_formarter = '%(levelname)s %(name)s %(asctime)s %(message)s'


parser = ArgumentParser(
    description="descarga mangas", fromfile_prefix_chars='@'
)

parser.add_argument(
    "sites", nargs='+', metavar="site",
    help="urls de las series que se quieren descargar" )

parser.add_argument(
    "--user", '-u', dest="user", default="",
    help="usuario del sitio" )

parser.add_argument(
    "--password", '-p', dest="password", default="",
    help="contrasenna del sitio" )

parser.add_argument(
    "--resoulution", '-r', dest="quality", default=240, type=int,
    help="resolucion a descargar" )

parser.add_argument(
    "--only_print", dest="only_print", action="store_true",
    help="define si silo va a imprimir la lista de links o episodios"
)

parser.add_argument(
    "--only_metadata", dest="only_metadata", action="store_true",
    help="se define si solo se queire recolectar los datos y no descargar"
)

parser.add_argument(
    "--only_links", dest="only_print_links", action="store_true",
    help="si se usa solo imprimira las urls"
)

parser.add_argument(
    "--random", dest="random", action="store_true",
    help="procesa las urls en un orden aleatorio"
)

parser.add_argument(
    "--log_level", dest="log_level", default="INFO",
    help="nivel de log",
)

parser.add_argument(
    "-o", "--output", type=Chibi_path, dest="download_path",
    help="ruta donde se guardara el video o manga" )

parser.add_argument(
    "-config_site", type=Chibi_path, dest="config_site",
    help="python, yaml o json archivo con el usuario y password de cada sitio"
)


def main():
    args = parser.parse_args()
    basic_config( args.log_level )

    if args.config_site:
        load_config( args.config_site )

    tmo_fans = TMO_fans( user=args.user, password=args.password, )
    proccessors = [
        Nhentai(),
        Crunchyroll(
            user=args.user, password=args.password,
            quality=args.quality ),
        tmo_fans,
    ]

    for site in args.sites:
        for proccesor in proccessors:
            if proccesor.i_can_proccess_this( site ):
                if proccesor.append( site ):
                    break


    if args.only_metadata:
        for proccesor in proccessors:
            for batch in proccesor:
                for item in batch:
                    json.dump( item.metadata, sys.stdout )
    if args.only_print:
        if args.only_print_links:
            for serie in tmo_fans.series:
                print( serie.url )
        """
        for proccesor in proccessors:
            logger.info( proccesor )
            for batch in proccesor:
                logger.info( proccesor )
                for item in batch:
                    logger.info( proccesor )
                    json.dump( item.metadata, sys.stdout )
        """
    else:
        for serie in tmo_fans.series:
            serie.download( args.download_path )

        """
        for proccesor in proccessors:
            proccesor.login()
            for download in proccesor:
                download.download( args.download_path )
        """


    """
    site = Site(
        user=args.user, password=args.password,
        quality=args.quality )
    if args.random:
        random.shuffle( args.sites )
    site.append( *args.sites )

    if args.only_print:
        site.print( args.only_print_links )
    else:
        site.download( args.download_path )
    """
