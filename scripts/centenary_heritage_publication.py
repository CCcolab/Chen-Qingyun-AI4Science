"""Scope the centenary framing, reader tone and 8+1 heritage presentation after v61."""

MANIFEST = 'provenance/platform-presentation.v62.json'
MANIFEST_SHA256 = '832ab18b70279900de448691e940a26207569adf94893458323fed438388bc32'
PREDECESSOR = 'afdf23a1a8f1e74158d05f29405d4e2c30b272b3'
PRESENTATION_ID = 'PLATFORM-CENTENARY-AND-HERITAGE-PRESENTATION-20261123-v62'
HTML_PATHS = (
    'achievements/index.html',
    'index.html',
    'topics/chen-reagent/index.html',
    'topics/f53/index.html',
    'topics/fluorinated-small-rings/index.html',
    'topics/index.html',
    'topics/refrigerants/index.html',
    'topics/sulfonyl-fluoride/index.html',
)
DOCUMENT_PATHS = ()
CHANGED_FILES = (
    {'site/' + name for name in HTML_PATHS}
    | {'scripts/story_sources_publication.py'}
)
V61_ADDITIONS = {
    'provenance/platform-presentation.v61.json':
        ('62cf0ea40368f73280ef2baded1f21cb2fe1050867362abaeaa77ad11214e09c', 13827),
    'scripts/major_achievement_card_publication.py':
        ('e0a0d2d08d0880d59b932561422909f79383b9dee1cab827c4c77ba5cfca1bad', 910),
}
