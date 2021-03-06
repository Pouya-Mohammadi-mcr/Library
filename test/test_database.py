from os import path
import unittest

from comp62521.database import database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        directory, _ = path.split(__file__)
        self.data_dir = path.join(directory, "..", "data")

    def test_read(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        self.assertEqual(len(db.publications), 1)

    def test_read_invalid_xml(self):
        db = database.Database()
        self.assertFalse(
            db.read(path.join(self.data_dir, "invalid_xml_file.xml")))

    def test_read_missing_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_year.xml")))
        self.assertEqual(len(db.publications), 0)

    def test_read_missing_title(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_title.xml")))
        # publications with missing titles should be added
        self.assertEqual(len(db.publications), 1)

    def test_get_average_authors_per_publication(self):
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        _, data = db.get_average_authors_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.8, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [0, 2, 4, 5])
        # additional test for union of authors
        self.assertEqual(data[-1], [0, 2, 4, 5])

    def test_get_publication_summary(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publication_summary()
        self.assertEqual(len(header), len(
            data[0]), "header and data column size doesn't match")
        self.assertEqual(
            len(data[0]), 6, "incorrect number of columns in data")
        self.assertEqual(len(data), 2, "incorrect number of rows in data")
        self.assertEqual(
            data[0][1], 1, "incorrect number of publications for conference papers")
        self.assertEqual(
            data[1][1], 2, "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "three-authors-and-three-publications.xml")))
        header, data = db.get_average_authors_per_publication_by_author(
            database.Stat.MEAN)
        self.assertEqual(len(header), len(
            data[0]), "header and data column size doesn't match")
        self.assertEqual(
            len(data), 3, "incorrect average of number of conference papers")
        self.assertEqual(
            data[0][1], 1.5, "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2, "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1, "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header), len(
            data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 2, "incorrect number of authors")
        self.assertEqual(data[0][-1], 1, "incorrect total")

    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_average_publications_per_author_by_year(
            database.Stat.MEAN)
        self.assertEqual(len(header), len(
            data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(
            data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header), len(
            data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")
        self.assertEqual(
            data[0][1], 2, "incorrect number of authors in result")

    def test_get_coauthor_data(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "three-authors-and-three-publications.xml")))
        header, data = db.get_coauthor_data(None, None, 4)
        self.assertEqual(len(data), 2, "incorrect number of rows")
        self.assertEqual(data[0][0], "author1 1")
        self.assertEqual(data[0][1], "author2 1")
        self.assertEqual(data[1][0], "author2 1")
        self.assertEqual(data[1][1], "author1 1")

    def test_get_publication_summary_average(self):
        MEANAPP = ['Mean authors per publication', 2.0, 0, 1.0, 0, 1.75]
        MEANPPA = ['Mean publications per author', 1.5, 0.0, 0.25, 0.0, 1.75]
        MEDAPP = ['Median authors per publication', 2, 0, 1, 0, 1.5]
        MEDPPA = ['Median publications per author', 1.5, 0.0, 0.0, 0.0, 1.5]
        MODEAPP = ['Mode authors per publication', [1, 2, 3], [], [1], [], [1]]
        MODEPPA = ['Mode publications per author', [
            0.0, 1.0, 2.0, 3.0], [0.0], [0.0], [0.0], [1.0]]
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_publication_summary_average(database.Stat.MEAN)
        self.assertEqual(data[0], MEANAPP)
        self.assertEqual(data[1], MEANPPA)
        _, data = db.get_publication_summary_average(database.Stat.MEDIAN)
        self.assertEqual(data[0], MEDAPP)
        self.assertEqual(data[1], MEDPPA)
        _, data = db.get_publication_summary_average(database.Stat.MODE)
        self.assertEqual(data[0], MODEAPP)
        self.assertEqual(data[1], MODEPPA)

    def test_get_average_authors_per_publication_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        header, data = db.get_average_authors_per_publication_by_year(
            database.Stat.MEAN)
        self.assertEqual(len(header), len(
            data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of years")
        self.assertEqual(
            data[0][1], 2.0, "incorrect mean authors per conference paper for year1")
        self.assertEqual(
            data[0][2], 0, "incorrect mean authors per journal for year1")
        self.assertEqual(
            data[0][3], 1.0, "incorrect mean authors per book for year1")
        self.assertEqual(
            data[0][4], 0, "incorrect mean authors per book chapter for year1")
        self.assertEqual(
            data[0][5], 1.75, "incorrect mean authors per publication for year1")

    def test_get_collaborations(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        data = db._get_collaborations(0, 1)
        self.assertEqual(data[0], 3, "wrong number of publications")
        self.assertEqual(
            data[1], 1, "wrong count of collaboration with author3")
        self.assertEqual(
            data[2], 2, "wrong count of collaboration with author4")

    def test_get_coauthor_details(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        data = db.get_coauthor_details("AUTHOR1")
        self.assertEqual(data[0][0], "AUTHOR1", "wrong name for author")
        self.assertEqual(data[0][1], 3, "wrong number of publications")
        self.assertEqual(data[1][0], "AUTHOR3", "wrong name for coauthor")
        self.assertEqual(
            data[1][1], 1, "wrong count of collaboration with author3")
        self.assertEqual(data[2][0], "AUTHOR4", "wrong name for author")
        self.assertEqual(
            data[2][1], 2, "wrong count of collaboration with author4")

    def test_all_authors(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))

    def test_get_network_data(self):
        nodes = [['AUTHOR1', 2], ['AUTHOR3', 2],
                 ['AUTHOR4', 2], ['AUTHOR2', 0]]
        links = {(0, 1), (0, 2), (1, 2)}
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        data = db.get_network_data()
        self.assertEqual(data[0][0][0], "AUTHOR1", "wrong name for author")
        self.assertEqual(data[0][0][1], 2,
                         "wrong number of authors in AUTHOR1's network")
        self.assertEqual(data[0], nodes, "wrong nodes details")
        self.assertEqual(data[1], links, "wrong links details")

    def test_get_author_firstlastsole(self):
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR1', 1, 1, 0], ['AUTHOR2', 0, 1, 0], [
                         'AUTHOR3', 0, 1, 0], ['AUTHOR4', 2, 0, 0]])
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR1', 2, 0, 1], ['AUTHOR3', 0, 0, 0], [
                         'AUTHOR4', 0, 2, 0], ['AUTHOR2', 0, 0, 1]])
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR', 0, 0, 9], ['AUTHOR1', 0, 0, 1]])
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR1', 1, 0, 2], ['AUTHOR2', 0, 1, 0], ['AUTHOR3', 2, 1, 0], ['AUTHOR4', 0, 2, 0],
                                ['AUTHOR6', 1, 0, 0], ['AUTHOR7', 0, 0, 1], ['AUTHOR8', 0, 0, 2]])

    def test_get_author_details(self):
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        header, data = db.get_author_details(9999, 9999, 0)
        self.assertEqual(data, [['AUTHOR1', 1, 1, 0], ['AUTHOR2', 0, 1, 0], [
                         'AUTHOR3', 0, 1, 0], ['AUTHOR4', 2, 0, 0]])
        header, data = db.get_author_details(9999, 9999, 1)
        self.assertEqual(data, [['AUTHOR1', 0, 0, 0], ['AUTHOR2', 0, 0, 0], [
                         'AUTHOR3', 0, 0, 0], ['AUTHOR4', 0, 0, 0]])
        self.assertTrue(
            db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        header, data = db.get_author_details(9999, 9999, 0)
        self.assertEqual(data, [['AUTHOR1', 2, 0, 1], ['AUTHOR3', 0, 0, 0], [
                         'AUTHOR4', 0, 2, 0], ['AUTHOR2', 0, 0, 0]])
        header, data = db.get_author_details(9999, 9999, 1)
        self.assertEqual(data, [['AUTHOR1', 0, 0, 0], ['AUTHOR3', 0, 0, 0], [
                         'AUTHOR4', 0, 0, 0], ['AUTHOR2', 0, 0, 0]])
        header, data = db.get_author_details(9999, 9999, 2)
        self.assertEqual(data, [['AUTHOR1', 0, 0, 0], ['AUTHOR3', 0, 0, 0], [
                         'AUTHOR4', 0, 0, 0], ['AUTHOR2', 0, 0, 1]])
        header, data = db.get_author_details(9999, 9999, 3)
        self.assertEqual(data, [['AUTHOR1', 0, 0, 0], ['AUTHOR3', 0, 0, 0], [
                         'AUTHOR4', 0, 0, 0], ['AUTHOR2', 0, 0, 0]])

    def test_get_author_stat(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        header, data = db.get_author_stat("author3")
        self.assertEqual(data, [1, 1, 0, 0, 0, 2, 0, 0])
        header, data = db.get_author_stat("author1")
        self.assertEqual(data, [3, 3, 0, 0, 0, 2, 2, 0])
        header, data = db.get_author_stat("author2")
        self.assertEqual(data, [1, 0, 0, 0, 1, 0, 0, 0])
        header, data = db.get_author_stat("author4")
        self.assertEqual(data, [2, 2, 0, 0, 0, 2, 0, 2])
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "dblp_curated_sample.xml")))
        header, data = db.get_author_stat("carlo batini")
        self.assertEqual(data, [10, 6, 3, 0, 1, 15, 3, 5])

        self.assertTrue(db.read(path.join(self.data_dir,
                                          "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_author_stat("anhai doan")
        self.assertEqual(data, [14, 6, 7, 1, 0, 11, 10, 0])

    def test_get_all_author_names_lower(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        data = db.get_all_author_names_lower()
        self.assertEqual(data, ['author1', 'author3', 'author4', 'author2'])

    def test_get_coauthor_details_lowerCase(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "dblp_curated_sample.xml")))
        self.assertEqual(db.get_coauthor_details_lowerCase("andrew brown"),
                         (db.get_coauthor_details("Andrew Brown")))

    def test_get_partial_match(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "dblp_curated_sample.xml")))
        allAuthors = db.get_all_author_names_lower()
        matchedNum, matched = db.get_partial_match("andrew", allAuthors)
        self.assertEqual(matchedNum, 9)
        self.assertEqual(matched, ['andrew dinn', 'andrew hayes', 'andrew c. jones', 'andrew gibson',
                                   'andrew r. jones', 'andrew borley', 'andrew eisenberg', 'andrew fikes', 'andrew brown'])

        matchedNum, matched = db.get_partial_match("cornell", allAuthors)
        self.assertEqual(matchedNum, 1)
        self.assertEqual(matched, ['mike cornell'])
    def test_sort_result(self):
        db = database.Database()
        searchedAuthorName = ['Brian Sam Alice', 'Sam Alice', 'Samuel Alice', 'Alice Sam Brian',
                              'Sam Brian', 'Samuel Brian', 'Alice Esam', 'Brian Esam', 'Brian Sam',
                              'Alice Sam', 'Alice Sammer', 'Brian Sammer', 'Alice Samming',
                              'Brian Samming']
        input = 'Sam'
        res = db.sort_result("Sam", searchedAuthorName)
        self.assertEqual(res, ['Alice Sam', 'Brian Sam', 'Alice Sammer', 'Brian Sammer', 'Alice Samming', 'Brian Samming', 'Sam Alice',
                               'Sam Brian', 'Samuel Alice', 'Samuel Brian', 'Brian Sam Alice', 'Alice Sam Brian', 'Alice Esam', 'Brian Esam'])

    def test_get_cs_staff(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        data = db.get_cs_staff()
        self.assertEqual(data, ["Sean Bechhofer", "Andy Brass", "Suzanne M. Embury", "Carole A. Goble", "Robert Haines", "Simon Harper",
                                "Duncan Hull", "Caroline Jay", "John A. Keane", "Goran Nenadic", "Bijan Parsia", "Norman W. Paton",
                                "Steve Pettifer", "Rizos Sakellariou", "Sandra Sampaio", "Uli Sattler", "Robert Stevens", "Chris Taylor",
                                "Markel Vigo", "Ning Zhang"])
    def test_get_author_stats_by_click(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        data = db.get_author_stats_by_click("Bijan Parsia")
        self.assertEqual(data, (True, [2, 2, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 8, "Internal",
                                'Patrice Seyed, Alan L. Rector, Klitos Christodoulou, Alvaro A. A. Fernandes, Cornelia Hedeler',
                                5, "Bijan Parsia"))
        data = db.get_author_stats_by_click("Markel Vigo")
        self.assertEqual(data, (True, [1, 1, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 3, "Internal",
                                'Yeliz Yesilada, Giorgio Brajnik', 2, "Markel Vigo"))
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        data = db.get_author_stats_by_click("AUTHOR1")
        self.assertEqual(data, (True, [3, 3, 0, 0, 0], [2, 2, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 0, 0, 0], 2, "External", '', 0, "AUTHOR1"))
        data = db.get_author_stats_by_click("AUTHOR2")
        self.assertEqual(data, (True, [1, 0, 0, 1, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 0, 0, 1, 0], 0, "External", '', 0, "AUTHOR2"))
        data = db.get_author_stats_by_click("AUTHOR3")
        self.assertEqual(data, (True, [1, 1, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 2, "External", '', 0, "AUTHOR3"))
        data = db.get_author_stats_by_click("AUTHOR4")
        self.assertEqual(data, (True, [2, 2, 0, 0, 0], [0, 0, 0, 0, 0], [2, 2, 0, 0, 0], [0, 0, 0, 0, 0], 2, "External", '', 0, "AUTHOR4"))

    
    def test_get_all_authors_stat_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_all_authors_stat_by_year(9999)
        self.assertEqual(data, ([["AUTHOR1", 1, 1, 0, 0, 0], ["AUTHOR2", 1, 1, 0, 0, 0]]))
        header, data = db.get_all_authors_stat_by_year(2012)
        self.assertEqual(data, ([["AUTHOR1", 0, 0, 0, 0, 0], ["AUTHOR2", 0, 0, 0, 0, 0]]))
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        header, data = db.get_all_authors_stat_by_year(2012)
        self.assertEqual(data, ([['AUTHOR', 3, 3, 0, 0, 0], ['AUTHOR1', 1, 1, 0, 0, 0]]))
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        header, data = db.get_all_authors_stat_by_year(9999)
        self.assertEqual(data, ([['AUTHOR1', 3, 3, 0, 0, 0], ['AUTHOR3', 1, 1, 0, 0, 0], ['AUTHOR4', 2, 2, 0, 0, 0], ['AUTHOR2', 1, 0, 0, 0, 1]]))
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml")))
        header, data = db.get_all_authors_stat_by_year(2005)
        self.assertEqual(data[0], (['Fabio Casati', 0, 0, 0, 0, 0]))
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_all_authors_stat_by_year(1999)
        self.assertEqual(data[5], (['AnHai Doan', 0, 0, 0, 0, 0]))                
                
    def test_get_publications_for_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_for_year(9999)
        self.assertEqual(data, ([1, 1, 0, 0, 0]))
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_separations.xml")))
        header, data = db.get_publications_for_year(9999)
        self.assertEqual(data, ([0, 0, 0, 0, 0]))
        header, data = db.get_publications_for_year(2008)
        self.assertEqual(data, ([1, 1, 0, 0, 0]))
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_publications_by_year_curated.xml")))
        header, data = db.get_publications_for_year(2004)
        self.assertEqual(data, ([4, 0, 3, 1, 0]))

    def test_get_all_publications(self):
        db = database.Database()
        self.assertTrue(
            db.read(path.join(self.data_dir, "dblp_publications_by_year_curated.xml")))
        header, data = db.get_all_publications()
        self.assertEqual(data, (
            [['Letter from the Special Issue Editor.', 'http://sites.computer.org/debull/A01JUN-CD.pdf', 
                'Alon Y. Halevy', 2019, '-', 'IEEE Data Eng. Bull.', '24', '2', '2', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/debu/debu24.html#Halevy01', '-', '-'],
            ['Representing and Reasoning about Mappings between Domain Models.', 'http://www.aaai.org/Library/AAAI/2002/aaai02-013.php',
                 'Jayant Madhavan, Philip A. Bernstein, Pedro Domingos, Alon Y. Halevy', 2002, 'AAAI/IAAI', '-', '-', '80-86', '-', 'conf/aaai/2002', 'http://www.informatik.uni-trier.de/~ley/db/conf/aaai/aaai2002.html#MadhavanBDH02', '-', '-'],
            ['Learning to Match the Schemas of Data Sources: A Multistrategy Approach.','http://dx.doi.org/10.1023/A:1021765902788', 
                'AnHai Doan, Pedro Domingos, Alon Y. Halevy', 2003, '-', 'Machine Learning', '50', '279-301','3', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/ml/ml50.html#DoanDH03', '-', '-'],
            ["Why your data won't mix.", 'http://doi.acm.org/10.1145/1103822.1103836', 
                'Alon Y. Halevy', 2005, '-', 'ACM Queue', '3', '50-58', '8', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/queue/queue3.html#Halevy05', '-', '-'],
            ['Data Integration: A Status Report.', 'http://subs.emis.de/LNI/Proceedings/Proceedings26/article623.html', 
                'Alon Y. Halevy', 2003, 'BTW', '-', '-', '24-29', '-', 'conf/btw/2003', 'http://www.informatik.uni-trier.de/~ley/db/conf/btw/btw2003.html#Halevy03', '-', '-'],
            ['Semantic Integration Research in the Database Community: A Brief Survey.', 'http://www.aaai.org/ojs/index.php/aimagazine/article/view/1801', 
                'AnHai Doan, Alon Y. Halevy', 2005, '-', 'AI Magazine', '26', '83-94', '1', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/aim/aim26.html#DoanH05', '-', '-'],
            ['Semantic Integration Workshop at the Second International Semantic Web Conference (ISWC-2003).', 'http://www.aaai.org/ojs/index.php/aimagazine/article/view/1753',
                'AnHai Doan, Alon Y. Halevy, Natalya Fridman Noy', 2004, '-', 'AI Magazine', '25', '109-112', '1', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/aim/aim25.html#DoanHN04', '-', '-'],
            ['Semantic Integration.', 'http://www.aaai.org/ojs/index.php/aimagazine/article/view/1794',
                'Natalya Fridman Noy, AnHai Doan, Alon Y. Halevy', 2005, '-', 'AI Magazine', '26', '7-10', '1', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/aim/aim26.html#NoyDH05', '-', '-'],
            ['Semantic Integration Workshop at the 2nd International Semantic Web Conference (ISWC-2003).', 'http://www.acm.org/sigmod/record/issues/0403/R3.Semantic_integration_03.pdf', 
                'AnHai Doan, Alon Y. Halevy, Natalya Fridman Noy', 2004, '-', 'SIGMOD Record', '33', '138-140', '1', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/sigmod/sigmod33.html#DoanHN04', '-', '-'],
            ['Introduction to the Special Issue on Semantic Integration.', 'http://doi.acm.org/10.1145/1041410.1041412', 
                'AnHai Doan, Natalya Fridman Noy, Alon Y. Halevy', 2004, '-', 'SIGMOD Record', '33', '11-13', '4', '-', 'http://www.informatik.uni-trier.de/~ley/db/journals/sigmod/sigmod33.html#DoanNH04', '-', '-']]

        ))
if __name__ == '__main__':
    unittest.main()
