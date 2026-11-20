"""Reviewed scope for the home, achievement overview and three research-line introductions."""

MANIFEST = 'provenance/platform-presentation.v53.json'
MANIFEST_SHA256 = '46c12253a1e424a62180d65080211d5081ffd61c46f507300691d4313c6ae3ce'
PREDECESSOR = 'bdbb270f6ec7978581223a83cd0571be81935ee7'
PRESENTATION_ID = 'PLATFORM-RESEARCH-LINE-OVERVIEWS-20261120-v53'
HTML_PATHS = ('index.html', 'achievements/index.html', 'topics/chen-reagent/index.html',
              'topics/single-electron-transfer/index.html', 'topics/fluoroporphyrins/index.html')
CHANGED_FILES = {'site/'+name for name in HTML_PATHS} | {'scripts/story_sources_publication.py'}
V52_ADDITIONS = {
    'provenance/platform-presentation.v52.json':
        ('c68409cea1bec2de4f0bd20fbe5d4e585c833d4548986c236f337d0969f531a7', 96048),
    'scripts/study_details_publication.py':
        ('e12d147ad8d376f703d42f091f78fc5d5303c8de2a0fc1c9d3236936b6c6936b', 805),
}
