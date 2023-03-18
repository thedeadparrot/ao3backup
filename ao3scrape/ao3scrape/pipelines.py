import yaml

from scrapy.selector import Selector
from markdownify import markdownify
from slugify import slugify

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

    def process_item(self, item, spider):
        title = item['title']
        slug_title = slugify(title)
        
        if item.get('single_chapter_text'):
            work_text = markdownify(item['single_chapter_text']).strip()
        else:
            work_text = self.process_multi_chapter_text(item['multi_chapter_text'])

        frontmatter = {
                'title': title,
                'summary': markdownify(item['summary']).strip(),
                'author': ', '.join(item['author']).strip(),
                'notes': markdownify(item['notes']).strip(),
                'fandom': item['fandom'],
                'characters': item['character'],
                'relationship' : item['relationship'],
                'tags': item['freeform'],
                'warnings': ", ".join(item['warning']),
                #'rating': item['rating'][0],
                'ao3_url': item['url'],
                'date': item['published'],
        }

        with open(f'{settings.OUTPUT_DIRECTORY}/{slug_title}.md', 'w') as f:
            # Write out metadata to frontmatter.
            f.write('---\n')
            frontmatter_text = yaml.dump(frontmatter)
            f.write(frontmatter_text)
            f.write('---\n\n')
            f.write(work_text)

        return item
