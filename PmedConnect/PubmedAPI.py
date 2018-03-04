import PmedConnect.config as config, PmedConnect.ParseFunctions as xpf
import math, xml.dom.minidom, progressbar, time

from datetime import date
from Bio import Entrez

class PubmedAPI(object):
  """Searches and fetches data from Pubmed using the Entrez module from Biopython."""

  search_progressbar_obj = None

  mindate = None
  maxdate = None
  
  retall = True
  retnum = config.RESULTS_PER_SEARCH_REQUEST
  retmax = config.RESULTS_PER_SEARCH_REQUEST
  
  # Summary variables, used to print at the end of a search
  total_results = 0
  found_results = 0
  query = ''
  interpreted_query = ''
  rounds_made = 0

  # Constants
  retmode = 'xml'
  datetype = 'pdat'
  fetch_block = config.RESULTS_PER_FETCH_REQUEST

  def __init__(self, email, fields = None):
    #Entrez requires an email address.
    Entrez.email = email

    self.parser = xpf.Parser(fields)

  def set_search_date(self, mindate, maxdate = None):
    """Restricts searches to the specified date range (format as YYYY/MM/DD, YYYY/MM, or YYYY)"""

    if maxdate == None:
      today = date.fromtimestamp(time.time())

      maxdate = today.strftime('%Y/%m/%d')

    self.mindate = mindate
    self.maxdate = maxdate

  def reset_search_data(self):
    self.mindate = None
    self.maxdate = None

  def set_retrieve_params(self, num_retrieve, num_retrieve_per_round):
    """Set the number of items to retrieve from the Entrez API each search call.
    If the number of retrieved items in a search does not satisfy the limit
    AND there are more items to retrieve from the API, the search will
    iterate using retstart."""
    self.retall = True
    self.retmax = config.RESULTS_PER_SEARCH_REQUEST

    # Check whether num_retrieve_per_round is provided
    if num_retrieve_per_round is not None:
      # Check against the Entrez API limits
      if num_retrieve_per_round > config.ENTREZ_MAX_RETRIEVE:
        raise ValueError('Number of items to retrieve lies outside the maximum of the Entrez API')

      self.retmax = num_retrieve_per_round

    # Check whether num_retrieve is provided
    if num_retrieve is not None:
      self.retall = False
      self.retnum = num_retrieve

      # Adjust the maximum number of items to retrieve per search.
      # If the nubmer to retrieve is lower than the current maximum
      # number of results per request, set the retmax to num_retrieve.
      if num_retrieve < self.retmax:
        self.retmax = num_retrieve

  def check_search_error(self, search_results):
    """Checks whether the search results contain an error, in which case an exception is raised"""
    if 'WarningList' in search_results:
      raise Exception('Entrez error: ' + '; '.join(search_results['WarningList']['OutputMessage']))

  def update_search_summary(self, search_results, num_ids):
    self.total_results = int(search_results['Count'])
    self.found_results = num_ids
    self.interpreted_query = search_results['QueryTranslation']
    self.rounds_made = self.rounds_made + 1

  def attach_search_summary(self, pmids):
    return {
      'pmids': pmids,
      'summary': {
        'translated_query': self.interpreted_query,
        'total_found': self.total_results,
        'retrieved': self.found_results,
        'rounds_made': self.rounds_made,
      }
    }

  def update_search_progressbar(self, initialise, max_results, current_results):
    """Initialises and updates the progressbar during searches"""
    if initialise == 0:
      bar_max = self.retnum

      if self.retnum == 0 or self.retnum > max_results:
        bar_max = max_results

      self.search_progressbar_obj = progressbar.ProgressBar(max_value = bar_max)
      
    self.search_progressbar_obj.update(current_results)

  def get_search_params(self, query, retstart):
    """Creates a dictionary of parameters to pass into the Entrez.esearch function"""
    func_params = dict(db = 'pubmed', term = query, retmode = self.retmode, retstart = retstart, retmax = self.retmax)

    if self.mindate is not None:
      func_params['datetype'] = self.datetype
      func_params['mindate'] = self.mindate
      func_params['maxdate'] = self.maxdate

    return func_params

  def get_search_total_count(self, results):
    """Returns the total number of results for the search"""
    self.check_search_error(results)

    return int(results['Count'])

  def get_search_result_ids(self, existing_ids, results):
    """Extracts the PMID list from the search results, cuts the list
    of IDs if it is bigger than the maximum number of results to
    return (i.e. self.retnum)"""
    self.check_search_error(results)

    ids = existing_ids + results['IdList']

    # Cut IDs to size of maximum to retrieve
    if len(ids) > self.retnum:
      ids = ids[0:self.retnum]

    return ids

  def search_round(self, query, retstart = 0, found_ids = []):
    """Searches for the provided parameters, iteratively calls itself
    if there are more results to retrieve."""
    search_params = self.get_search_params(query, retstart)
    search_results = Entrez.read(Entrez.esearch(**search_params))

    total_count = self.get_search_total_count(search_results)
    found_ids = self.get_search_result_ids(found_ids, search_results)

    self.update_search_progressbar(retstart, total_count, len(found_ids))

    # Check for empty searches
    if len(found_ids) == 0 or total_count == 0:
      return found_ids
    
    # Check if another search is possible and/or necessary
    if (self.retall == True or len(found_ids) < self.retnum) and total_count > retstart:
      retstart = retstart + self.retmax

      found_ids = self.search_round(query, retstart, found_ids)

    self.update_search_summary(search_results, len(found_ids))

    return found_ids

  def search(self, query, num_retrieve = None, num_retrieve_per_round = None):
    """Uses the esearch function to search in the Entrez API"""
    self.set_retrieve_params(num_retrieve, num_retrieve_per_round)

    pmids = self.search_round(query)
    
    return self.attach_search_summary(pmids)

  def fetch_round(self, pmids):
    """Fetch and parse the XML for a list of PMIDs."""
    func_params = dict(db = 'pubmed', id = pmids, retmode = self.retmode)
    
    fetch_results = Entrez.read(Entrez.efetch(**func_params))

    return fetch_results['PubmedArticle']

  def fetch(self, pmid):
    """Breaks Entrez fetching process into blocks,
    fetches documents in chunks of fetch_block."""
    number_of_rounds = int(math.floor(len(pmid) / self.fetch_block + (len(pmid) % self.fetch_block > 0)))
    
    doc_list = []

    if number_of_rounds > 1:
      print('Will fetch in %i rounds with %i articles per round.' % (number_of_rounds, self.fetch_block))

      for i in range(number_of_rounds):
        start = i * self.fetch_block
        finish = (i + 1) * self.fetch_block

        self.update_search_progressbar(i, number_of_rounds * self.fetch_block, start)
                 
        doc_list = doc_list + self.fetch_round(pmid[start:finish])
    else:
      print('Will fetch %i articles.' % len(pmid))

      doc_list = self.fetch_round(pmid)
    
    return self.parser.extract_from_docs(doc_list)