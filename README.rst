PmedConnect
-----------

To use search::

    >>> import pmedconnect
    >>> pubmed_ids = pmedconnect.search('Influenza')

To fetch (needs a list of PubMed IDs)::

		>>> import pmedconnect
		>>> documents = pmedconnect.fetch(pubmed_ids)