"""Scope four primary scientific achievements before the expanded research-line index."""
MANIFEST = 'provenance/platform-presentation.v56.json'
MANIFEST_SHA256 = '18c1948ba8661badc7da892195dff31e915fdc66ec3ddbf47df1c448e1b2bfc6'
PREDECESSOR = '09041abc94f7f5d492c410e5d5a6ddd1d681e117'
PRESENTATION_ID = 'PLATFORM-FOUR-PRIMARY-ACHIEVEMENTS-20261121-v56'
HTML_PATHS = ('index.html', 'achievements/index.html', 'topics/index.html',
              'topics/fluoroporphyrins/index.html')
DOCUMENT_PATHS = ('README.md', 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md',
                  'docs/PLATFORM_PURPOSE_zh-CN.md')
CHANGED_FILES = {'site/'+name for name in HTML_PATHS} | set(DOCUMENT_PATHS) | {'scripts/story_sources_publication.py'}
V55_ADDITIONS = {
    'provenance/platform-presentation.v55.json':
        ('eef3a5d8569ce4a1f40d514a23866c768c5518cac29f82c940955c76dc01d3d5', 212041),
    'scripts/reader_directory_publication.py':
        ('19ff2c0e384b91a3a467adf63144dbedc43ad40e26145a2745e519cdbc452bde', 1654),
}
