class MockDatabase:
    def read(self, filename):
        pass

    def get_publication_summary(self):
        return (('Details', 'Conference Paper', 'Journal', 'Book', 'Book Chapter', 'Total'),
                [('Number of publications', 10, 5, 8, 2, 25), ('Number of authors', 20, 15, 18, 12, 35)])

    # Return tuple containing headers and list of data
        def get_publications_by_author(self):
        return ('Author', 'Number of conference papers', 'Number of journals', 'Number of books',
                'Number of book chapters', 'Total'), \
               [('Author E', 1, 2, 3, 4, 10),
                ('Author C', 5, 6, 7, 8, 26),
                ('Author D', 3, 5, 2, 6, 21),
                ('Author B', 3, 3, 4, 5, 23),
                ('Author A', 3, 5, 7, 4, 10)]

    # Return tuple containing headers and list of data
    def get_publications_by_year(self):
        return ('Year', 'Number of conference papers', 'Number of journals', 'Number of books',
                'Number of book chapters'), [(2002, 100, 50, 25, 10), (2004, 99, 49, 24, 9)]

    # Return tuple containing headers and list of data
    def get_author_totals_by_year(self):
        return ('Year', 'Number of conference papers', 'Number of journals', 'Number of books',
                'Number of book chapters'), [(2001, 10, 5, 6, 3), (2003, 12, 7, 4, 2)]

    # Return a list in the format:
    # [ [author, total], ... ]
    # where author is the author name
    # and total is the number of publications
    # the publications used will only include items where
    # the give name was an author
    def get_coauthor_details(self, name):
        return [('foo', 1), ('bar', 2), ('baz', 3)]
