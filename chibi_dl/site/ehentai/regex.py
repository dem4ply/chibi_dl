import re


#https://e-hentai.org/g/618395/0439fa3666/
re_episode = re.compile( r'https://e-hentai.org/g/\d+/\w+/?' )
#re_image = re.compile( r'https://nhentai.net/g/\d+/\d+/?' )
re_main = re.compile( r'https://e-hentai.org/?' )

banned_time = re.compile(
    r'Your IP address has been temporarily banned for excessive '
    r'pageloads which indicates that you are using automated '
    r'mirroring/harvesting software. '
    r'The ban expires in (\d+) minutes and (\d+) seconds' )


banned_time_2 = re.compile(
    r'Your IP address has been temporarily banned for excessive '
    r'pageloads which indicates that you are using automated '
    r'mirroring/harvesting software. '
    r'The ban expires in (\d+) hours and (\d+) minutes' )
