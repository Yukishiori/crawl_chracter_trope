import scrapy
import json
from unicodedata import normalize


class QuotesSpider(scrapy.Spider):
    name = "character"
    base_url = "https://tvtropes.org"

    def start_requests(self):
        urls = [
            "https://tvtropes.org/pmwiki/pmwiki.php/Main/Manga",
            "https://tvtropes.org/pmwiki/pmwiki.php/Main/LightNovels",
            # "https://tvtropes.org/pmwiki/pmwiki.php/Main/Anime"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.get_anime_url)

    def get_anime_url(self, response):
        for component in response.css(".folder .twikilink"):
            anime_page = component.css("::attr(href)").get()
            media_name = component.css("::text").get()
            character_page_prob = self.base_url + \
                "/pmwiki/pmwiki.php/Characters/" + anime_page.split('/')[-1]
            # if character_page_prob in ['https://tvtropes.org/pmwiki/pmwiki.php/Characters/Oreimo']:
            #     yield scrapy.Request(url=character_page_prob, callback=self.parse_anime_character, meta={"media_name": media_name})
            yield scrapy.Request(url=character_page_prob, callback=self.parse_anime_character, meta={"media_name": media_name})

    def parse_anime_character(self, response):
        if response.status == 404:
            return
        media_name = response.meta.get('media_name')

        characters = []
        # only h2
        # response.css("#main-article > h2, #main-article > p , #main-article > li")[0].css("*::text")
        if response.css(".folderlabel"):
            elements = response.css(
                "#main-article > .folder, #main-article > .folderlabel")
            top = ""
            for i in range(1, len(elements), 2):
                top = normalize('NFKD', elements[i].css("::text").get())
                data_element = elements[i+1]
                if data_element.css("h2"):
                    curr_char = ""
                    description = []
                    tropes = []
                    childrem_elem = data_element.css('h2,p,div>ul>li')
                    for ele in childrem_elem:
                        tag_name = ele.re_first("<.+?>")
                        if tag_name == '<h2>' and curr_char:
                            char = self.get_character_object(
                                curr_char, description, tropes)
                            # self.log(f'case 1 {char}')
                            characters.append(char)
                            description = []
                            tropes = []
                        if tag_name == '<h2>':
                            curr_char = ele.css("*::text").get()
                            # self.log(f"current character: {curr_char}")

                        elif tag_name == '<p>' and curr_char:
                            if ele.css("*::text").getall():
                                description = description.extend(
                                    ele.css("*::text").getall())
                            # self.log(
                            #     f"p : {description}") if description else None
                        elif tag_name == '<li>' and curr_char:
                            trope = ele.css("*::text").getall()
                            tropes.append(trope)
                            # self.log(f"li : {trope}")
                    if curr_char:
                        char = self.get_character_object(
                            curr_char, description, tropes)
                        # self.log(f'case 1 {char}')
                        characters.append(char)
                        description = []
                        tropes = []

                else:
                    # self.log('case2')
                    # self.log(f'character: {top}')
                    description = description.extend(
                        data_element.css("p *::text").getall())
                    # self.log(f"p: {description}")
                    tropes = [li.css("*::text").getall()
                              for li in data_element.css("div>ul>li")]
                    if top:
                        char = self.get_character_object(
                            top, description, tropes)
                        # self.log(f'case 2 {char}')
                        characters.append(char)

        elif response.css('#main-article > h2'):
            elements = response.css(
                "#main-article > h2, #main-article > p , #main-article>ul>li")
            curr_char = ""
            description = []
            tropes = []
            for element in elements:
                tag_name = element.re_first("<.+?>")
                if tag_name == '<h2>' and curr_char:
                    char = self.get_character_object(
                        curr_char, description, tropes)
                    # self.log(f'case 3 {char}')
                    characters.append(char)
                    description = []
                    tropes = []
                if tag_name == '<h2>':
                    curr_char = element.css("::text").get()
                elif tag_name == '<p>' and curr_char:
                    description = description.extend(
                        element.css("*::text").getall())
                    # self.log(f"current character: {curr_char}")
                    # self.log(f"p : {description}") if description else None
                elif tag_name == '<li>' and curr_char:
                    tropes.append(element.css("*::text").getall())
                    # self.log(f"li : {trope}")
            if curr_char:
                char = self.get_character_object(
                    curr_char, description, tropes)
                # self.log(f'case 3 {char}')
                characters.append(char)
                description = []
                tropes = []

        elif response.css('#main-article .twikilink'):
            for ele in response.css('.twikilink'):
                anime_page = ele.css("::attr(href)").get()
                character_page_prob = self.base_url + \
                    "/pmwiki/pmwiki.php/Characters/" + \
                    anime_page.split('/')[-1]
                media_name_1 = media_name + ele.css("::text").get()
                yield scrapy.Request(url=character_page_prob, callback=self.parse_anime_character, meta={"media_name": media_name_1})
        # only folder
        # both

        # self.log(f'writting {media_name}.json {len(characters)}')
        if characters:
            with open(f'crawled/{media_name}.json', 'w+') as outfile:
                json.dump({"name": media_name, "data": characters}, outfile)

    def get_character_object(self, name, description, lis):
        # try:
        return {
            "name": name,
            "description": "".join(description),
            "tropes": [{"trope_type": li[1] if len(li) > 1 else li[0], "trope_description": "".join(li[2:]) if len(li) > 2 else ""} for li in lis]
        }
