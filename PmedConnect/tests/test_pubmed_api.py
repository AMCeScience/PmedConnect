from unittest import TestCase

import os
from unittest.mock import patch
from unittest.mock import Mock
import PmedConnect.PubmedAPI as pf
import PmedConnect.config as config
from Bio import Entrez

class TestPubmedAPI(TestCase): 

  def setUp(self):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(__location__ + '/fetch_output.xml', 'r') as xml:
      fetch_obj = Entrez.read(xml)

    with open(__location__ + '/search_output.xml', 'r') as xml:
      search_obj = Entrez.read(xml)

    self.extracted_docs = {
      'pmid': '00000001',
      'doi': None,
      'title': 'Test Title.'
    }

    def search_result(*args, **kwargs):
      # dict(db = 'pubmed', term = query, retmode = self.retmode, retstart = retstart, retmax = self.retmax)
      return_obj = search_obj

      return_obj['IdList'] = []

      return_obj['RetMax'] = kwargs['retmax']
      return_obj['RetStart'] = kwargs['retstart']

      print(kwargs['retmax'])
      if kwargs['retmax'] is 1:
        return_obj['IdList'].append(str(1).zfill(8))
      else:
        for i in range(kwargs['retmax']):
          return_obj['IdList'].append(str(i).zfill(8))

      return return_obj

    def fetch_result(*args, **kwargs):
      data_el = fetch_obj['PubmedArticle']
      
      return_obj = {'PubmedArticle': []}

      for i in range(len(kwargs['id'])):
        return_obj['PubmedArticle'].append(data_el)
      
      return return_obj

    def pass_through(*args):
      return args[0]

    patches = {
      'PmedConnect.PubmedAPI.Entrez.esearch': Mock(side_effect = search_result),
      'PmedConnect.PubmedAPI.Entrez.efetch': Mock(side_effect = fetch_result),
      'PmedConnect.PubmedAPI.Entrez.read': Mock(side_effect = pass_through),
      'PmedConnect.ParseFunctions.Parser.extract_fields': Mock(return_value = self.extracted_docs),
      'PmedConnect.PubmedAPI.progressbar': Mock(side_effect = pass_through),
      'PmedConnect.PubmedAPI.progressbar.update': Mock(return_value = ''),
    }

    # for item in config.AVAILABLE_FIELDS:
    #   patches['PmedConnect.ParseFunctions.' + item] = Mock(return_value = 'Test_value_' + item)

    applied_patches = [patch(patch_name, data) for patch_name, data in patches.items()]

    [self.addCleanup(patch_name.stop) for patch_name in applied_patches]
    [patch_name.start() for patch_name in applied_patches]

  def test_set_email(self):
    with self.assertRaises(TypeError):
      api = pf.PubmedAPI()

  def test_fetch(self):
    api = pf.PubmedAPI('test@test.com')

    id_list = [1]

    docs = api.fetch(id_list)

    self.assertEqual(len(docs), 1)
    self.assertEqual(docs, [self.extracted_docs])

  def test_fetch_multiple(self):
    api = pf.PubmedAPI('test@test.com')

    id_list = [1,2]

    docs = api.fetch(id_list)

    self.assertEqual(len(docs), 2)
    self.assertEqual(docs, [self.extracted_docs, self.extracted_docs])

  def test_fetch_looping(self):
    api = pf.PubmedAPI('test@test.com')

    id_list = range(1000)

    docs = api.fetch(id_list)

    self.assertEqual(len(docs), 1000)

  def test_search(self):
    api = pf.PubmedAPI('test@test.com')

    query = 'Testable Query'

    docs = api.search(query, num_retrieve = 1)

    self.assertEqual(len(docs['pmids']), 1)
    self.assertEqual(docs['summary']['translated_query'], 'Testable[All Fields] AND Query[All Fields]')
    self.assertEqual(docs['summary']['total_found'], 500000)
    self.assertEqual(docs['summary']['retrieved'], 1)
    self.assertEqual(docs['summary']['rounds_made'], 1)

  def test_search_multiple(self):
    api = pf.PubmedAPI('test@test.com')

    query = 'Testable Query'

    docs = api.search(query, num_retrieve = 10)

    self.assertEqual(len(docs['pmids']), 10)
    self.assertEqual(docs['summary']['translated_query'], 'Testable[All Fields] AND Query[All Fields]')
    self.assertEqual(docs['summary']['total_found'], 500000)
    self.assertEqual(docs['summary']['retrieved'], 10)
    self.assertEqual(docs['summary']['rounds_made'], 1)

  def test_search_looping(self):
    api = pf.PubmedAPI('test@test.com')

    query = 'Testable Query'

    docs = api.search(query, num_retrieve = 1000)

    self.assertEqual(len(docs['pmids']), 1000)
    self.assertEqual(docs['summary']['translated_query'], 'Testable[All Fields] AND Query[All Fields]')
    self.assertEqual(docs['summary']['total_found'], 500000)
    self.assertEqual(docs['summary']['retrieved'], 1000)
    self.assertEqual(docs['summary']['rounds_made'], 1)

  def test_search_max_blocking(self):
    api = pf.PubmedAPI('test@test.com')

    query = 'Testable Query'

    docs = api.search(query, num_retrieve = 1000, num_retrieve_per_round = 101)
    
    self.assertEqual(len(docs['pmids']), 1000)
    self.assertEqual(docs['summary']['translated_query'], 'Testable[All Fields] AND Query[All Fields]')
    self.assertEqual(docs['summary']['total_found'], 500000)
    self.assertEqual(docs['summary']['retrieved'], 1000)
    self.assertEqual(docs['summary']['rounds_made'], 10)

  def test_search_overload(self):
    api = pf.PubmedAPI('test@test.com')

    query = 'Testable Query'

    with self.assertRaises(ValueError):
      docs = api.search(query, num_retrieve_per_round = 1000000)