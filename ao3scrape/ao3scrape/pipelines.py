import yaml

from scrapy.selector import Selector
from markdownify import markdownify

from ao3scrape import settings


class Ao3ScrapePipeline:
    """ Only handles items of type WorkItem. """

    def process_multi_chapter_text(self, chapter_text_list):
        processed_list = []

        for element in chapter_text_list:
            el_selector = Selector(text=element)
            # Extract out the auto-generated chapter title and then add in the user-supplied title.
            chapter_title = el_selector.xpath('//h3[@class="title"]/a/text()').get() + ''.join(el_selector.xpath('//h3[@class="title"]/text()').getall()).strip()
            chapter_summary = ''.join(el_selector.xpath('//div[@id="summary"]/blockquote/*').getall()).strip()
            chapter_notes = ''.join(el_selector.xpath('//div[@id="notes"]/blockquote/*').getall()).strip()
            # The first element is a landmark h3, so we want to drop that for our backup.
            chapter_text = ''.join(el_selector.xpath('//div[@role="article"]/*').getall()[1:]).strip()
            processed_chapter_text = f'''<h3>{chapter_title}</h3>
                <h4>Chapter Summary</h4>
                <blockquote>{chapter_summary}</blockquote>
                <h4>Chapter Notes</h4>
                <blockquote>{chapter_notes}</blockquote>
                \n\n{chapter_text}
            '''
            processed_list.append(processed_chapter_text)

        return markdownify('\n\n'.join(processed_list).strip())

    def strip_ending_periods(self, item_list):
        # This is a terrible hack to ensure that House fandom can be rendered by Hugo, which seems
        # to have problems with taxonomies that end in a period. It will look weird, but oh well?
        return [item.removesuffix('.') for item in item_list]

    def process_item(self, item, spider):
        if item.get('single_chapter_text'):
            work_text = markdownify(item['single_chapter_text']).strip()
        else:
            work_text = self.process_multi_chapter_text(item['multi_chapter_text'])

        stripped_fandoms = self.strip_ending_periods(item['fandom'])
        stripped_tags = self.strip_ending_periods(item['freeform'])
        frontmatter = {
                'title': item['title'],
                'summary': markdownify(item['summary']).strip(),
                'author': ', '.join(item['author']).strip(),
                'notes': markdownify(item['notes']).strip(),
                'fandom': stripped_fandoms,
                'characters': item['character'],
                'relationship' : item['relationship'],
                'tags': stripped_tags,
                'warnings': ", ".join(item['warning']),
                'rating': item['rating'][0],
                'ao3_url': f'https://archiveofourown.org/works/{item["work_id"]}',
                'date': item['published'],
        }
        if 'series' in item:
            frontmatter['series'] = self.strip_ending_periods(item['series'])
            frontmatter['series_weight'] = item['series_position']

        with open(f'{settings.OUTPUT_DIRECTORY}/{item["work_id"]}.md', 'w') as f:
            # Write out metadata to frontmatter.
            f.write('---\n')
            frontmatter_text = yaml.dump(frontmatter)
            f.write(frontmatter_text)
            f.write('---\n\n')
            f.write(work_text)

        return item
