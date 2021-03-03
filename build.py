import hashlib
from pathlib import Path

from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    PrefixLoader,
)

repo = Path('.')
src = repo / 'src'
dist = repo / 'dist'
root = dist / 'alerts'


jinja_loader = ChoiceLoader([
    FileSystemLoader(str(repo)),
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
    root.mkdir(exist_ok=True)

    for page in src.glob('*.html'):
        template = env.get_template(str(page))
        if 'index.html' in str(page):
            target = dist / page.relative_to(src)
        else:
            target = root / page.relative_to(src)
        target.parent.mkdir(exist_ok=True)
        target.open('w').write(template.render())
        if 'index.html' not in str(page):
            target.replace(str(target).replace(".html", ""))
