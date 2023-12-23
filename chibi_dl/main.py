#!/usr/bin/env python3
import json
import sys
import logging
import random
from argparse import ArgumentParser

from chibi.file import Chibi_path
from chibi.config import basic_config, load as load_config

from chibi_dl.site import Site


logger_formarter = '%(levelname)s %(name)s %(asctime)s %(message)s'


parser = ArgumentParser(
    description="descarga mangas", fromfile_prefix_chars='@'
)

parser.add_argument(
    "sites", nargs='+', metavar="site",
    help="urls de las series que se quieren descargar" )

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
    "-config_site", type=Chibi_path, dest="config_site",
    help="python, yaml o json archivo con el usuario y password de cada sitio"
)


def main():
    args = parser.parse_args()
    basic_config( args.log_level )

    if args.config_site:
        load_config( args.config_site )

    for site in args.sites:
        site = Site( url=site )
        for link in site.links:
            print( link )
