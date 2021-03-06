from comp62521.statistics import average
import itertools
import numpy as np
import xml.sax
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import validators

PublicationType = ["Conference Paper", "Journal", "Book", "Book Chapter"]


class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, link , year, authors, booktitle, journ, vol, pages, number, crossref, ee, isbn, series):
        self.pub_type = pub_type
        self.title = title
        self.link = link
        self.booktitle = booktitle
        self.journ = journ
        self.vol = vol
        self.pages = pages
        self.number = number
        self.crossref = crossref
        self.ee = ee
        self.isbn = isbn
        self.series = series
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors


class Author:
    def __init__(self, name):
        self.name = name


class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2


class Database:
    def __init__(self):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

    def read(self, filename):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        infile = open(filename, "r")
        valid = True
        try:
            parser.parse(infile)
        except xml.sax.SAXException as e:
            valid = False
            print("Error reading file (" + e.getMessage() + ")")
        infile.close()

        for p in self.publications:
            if self.min_year is None or p.year < self.min_year:
                self.min_year = p.year
            if self.max_year is None or p.year > self.max_year:
                self.max_year = p.year

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()

    def get_coauthor_data(self, start_year, end_year, pub_type):
        coauthors = {}
        for p in self.publications:
            if ((start_year is None or p.year >= start_year) and
                    (end_year is None or p.year <= end_year) and
                    (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])

        def display(db, coauthors, author_id):
            return f"{db.authors[author_id].name} {len(coauthors[author_id])}"

        header = ("Author", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([display(self, coauthors, a),
                         ", ".join([
                             display(self, coauthors, ca) for ca in coauthors[a]])])

        return header, data

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [func(auth_per_pub[i]) for i in np.arange(4)] + [func(list(itertools.chain(*auth_per_pub)))]
        return header, data

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [func(pub_per_auth[:, i]) for i in np.arange(4)] + [func(pub_per_auth.sum(axis=1))]
        return header, data

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper",
                  "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [func(ystats[:, i]) for i in np.arange(4)] + [func(ystats.sum(axis=1))]
        return header, data

    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper",
                  "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [[set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1)]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([[len(S) for S in y] for y in yauth])

        func = Stat.FUNC[av]

        data = [func(ystats[:, i]) for i in np.arange(5)]
        return header, data

    def get_publication_summary_average(self, av):
        header = ("Details", "Conference Paper",
                  "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
            + [func(auth_per_pub[i]) for i in np.arange(4)]
            + [func(list(itertools.chain(*auth_per_pub)))],
            [name + " publications per author"]
            + [func(pub_per_auth[:, i]) for i in np.arange(4)]
            + [func(pub_per_auth.sum(axis=1))]]
        return header, data

    def get_publication_summary(self):
        header = ("Details", "Conference Paper",
                  "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [len(a) for a in alist] + [len(ua)]]
        return header, data

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapers", "All publications")

        astats = [[[], [], [], []] for _ in range(len(self.authors))]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [[self.authors[i].name]
                + [func(L) for L in astats[i]]
                + [func(list(itertools.chain(*astats[i])))]
                for i in range(len(astats))]
        return header, data

    def get_publications_by_author(self):
        header = ("Author", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapers", "Total")

        astats = [[0, 0, 0, 0] for _ in range(len(self.authors))]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type] += 1

        data = [[self.authors[i].name] + astats[i] + [sum(astats[i])]
                for i in range(len(astats))]
        return header, data

    def get_author_firstlastsole(self):
        header = ("Author",
                  "First author",
                  "Last author",
                  "Sole author")

        astats = [ [0, 0, 0] for _ in range(len(self.authors)) ]

        for p in self.publications:
            if p.authors[0] == p.authors[-1]:
                astats[p.authors[0]][2] += 1
            else:
                astats[p.authors[0]][0] += 1
                astats[p.authors[-1]][1] += 1
        data = [[self.authors[i].name] + astats[i]
                for i in range(len(astats))]
        return header, data

    def get_author_stat(self, name):
        header = ("Author", "Number of all publications","Number of conference papers",
                  "Number of journals", "Number of book chapters", "Number of books",
                  "Number of co-authors", "First on a paper", "Last on a paper")
        astats=[0,0,0,0,0,0,0,0]
        for p in self.publications:
            for a in p.authors:
                if self.authors[a].name.lower() == name:
                    astats[0]+= 1
                    if p.pub_type == 0:
                        astats[1]+= 1
                    elif p.pub_type == 1:
                        astats[2]+= 1
                    elif p.pub_type == 2:
                        astats[4]+= 1
                    elif p.pub_type == 3:
                        astats[3]+= 1
                        
        
        astats[5] = len(self.get_coauthor_details_lowerCase(name)) - 1   
        

        h , d = self.get_author_firstlastsole()
        for i in d:
            if i[0].lower()== name:
                astats[6] = i[1]
                astats[7] = i[2]
        return header, astats

    def get_partial_match(self, authorName, allAuthors):
        matchScore = {}
        matched = []
        for i in allAuthors:
            matchScore[i] = fuzz.partial_ratio(authorName, i)
            if matchScore[i] == 100:
                matched.append(i)
        return len(matched), matched

    def get_all_author_names_lower(self):
        data = []
        for i in range(len(self.authors)):
            data += [self.authors[i].name.lower()]
        return data

    def get_all_authors_stat_by_year(self,year):
        header = ("Author", "Number of all publications","Number of conference papers",
                  "Number of journals", "Number of book chapters", "Number of books")
        astats = []
        data = []
        for i in range(len(self.authors)) :
            astats.append([self.authors[i].name, 0, 0, 0, 0 ,0 ]) 
        for p in self.publications:
                if p.year == year:
                    for a in p.authors:
                        for i in range(len(astats)):
                            if self.authors[a].name == astats[i][0]:
                                astats[i][1] += 1
                                if p.pub_type == 0:
                                    astats[i][2]+= 1
                                elif p.pub_type == 1:
                                    astats[i][3]+= 1
                                elif p.pub_type == 2:
                                    astats[i][5]+= 1
                                elif p.pub_type == 3:
                                    astats[i][4]+= 1          
                           
        return header, astats

    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year", "Conference papers",
                  "Journals", "Books",
                  "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [[y]
                + [func(L) for L in ystats[y]]
                + [func(list(itertools.chain(*ystats[y])))]
                for y in ystats]
        return header, data

    def get_publications_by_year(self):
        header = ("Year", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        data = [[y] + ystats[y] + [sum(ystats[y])] for y in ystats]
        return header, data

    def get_publications_for_year(self, year):
        oldHeader, data = self.get_publications_by_year()
        header = ("Number of all publications","Number of conference papers",
                  "Number of journals", "Number of book chapters", "Number of books")
        for i in data:
            if i[0] == year:
                return header, [i[5],i[1],i[2],i[4],i[3]]
 
        return header, [0,0,0,0,0]    

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year", "Conference papers",
                  "Journals", "Books",
                  "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [[y]
                + [func(ystats[y][:, i]) for i in np.arange(4)]
                + [func(ystats[y].sum(axis=1))]
                for y in ystats]
        return header, data

    def get_author_totals_by_year(self):
        header = ("Year", "Number of conference papers",
                  "Number of journals", "Number of books",
                  "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [[y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
                for y in ystats]
        return header, data


    def add_publication(self, pub_type, title, link , year, authors, booktitle, journ, vol, pages, number, crossref, ee, isbn, series):
        if year is None or len(authors) == 0:
            print("Warning: excluding publication due to missing information")
            print("    Publication type:", PublicationType[pub_type])
            print("    Title:", title)
            print("    Year:", year)
            print("    Authors:", ",".join(authors))
            return
        if title is None:
            print(f"Warning: adding publication with missing title "
                  f"[ {PublicationType[pub_type]} {year} ({','.join(authors)}) ]")
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, link, year, idlist, booktitle, journ, vol, pages, number, crossref, ee, isbn, series))
        if (len(self.publications) % 100000) == 0:
            print(
                f"Adding publication number {len(self.publications)} "
                f"(number of authors is {len(self.authors)})")

        if self.min_year is None or year < self.min_year:
            self.min_year = year
        if self.max_year is None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [(self.authors[key].name, data[key])
                for key in data]

    def get_coauthor_details_lowerCase(self, name):
        for a in range(len(self.author_idx)):
            keys_list = list(self.author_idx)
            if name == keys_list[a].lower():
                author_id = self.author_idx[keys_list[a]]
                data = self._get_collaborations(author_id, True)
                return [(self.authors[key].name, data[key])
                        for key in data]

    def get_network_data(self):
        na = len(self.authors)

        nodes = [[self.authors[i].name, -1] for i in range(na)]
        links = set()
        for a in range(na):
            collab = self._get_collaborations(a, False)
            nodes[a][1] = len(collab)
            for a2 in collab:
                if a < a2:
                    links.add((a, a2))
        return nodes, links
        
    def sort_result(self, input, searchedAuthorName):
        # authorName = ['Brian Sam Alice', 'Sam Alice', 'Samuel Alice', 'Alice Sam Brian',
        #               'Sam Brian', 'Samuel Brian', 'Alice Esam', 'Brian Esam', 'Alice Sam',
        #               'Brian Sam', 'Alice Sammer', 'Brian Sammer', 'Alice Samming',
        #               'Brian Samming', 'Mona Zaki']
        # searchedAuthorName = ['Brian Sam Alice', 'Sam Alice', 'Samuel Alice', 'Alice Sam Brian',
        #               'Sam Brian', 'Samuel Brian', 'Alice Esam', 'Brian Esam', 'Brian Sam',
        #               'Alice Sam', 'Alice Sammer', 'Brian Sammer', 'Alice Samming',
        #               'Brian Samming']
        # print(searchedAuthorName)
        searchValue = input
        searchValue = searchValue.lower()
        length = len(searchValue)
        sort1 = []
        for i in searchedAuthorName:
            if (i.split()[-1][0:length].lower() == searchValue):
                sort1.append(i)
        # print(sort1)
        sort1.sort(key=lambda x: (x.split()[0]))
        sort1.sort(key=lambda x: (x.split()[-1]))
        # print(sort1)
        for i in sort1:
            searchedAuthorName.remove(i)

        sort2 = []
        for i in searchedAuthorName:
            if (i.split()[0][0:length].lower() == searchValue):
                sort2.append(i)
        # print(sort2)
        sort2.sort(key=lambda x: (x.split()[-1]))
        sort2.sort(key=lambda x: (x.split()[0]))
        # print(sort2)
        for i in sort2:
            searchedAuthorName.remove(i)

        sort3 = []
        for i in searchedAuthorName:
            if (len(i.split()) == 3 and i.split()[1][0:length].lower() == searchValue):
                sort3.append(i)
        # print('3:')
        # print(sort3)
        sort3.sort(key=lambda x: (x.split()[0]))
        sort3.sort(key=lambda x: (x.split()[-1]))
        sort3.sort(key=lambda x: (x.split()[1]))
        # print(sort3)
        for i in sort3:
            searchedAuthorName.remove(i)

        # print(searchedAuthorName)
        sort4 = []
        for i in searchedAuthorName:
            if (searchValue in i.split()[-1].lower()):
                sort4.append(i)
        # print('4:')
        # print(sort4)
        sort4.sort(key=lambda x: (x.split()[0]))
        sort4.sort(key=lambda x: (x.split()[-1]))
        # print(sort4)
        for i in sort4:
            searchedAuthorName.remove(i)

        searchedAuthorName.sort(key=lambda x: x.split()[0])
        searchedAuthorName.sort(key=lambda x: x.split()[-1])

        res = sort1 + sort2 + sort3 + sort4 + searchedAuthorName
        return (res)

    def get_author_details(self, start_year, end_year, pub_type):
        header = ("Author",
                  "First author",
                  "Last author",
                  "Sole author")

        astats = [ [0, 0, 0] for _ in range(len(self.authors)) ]

        for p in self.publications:
            if ( (start_year == None or p.year >= start_year) and
                (end_year == None or p.year <= end_year) and
                (pub_type == 4 or pub_type == p.pub_type) ):
                    if p.authors[0] == p.authors[-1]:
                        astats[p.authors[0]][2] += 1
                    else:
                        astats[p.authors[0]][0] += 1
                        astats[p.authors[-1]][1] += 1
        data = [[self.authors[i].name] + astats[i]
                for i in range(len(astats))]
        return header, data

    def get_cs_staff(self):
        with open('data/CS-staff.txt') as f:
            staff = list()
            Lines = f.readlines()
            converted_Lines = []
            for line in Lines:
                if line:
                    converted_Lines.append(line.strip())
            return converted_Lines

    def get_author_stats_by_click(self,author):
        coauthors = {}
        author_name = ''
        author_found = False
        NoPublications = [0, 0, 0, 0, 0]
        NoFirstAuthor = [0, 0, 0, 0, 0]
        NoLastAuthor = [0, 0, 0, 0, 0]
        NoSoleAuthor = [0, 0, 0, 0, 0]
        NoCoAuthor = 0
        isInternal = 0
        AuthorType = 'External'
        ExCoAuthorsList = []
        NoExCoAuthors = 0
        internal_staff = self.get_cs_staff()

        if author in internal_staff:
            isInternal = 1
            AuthorType = 'Internal'

        for p in self.publications:
            for a in p.authors:
                if str(self.authors[a].name) == author:
                    author_found = True
                    author_name = self.authors[a].name
                    NoPublications[p.pub_type + 1] += 1
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
                    try:
                        NoCoAuthor = len(coauthors[a])
                    except:
                        NoCoAuthor = 0

                    if a == p.authors[0] and len(p.authors) > 1:
                        NoFirstAuthor[p.pub_type + 1] += 1
                    if a == p.authors[-1] and len(p.authors) > 1:
                        NoLastAuthor[p.pub_type + 1] += 1
                    if len(p.authors) == 1 and (a == p.authors[0]):
                        NoSoleAuthor[p.pub_type + 1] += 1

                    NoPublications[0] = NoPublications[1] + NoPublications[2] + NoPublications[3] + NoPublications[4]
                    NoFirstAuthor[0] = NoFirstAuthor[1] + NoFirstAuthor[2] + NoFirstAuthor[3] + NoFirstAuthor[4]
                    NoLastAuthor[0] = NoLastAuthor[1] + NoLastAuthor[2] + NoLastAuthor[3] + NoLastAuthor[4]
                    NoSoleAuthor[0] = NoSoleAuthor[1] + NoSoleAuthor[2] + NoSoleAuthor[3] + NoSoleAuthor[4]

                    if isInternal == 1:
                        for b in p.authors:
                            bname = self.authors[b].name
                            if bname not in internal_staff and bname not in ExCoAuthorsList:
                                ExCoAuthorsList.append(bname)
                                NoExCoAuthors += 1

        return author_found, NoPublications, NoFirstAuthor, NoLastAuthor, NoSoleAuthor, NoCoAuthor, AuthorType,  ", ".join(ExCoAuthorsList), NoExCoAuthors, author_name


    def get_all_publications(self):
        header = ('Title', 'Authors', 'Year', 'Book title', 'Journal', 'Volume', 'Pages', 'Number', 'Cross reference', 'Url', 'ISBN', 'Series')
        all_publications = []
        
        for p in self.publications:
            link_valid = validators.url(str(p.link))
            authors_list = []

            booktitle = '-' if p.booktitle == None else p.booktitle
            jn = '-' if p.journ == None else p.journ
            vol = '-' if p.vol == None else p.vol
            pages = '-' if p.pages == None else p.pages
            number = '-' if p.number == None else p.number
            crossref = '-' if p.crossref == None else p.crossref
            ee = '-' if p.ee == None else p.ee
            isbn = '-' if p.isbn == None else p.isbn
            series = '-' if p.series == None else p.series

            if link_valid:
                authors_list = ', '.join([self.authors[i].name for i in p.authors])
                all_publications.append([p.title, p.link, authors_list, p.year, booktitle, jn, vol, pages, number, crossref, ee, isbn, series])
                
        return header, all_publications


class DocumentHandler(xml.sax.handler.ContentHandler):
    TITLE_TAGS = ["sub", "sup", "i", "tt", "ref"]
    PUB_TYPE = {
        "inproceedings": Publication.CONFERENCE_PAPER,
        "article": Publication.JOURNAL,
        "book": Publication.BOOK,
        "incollection": Publication.BOOK_CHAPTER}

    def __init__(self, db):
        super().__init__()
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None
        self.link = None
        self.booktitle = None
        self.journ = None
        self.vol = None
        self.pages = None
        self.number = None
        self.crossref = None
        self.ee = None
        self.isbn = None
        self.series = None

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None
        self.link = None
        self.booktitle = None
        self.journ = None
        self.vol = None
        self.number = None
        self.crossref = None
        self.ee = None
        self.isbn = None
        self.series = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type is None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(d)
        elif self.tag == "title":
            self.title = d
        elif self.tag == "ee":
            self.link = d
        elif self.tag == "year":
            self.year = int(d)
        elif self.tag == "booktitle":
            self.booktitle = d
        elif self.tag == "journal":
            self.journ = d
        elif self.tag == "volume":
            self.vol = d
        elif self.tag == "pages":
            self.pages = d
        elif self.tag == "number":
            self.number = d
        elif self.tag == "crossref":
            self.crossref = d
        elif self.tag == "url":
            self.ee = d
        elif self.tag == "isbn":
            self.isbn = d
        elif self.tag == "series":
            self.series = d
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.link,
                self.year,
                self.authors,
                self.booktitle,
                self.journ,
                self.vol,
                self.pages,
                self.number,
                self.crossref,
                self.ee,
                self.isbn,
                self.series
                )
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type is not None:
            self.chrs += chrs
