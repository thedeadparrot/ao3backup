To run locally:

1. create a Python virtualenv.
2. `pip install -r requirements.txt`
3. To customize the user, modify `ao3scrape/settings.py` or set the environment variable `AO3_USER`.
4. Run `scrapy crawl ao3`.

Markdown files will be created in `../backup/content/posts`.
