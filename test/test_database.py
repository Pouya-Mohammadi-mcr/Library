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
        self.assertFalse(db.read(path.join(self.data_dir, "invalid_xml_file.xml")))

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
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
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
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data[0]), 6, "incorrect number of columns in data")
        self.assertEqual(len(data), 2, "incorrect number of rows in data")
        self.assertEqual(data[0][1], 1, "incorrect number of publications for conference papers")
        self.assertEqual(data[1][1], 2, "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "three-authors-and-three-publications.xml")))
        header, data = db.get_average_authors_per_publication_by_author(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 3, "incorrect average of number of conference papers")
        self.assertEqual(data[0][1], 1.5, "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2, "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1, "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 2, "incorrect number of authors")
        self.assertEqual(data[0][-1], 1, "incorrect total")

    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_average_publications_per_author_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of rows")
        self.assertEqual(data[0][0], 9999, "incorrect year in result")
        self.assertEqual(data[0][1], 2, "incorrect number of authors in result")

    def test_get_coauthor_data(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "three-authors-and-three-publications.xml")))
        header, data = db.get_coauthor_data(None,None,4)
        self.assertEqual(len(data), 2,"incorrect number of rows")
        self.assertEqual(data[0][0],"author1 1")
        self.assertEqual(data[0][1],"author2 1")
        self.assertEqual(data[1][0],"author2 1")
        self.assertEqual(data[1][1],"author1 1")

    def test_get_publication_summary_average(self):
        MEANAPP=['Mean authors per publication', 2.0, 0, 1.0, 0, 1.75]
        MEANPPA=['Mean publications per author', 1.5, 0.0, 0.25, 0.0, 1.75]
        MEDAPP=['Median authors per publication', 2, 0, 1, 0, 1.5]
        MEDPPA=['Median publications per author', 1.5, 0.0, 0.0, 0.0, 1.5]
        MODEAPP=['Mode authors per publication', [1, 2, 3], [], [1], [], [1]]
        MODEPPA=['Mode publications per author', [0.0, 1.0, 2.0, 3.0], [0.0], [0.0], [0.0], [1.0]]
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_publication_summary_average(database.Stat.MEAN)
        self.assertEqual(data[0],MEANAPP)
        self.assertEqual(data[1],MEANPPA)
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
        header, data = db.get_average_authors_per_publication_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        self.assertEqual(len(data), 1, "incorrect number of years")
        self.assertEqual(data[0][1], 2.0, "incorrect mean authors per conference paper for year1")
        self.assertEqual(data[0][2], 0, "incorrect mean authors per journal for year1")
        self.assertEqual(data[0][3], 1.0, "incorrect mean authors per book for year1")
        self.assertEqual(data[0][4], 0, "incorrect mean authors per book chapter for year1")
        self.assertEqual(data[0][5], 1.75, "incorrect mean authors per publication for year1")


    def test_get_collaborations(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        data = db._get_collaborations(0,1)
        self.assertEqual(data[0],3,"wrong number of publications")
        self.assertEqual(data[1],1,"wrong count of collaboration with author3")
        self.assertEqual(data[2],2,"wrong count of collaboration with author4") 

    def test_get_coauthor_details(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        data = db.get_coauthor_details("AUTHOR1")
        self.assertEqual(data[0][0],"AUTHOR1","wrong name for author")
        self.assertEqual(data[0][1],3,"wrong number of publications")
        self.assertEqual(data[1][0],"AUTHOR3","wrong name for coauthor")
        self.assertEqual(data[1][1],1,"wrong count of collaboration with author3")
        self.assertEqual(data[2][0],"AUTHOR4","wrong name for author")
        self.assertEqual(data[2][1],2,"wrong count of collaboration with author4")

    def test_all_authors(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))  
        print(db.get_all_authors())           
    def test_get_network_data(self):
        nodes = [['AUTHOR1', 2], ['AUTHOR3', 2], ['AUTHOR4', 2], ['AUTHOR2', 0]]
        links = {(0, 1), (0, 2), (1, 2)}
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir,
                                          "sprint-2-acceptance-2.xml")))
        data = db.get_network_data()
        self.assertEqual(data[0][0][0],"AUTHOR1","wrong name for author")   
        self.assertEqual(data[0][0][1],2,"wrong number of authors in AUTHOR1's network")
        self.assertEqual(data[0], nodes, "wrong nodes details")   
        self.assertEqual(data[1], links, "wrong links details")  

    def test_get_author_firstlastsole(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR1', 1, 1, 0], ['AUTHOR2', 0, 1, 0], ['AUTHOR3', 0, 1, 0], ['AUTHOR4', 2, 0, 0]])
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR1', 2, 0, 1], ['AUTHOR3', 0, 0, 0], ['AUTHOR4', 0, 2, 0], ['AUTHOR2', 0, 0, 1]])
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR', 0, 0, 9], ['AUTHOR1', 0, 0, 1]])
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        header, data = db.get_author_firstlastsole()
        self.assertEqual(data, [['AUTHOR1', 1, 0, 2], ['AUTHOR2', 0, 1, 0], ['AUTHOR3', 2, 1, 0], ['AUTHOR4', 0, 2, 0],
                                ['AUTHOR6', 1, 0, 0], ['AUTHOR7', 0, 0, 1], ['AUTHOR8', 0, 0, 2]])
        
if __name__ == '__main__':
    unittest.main()
