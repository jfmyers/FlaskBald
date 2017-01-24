import json
import os


def front_end_js_src():
    from memory_site.run import app
    url = app.config.get('STATIC_ASSET_JS_URL', '.')
    url = '{0}/app-{1}.min.js'.format(url, front_end_hash())
    return url


def front_end_css_src():
    from memory_site.run import app
    url = app.config.get('STATIC_ASSET_CSS_URL', '.')
    url = '{0}/app-{1}.min.css'.format(url, front_end_hash())
    return url


def front_end_hash():
    from memory_site.run import BASE_DIR
    tmp_path = os.path.join(BASE_DIR, '..', 'tmp')
    front_end_manifest_path = os.path.join(tmp_path, 'front_end_manifest.json')

    if not os.path.isdir(tmp_path):
        return None

    if not os.path.exists(front_end_manifest_path):
        return None

    manifest_content = open(front_end_manifest_path).read()

    manifest = json.loads(manifest_content)
    return manifest.get('hash')


template_functions = {
    "front_end_js_src": front_end_js_src,
    "front_end_css_src": front_end_css_src,
    "front_end_hash": front_end_hash
}
