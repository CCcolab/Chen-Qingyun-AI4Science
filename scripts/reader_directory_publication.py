"""Scope the public site navigation and its corresponding GitHub reader documents."""
MANIFEST = 'provenance/platform-presentation.v55.json'
MANIFEST_SHA256 = '03eabfce24506d575b87a3d7b96dd063739e793134c62c93fc257c080aa870a2'
PREDECESSOR = '46dd2d9c41b3113f44b98953d36277e421b21ff8'
PRESENTATION_ID = 'PLATFORM-READER-DIRECTORY-20261120-v55'
HTML_PATHS = ('index.html', 'achievements/index.html', 'topics/index.html', 'research/index.html',
              'topics/single-electron-transfer/index.html', 'topics/fluoroporphyrins/index.html',
              'topics/perfluorosulfonates/index.html', 'topics/fluorinated-small-rings/index.html',
              'topics/deoxyfluorination/index.html', 'topics/sulfonyl-fluoride/index.html',
              'people/stories/index.html', 'pftb/index.html')
DOCUMENT_PATHS = ('README.md', 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md',
                  'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md', 'docs/PLATFORM_PURPOSE_zh-CN.md',
                  'docs/PLATFORM_ROADMAP_zh-CN.md', 'docs/AI_RESEARCH_zh-CN.md',
                  'docs/A01_HISTORICAL_ACHIEVEMENTS_zh-CN.md',
                  'docs/A01_FIRST_REPORT_zh-CN.md',
                  *(f'docs/A{i:02d}_ACADEMIC_ACHIEVEMENTS_zh-CN.md' for i in range(2, 9)))
CHANGED_FILES = {'site/'+name for name in HTML_PATHS} | set(DOCUMENT_PATHS) | {'scripts/story_sources_publication.py'}
V54_ADDITIONS = {
    'provenance/platform-presentation.v54.json':
        ('25b2e3339d8f5825e520baa45dbc38b7dfb68f3edc342b97b4fad5b08bff77e8', 126581),
    'scripts/research_contributions_publication.py':
        ('5422950e040558a1111aa9270d6da14cb243a3cbbd9042f304008f4613adf20a', 899),
}
