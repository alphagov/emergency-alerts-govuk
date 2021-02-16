import os
from distutils.dir_util import copy_tree, mkpath, remove_tree
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, PrefixLoader


jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.abspath(os.path.dirname(__file__))),
    PrefixLoader({
        'govuk_frontend_jinja': PackageLoader('govuk_frontend_jinja')
    })
])
env = Environment(loader=jinja_loader, autoescape=True)

if __name__ == '__main__':
    # make build dir cleanly
    if os.path.isdir('./dist'):
        remove_tree('./dist')

    mkpath('./dist/assets')

    for page in [
        'index.html',
        'info.html',
        '404.html'
    ]:
        template = env.get_template(f'src/{page}')
        with open(f'dist/{page}', 'w') as file:
            file.write(template.render())
