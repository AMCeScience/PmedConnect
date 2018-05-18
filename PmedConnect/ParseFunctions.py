import PmedConnect.ParseFields as pf
import PmedConnect.config as config
import calendar

class Parser(object):
  available_parse_paths = config.PUBMED_PATHS

  # This is for translating abbreviated month names to numbers.
  months_rdict = {v: str(k) for k, v in enumerate(calendar.month_abbr)}    

  def __init__(self, fields, extra_parse_functions = None):
    self.build_parse_functions()
    # self.add_extra_parse_functions(extra_parse_functions)

    field_validator = pf.ParseFields(self.parse_functions)
    
    self.fields = field_validator.validate(fields)

  def extract_from_docs(self, docs):
    parsed_docs = []

    for doc in docs:
      parsed_docs.append(self.extract_fields(doc))

    return parsed_docs

  def extract_fields(self, doc):
    """Extracts the required fields from the documents,
    where each document is an Entrez dictionary"""    
    parsed_doc = {}

    parsed_doc['doc_type'] = self.determine_doc_type(doc)

    for field in self.fields:
      parse_func = self.parse_functions.get(field)
      
      parsed_doc[field] = parse_func(doc)

    return parsed_doc

  def determine_doc_type(self, doc):
    for path in self.available_parse_paths['path_determine_type']['paths']:
      try:
        data = doc

        for node in path:
          data = data[node]

        if node == 'PublicationTypeList':
          return data[0]
        
        return node
      except KeyError:
        continue

    return 'Other'


  def parse_abstract(self, abs_str):
    """Abstracts may contain multiple elements, convert to string and return joined string"""
    return ' '.join(abs_str).encode('utf-8')

  def format_ddate(self, ddate):
    """Turn a date dictionary into an ISO-type string (YYYY-MM-DD)."""
    year = ddate['Year']
    month = ddate['Month']
    day = ddate['Day']
    
    if not month.isdigit():
      month = self.months_rdict.get(month, None)
      
      if not month:
        return None

    return "%s-%s-%s" % (year, month.zfill(2), day.zfill(2))

  def extract_id_factory(self, idtype):
    """Extract an ID from Entrez XML output."""
    def extract_id(doc_data, key = 'PubmedData'):
      found = None

      try:
        for articleid in doc_data[key]['ArticleIdList']:
          if articleid.attributes['IdType'].lower() == idtype:
            found = str(articleid)
      except (KeyError):
        if key is 'PubmedData':
          return extract_id(doc_data, 'PubmedBookData')

      if found is None and 'path_' + idtype in self.available_parse_paths:
        found = self.extract_path_factory(idtype)(doc_data)

        if found is not None:
          found = found[0]

      return found
    
    return extract_id

  def extract_date_factory(self, datetype):
    def extract_date(doc_data, key = 'PubmedData'):
      try:
        for date in doc_data[key]['History']:
          if date.attributes['PubStatus'].lower() == datetype:
            return self.format_ddate(date)
      except (KeyError):
        if key is 'PubmedData':
          return extract_date(doc_data, 'PubmedBookData')
    
    return extract_date

  def extract_path_factory(self, field, rdict = None, fmt = None):
    def extract_path(doc_data):
      for path in self.available_parse_paths['path_' + field]['paths']:
        data = doc_data

        try:
          for node in path:
            data = data[node]

          if len(data) < 1:
            continue

          if rdict != None:
            data = rdict[data]

          if fmt != None:
            data = fmt(data)

          return data
        except (KeyError, TypeError):
          continue
          
      return None

    return extract_path

  def extract_keywords_factory(self):
    def extract_keywords(doc_data):
      for path in self.available_parse_paths['path_keywords']['paths']:
        try:
          data = doc_data

          for node in path:
            data = data[node]

          keywords = []
          
          try:
            for keyword in data[0]:
              keywords.append(str(keyword))
          except IndexError:
            return keywords

          return keywords
        except (KeyError, TypeError):
          continue

      return None

    return extract_keywords

  def add_extra_parse_functions(self, parse_functions):
    raise NotImplementedError
    # if parse_functions is None:
    #   return

    # for name, parse_function in parse_functions.items():
    #   self.parse_functions[name] = parse_function

  def build_parse_functions(self):
    self.parse_functions = {
      'pmid': self.extract_id_factory('pubmed'),
      'doi': self.extract_id_factory('doi'),

      'date_pubmed_published': self.extract_date_factory('pubmed'),
      'date_medline_published': self.extract_date_factory('medline'),

      'title': self.extract_path_factory('title'),
      'abstract': self.extract_path_factory('abstract', fmt = self.parse_abstract),
      'pub_year': self.extract_path_factory('pub_year'),
      'pub_month': self.extract_path_factory('pub_month', rdict = self.months_rdict),
      'pub_day': self.extract_path_factory('pub_day'),
      'vol': self.extract_path_factory('vol'),
      'pages': self.extract_path_factory('pages'),
      'date_pubmed_created': self.extract_path_factory('date_pubmed_created', fmt = self.format_ddate),
      'date_pubmed_updated': self.extract_path_factory('date_pubmed_updated', fmt = self.format_ddate),

      'journal_title': self.extract_path_factory('journal_title'),
      'journal_iso': self.extract_path_factory('journal_iso'),
      'journal_issn': self.extract_path_factory('journal_issn', fmt = str),

      'keywords': self.extract_keywords_factory()
    }