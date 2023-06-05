#!/usr/bin/env python3
import requests
import random
import os
import subprocess
import argparse
import coloredlogs, logging

parser = argparse.ArgumentParser(
                    prog='random-anime-wallpaper',
                    description='Fetches a random recent anime wallpaper from anime-pictures.net',
                    epilog='Enjoy your new wallpaper!')
parser.add_argument('-p', '--path', help='Path to save the wallpaper to', default=None)
parser.add_argument('-s', '--set', help='Set the wallpaper as the desktop background', default=True)
parser.add_argument('-r', '--remove', help='Remove the image after saving. Only works if --set is true.', default=True)
parser.add_argument('-pg', '--pages', help='Page count to fetch wallpapers from. The higher, the more random the wallpaper will be.', type=int, default=0)
parser.add_argument('-ar', '--aspect-ratio', help='Aspect ratio of the wallpaper. Default is 16:9', default='16:9')
parser.add_argument('-q', '--query', help='List of tags to search for')

args = parser.parse_args()
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)

BASE_URL = "https://anime-pictures.net/api/v3/posts"
CDN_URL = "https://images.anime-pictures.net"
PARAMS = {
    "page": random.randint(0, args.pages),
    "aspect": args.aspect_ratio,
    "order_by": "date",
    "ldate": 0,
    "lang": 'en',
}

if args.query:
    PARAMS['search_tag'] = args.query.replace(' ', '||').replace(',', '||')

def main():
    logger.info(f'Fetching wallpaper from anime-pictures.net from the last {args.pages} pages with aspect ratio {args.aspect_ratio}')
    if args.query:
        logger.info('Searching for tags: ' + ', '.join(PARAMS['search_tag'].split('||')))

    req = requests.get(BASE_URL, params=PARAMS)
    data = req.json()
    posts = [post['md5'] + post['ext'] for post in data['posts']]
    urls = [f'{CDN_URL}/{post[0:3]}/{post}' for post in posts]

    if len(urls) == 0:
        logger.error('No wallpapers found. Try increasing the page count or changing the query.')
        return

    url = random.choice(urls)
    filename = url.split('/')[-1]

    if not args.path:
        args.path = os.path.join(os.path.expanduser('~'), 'Pictures', 'Wallpapers')
        os.makedirs(args.path, exist_ok=True)

    with open(os.path.join(args.path, filename), 'wb') as f:
        logger.info(f'Saving image to {args.path}/{filename}')
        f.write(requests.get(url).content)

    if args.set:
        process = subprocess.run(['python', '-m', 'pywal', '-i', f'{args.path}/{filename}'])
        try:
            process.check_returncode()
            logger.info('Successfully set image as wallpaper')
        except:
            logger.error('Failed to set image as wallpaper. Is Pywal installed?')

    if args.set and args.remove:
        os.remove(os.path.join(args.path, filename))
        logger.info('Removed the image file.')

if __name__ == '__main__':
    main()
