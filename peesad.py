rom juicer.utils import *
from juicer.items import *

chann_pro = 'http://whatson.astro.com.my/woapi/whatsonAPI6/Source/channels/individual?channelid=%s&sid=null&uname=null'
pro_info = 'http://whatson.astro.com.my/woapi/whatsonAPI6/Source/showdetail?cid=0&eid=%s&sid=null&uname=null'
class AstroSpider(JuicerSpider):
    name = 'astro_browse'
    start_urls = ['http://whatson.astro.com.my/woapi/whatsonAPI6/Source/channels/index?sid=null&uname=null&c=1487412972054']

    def __init__(self, *args, **kwargs):
        super(AstroSpider, self).__init__(*args, **kwargs)
        self.dure_patt = re.compile(r'(\d+)h (\d+)m')
        self.dure_patt1 = re.compile(r'(\d+)m')
        self.dimention_patt = re.compile(r'(\d+)_(\d+)')

    def get_channel_items(self, sk, title, desc, genres, sub_genre, image, itme_zone, ref_url):
        itme_zone = '+05:30'
        channel_item = ChannelItem()
        channel_item.update({'sk':sk, 'title':title, 'description':desc,
                       'genres':genres, 'image':image, 'timezone_offset':itme_zone,
                       'reference_url':ref_url})
        return channel_item

    def get_rich_item(self, sk, program_sk, program_type,\
                       media_type, image_type, dimensions,\
                            description, image_url, reference_url):
