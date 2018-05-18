PmedConnect
-----------

Handles searches in both PubMed and PubMed Central (PMC).
Because the underlying Bio Entrez library does not support
parsing of PMC XML results. Fetching PMC documents yields
two calls, the first to retrieve PubMed IDs, and the second
to retrieve the documents from PubMed.

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