"""Reviewed page scope and predecessor identities for the eight representative studies."""
from render_representative_studies import ROUTES

MANIFEST = 'provenance/platform-presentation.v52.json'
MANIFEST_SHA256 = 'c68409cea1bec2de4f0bd20fbe5d4e585c833d4548986c236f337d0969f531a7'
PREDECESSOR = 'bc65a9f2a540b109a50a2bde2c21ca148fdb309c'
PRESENTATION_ID = 'PLATFORM-STUDY-DETAILS-20261119-v52'
HTML_PATHS = ROUTES[:8]
CHANGED_FILES = {'site/'+name for name in HTML_PATHS} | {'scripts/story_sources_publication.py'}
V51_ADDITIONS = {
    'provenance/platform-presentation.v51.json':
        ('4f4392c55736ba2dae84bf2e9bc23f1bd28e5b4df83b798f7a634c1d8c7d8054', 23062),
    'scripts/home_achievement_links_publication.py':
        ('dcadcc09ed9318fbcff8e5e618cc38efdad508f16fe4b8d41c46fd485436facc', 781),
}
