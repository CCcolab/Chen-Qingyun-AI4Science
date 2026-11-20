"""Reviewed scope and preceding file identities for the eight research-line overviews."""
from render_representative_studies import ROUTES

MANIFEST = 'provenance/platform-presentation.v54.json'
MANIFEST_SHA256 = '25b2e3339d8f5825e520baa45dbc38b7dfb68f3edc342b97b4fad5b08bff77e8'
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
