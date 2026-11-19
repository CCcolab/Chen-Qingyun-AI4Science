"""Reviewed scope and identities for the home and achievement overview revision."""

MANIFEST = 'provenance/platform-presentation.v51.json'
MANIFEST_SHA256 = '4f4392c55736ba2dae84bf2e9bc23f1bd28e5b4df83b798f7a634c1d8c7d8054'
PREDECESSOR = 'd7ea8adb1e826381e21a317e54ecd855b0fcbc0d'
PRESENTATION_ID = 'PLATFORM-HOME-ACHIEVEMENT-LINKS-20261119-v51'
HTML_PATHS = ('achievements/index.html', 'index.html')
CHANGED_FILES = {'site/'+name for name in HTML_PATHS} | {'scripts/story_sources_publication.py'}
V50_ADDITIONS = {
    'provenance/platform-presentation.v50.json':
        ('1d392c6af7f1ff6d2d226570fc363502559ff934d1ac14133515635a04e53f3f', 24594),
    'scripts/story_sources_publication.py':
        ('f29e917f7c5c446668bc31533427ac55bdf70cb504e8060abf8ed85e96c4ab23', 5719),
}
