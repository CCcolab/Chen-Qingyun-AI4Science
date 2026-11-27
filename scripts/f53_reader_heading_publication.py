"""Record the A04 reader headings and corresponding routes."""

MANIFEST = 'provenance/platform-presentation.v72.json'
MANIFEST_SHA256 = 'd16911a963e13d10dab6ce551621d5afb754f2e61f1abce8cdde2b8eca8529a2'
PREDECESSOR = '491f118f59e364393f12a3e282d12f26fc3c98de'
PRESENTATION_ID = 'PLATFORM-A04-READER-HEADINGS-20261127-v72'
HTML_PATHS = (
    'achievements/index.html',
    'index.html',
    'people/stories/index.html',
    'research/index.html',
    'topics/f53/index.html',
    'topics/index.html',
)
CHANGED_FILES = {
    'scripts/story_sources_publication.py',
    'site/achievements/index.html',
    'site/index.html',
    'site/people/stories/index.html',
    'site/research/index.html',
    'site/topics/f53/index.html',
    'site/topics/index.html',
}
V71_ADDITIONS = {
    'provenance/platform-presentation.v71.json': (
        '49455e679fac0d2df0d7f1a259c0ce49a0babc57f1a21fe8b9327a61b611713d', 10979,
    ),
    'scripts/f53_reading_titles_publication.py': (
        '07e424331c1e08c1271d11d6c57a884a350088524c9a9f13bfe2edc293d9ed9e', 893,
    ),
}
