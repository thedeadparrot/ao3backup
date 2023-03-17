# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import yaml

from markdownify import markdownify
from slugify import slugify

from ao3scrape import settings


class Ao3ScrapePipeline:
    """ Only handles items of type WorkItem. """

    def process_item(self, item, spider):
        title = item['title']
        slug_title = slugify(title)
        
        work_text = markdownify(item['text']).strip()
        frontmatter = {
                'summary': markdownify(item['summary']).strip(),
                'author': ', '.join(item['author']).strip(),
                'notes': markdownify(item['notes']).strip(),
                'fandom': ", ".join(item['fandom']),
                'characters': ", ".join(item['character']),
                'relationship' : ", ".join(item['relationship']),
                'freeform': ", ".join(item['freeform']),
                'warnings': ", ".join(item['warning']),
                #'rating': item['rating'][0],
                'published': item['published'],
        }

        with open(f'{settings.OUTPUT_DIRECTORY}/{slug_title}.md', 'w') as f:
            # Write out metadata to frontmatter.
            f.write('---\n')
            frontmatter_text = yaml.dump(frontmatter)
            f.write(frontmatter_text)
            f.write('---\n\n')
            f.write(work_text)

        return item
