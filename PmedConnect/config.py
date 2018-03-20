ENTREZ_MAX_RETRIEVE = 100000

RESULTS_PER_SEARCH_REQUEST = 10000
RESULTS_PER_FETCH_REQUEST = 10000

AVAILABLE_FIELDS = [
  'pmid', 'doi', 'title', 'abstract',
  'pub_year', 'pub_month', 'pub_day',
  'journal_title', 'journal_iso', 'journal_issn',
  'keywords',
  'date_pubmed_created', 'date_pubmed_updated',
  'date_pubmed_published', 'date_medline_published'
]

RETRIEVE_FIELDS = AVAILABLE_FIELDS

PUBMED_PATHS = {
  'path_doi': {'paths': [['MedlineCitation', 'Article', 'ELocationID']]},
  'path_title': {'paths': [['MedlineCitation', 'Article', 'ArticleTitle']]},
  'path_abstract': {'paths': [['MedlineCitation', 'Article', 'Abstract', 'AbstractText']]},
  'path_vol': {'paths': [['MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'Volume']]},
  'path_pages': {'paths': [['MedlineCitation', 'Article', 'Pagination', 'MedlinePgn']]},
  'path_pub_year': {'paths': [['MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Year']]},
  'path_pub_month': {'paths': [['MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Month']]},
  'path_pub_day': {'paths': [['MedlineCitation', 'Article', 'Journal', 'JournalIssue', 'PubDate', 'Day']]},
  'path_date_pubmed_created': {'paths': [['MedlineCitation', 'DateCreated']]},
  'path_date_pubmed_updated': {'paths': [['MedlineCitation', 'DateRevised']]},

  'path_journal_title': {'paths': [['MedlineCitation', 'Article', 'Journal', 'Title']]},
  'path_journal_iso': {'paths': [['MedlineCitation', 'Article', 'Journal', 'ISOAbbreviation'], ['MedlineCitation', 'MedlineJournalInfo', 'MedlineTA']]},
  'path_journal_issn': {'paths': [['MedlineCitation', 'Article', 'Journal', 'ISSN'], ['MedlineCitation', 'MedlineJournalInfo', 'ISSNLinking']]},
}