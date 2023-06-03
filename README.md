# AO3 Backup-to-Website

## What is this?

This is really two-and-a-half projects glued together. The first project scrapes the AO3 works for a single user and generates markdown files for backup and storage. The second project builds a static site based on those markdown files for hosting those works.

Uses [Scrapy](https://scrapy.org) for scraping AO3 and [Hugo](https://gohugo.io/) for generating a static site.

Scrapes AO3 and deploys to Github Pages using actions.


## How can I use this?

This is not currently designed to be usable for anyone not comfortable with the command line and modifying configuration files.

### Running locally

This is for if you don't want to futz around with getting GitHub actions to work or using GitHub in particular.

#### Scraping AO3
1. Run `git clone https://github.com/thedeadparrot/ao3backup.git`
2. Set up a python virtualenv.
3. Run `pip install -r ao3scrape/requirements.txt`
4. Modify `ao3scrape/settings.py` to set `AO3_USER` to your own AO3 username.
5. Run `git rm backup/content/posts/*` in ordert to delete all of my fic and clear the way for your own.
6. From within the `ao3scrape` subdirectory, run `scrapy crawl ao3`. This will create the markdown files `backup/content/posts`.

#### Building the static site
1. Install [Hugo](https://gohugo.io/).
2. Run `git submodule add hermit`. This will pull in the theme.
3. Modify `backup/config.toml` with your own name and links and other configuration you might be interested in.
4. Run `hugo` from within the `backup` directory.
5. Your static site should now be in `backup/public`, which can then be hosted wherever you wish.


### Running on GitHub

These instructions assume a familiarity with both GitHub and git.

1. Fork the repo.
2. Delete the markdown files in `backup/content/posts`.
3. Modify the settings in `backup/config.toml`.
4. Set up your fork to use GitHub Pages and the source 'GitHub Actions'.
5. Set up your fork to use GitHub Actions and 'all actions and reusable workflows'.
6. From your fork, run the action `Scrape AO3 and attempt to commit`, inserting the username when prompted.
7. Once that action has run (mine takes about 30 minutes), check your pull requests for the new markdown files and merge if they look good.
8. Run `Deploy Hugo site to Pages` to build and deploy your site.
