PmedConnect
-----------

To use search::

    >>> from PmedConnect import PubmedAPI as api
    >>> connector = api.PubmedAPI('your@email.com')
    >>> search = connector.search('Influenza')
    >>> print(search['pmids'])

Search supports the regular PubMed query language.

To fetch (needs a list of PubMed IDs)::

		>>> from PmedConnect import PubmedAPI as api
    >>> connector = api.PubmedAPI('your@email.com')
		>>> documents = connector.fetch(search['pmids'])
    >>> print(documents)