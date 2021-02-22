from pathlib import Path
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, PrefixLoader

import hashlib


root = Path('.')
src = root / 'src'
dist = root / 'dist'
assets = dist / 'assets'

jinja_loader = ChoiceLoader([
    FileSystemLoader(str(root)),
    PrefixLoader({
        'govuk_frontend_jinja': PackageLoader('govuk_frontend_jinja')
    })
])


def file_fingerprint(path):
    contents = open(str(dist) + path, 'rb').read()
    return path + '?' + hashlib.md5(contents).hexdigest()


env = Environment(loader=jinja_loader, autoescape=True)
env.filters['file_fingerprint'] = file_fingerprint

if __name__ == '__main__':
    for page in src.glob('**/*.html'):
        template = env.get_template(str(page))
        target = dist / page.relative_to(src)
        target.parent.mkdir(exist_ok=True)
        target.open('w').write(template.render())

    assets.mkdir(exist_ok=True)
