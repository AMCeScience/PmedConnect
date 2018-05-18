from xml.dom import minidom

class ReadPMC(object):
  dom_data = None

  def read_xml(self, xml):
    self.dom_data = minidom.parse(xml)

  def get_pmids(self, xml):
    self.read_xml(xml)

    pmid_list = []

    # Iterate the documents
    for doc in self.dom_data.getElementsByTagName('article'):
      # Retrieve the pmids
      pmid_list.append(self.get_pmid(doc))

    cleaned_pmid_list = list(filter(None.__ne__, pmid_list))

    list_len = len(pmid_list)
    clean_len = len(cleaned_pmid_list)

    if list_len - clean_len > 0:
      print('Removed %i items from the list because no pubmed id could be retrieved.' % (list_len - clean_len))

    return cleaned_pmid_list

  def get_pmid(self, article):
    for item in article.getElementsByTagName('article-id'):
      if item.attributes['pub-id-type'].value == 'pmid':
        # if item.firstChild.nodeValue is None:
        #   article.toprettyxml()

        return item.firstChild.nodeValue