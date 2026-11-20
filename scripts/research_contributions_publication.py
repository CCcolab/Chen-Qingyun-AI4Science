"""Reviewed scope and preceding file identities for the eight research-line overviews."""
from render_representative_studies import ROUTES

MANIFEST = 'provenance/platform-presentation.v54.json'
MANIFEST_SHA256 = '49afe43fd0f81d28a2e3c999a3e95a9ba88edb476edc759d118b7dd3188f1db8'
PREDECESSOR = 'a1da87c527cda2b34ac33c324e3b4b4ca1561e88'
PRESENTATION_ID = 'PLATFORM-RESEARCH-CONTRIBUTIONS-20261120-v54'
HTML_PATHS = ('index.html', 'achievements/index.html', *ROUTES[:8], 'topics/perfluorosulfonates/index.html')
CHANGED_FILES = {'site/'+name for name in HTML_PATHS} | {'scripts/story_sources_publication.py'}
V53_ADDITIONS = {
    'provenance/platform-presentation.v53.json':
        ('46c12253a1e424a62180d65080211d5081ffd61c46f507300691d4313c6ae3ce', 40584),
    'scripts/research_line_overviews_publication.py':
        ('065a7053b924e13e57c1502b5b0daf301c995d07b2c502531d34c58f7286c443', 924),
}
