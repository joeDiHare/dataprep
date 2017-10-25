import unittest

import dataprep
from dataprep.dataprep.parse_input import *
from dataprep.dataprep.load_data import LoadData


class TestData(unittest.TestCase):

    def setUp(self):
        pass

    def test_parsing(self):
        print('Check that all images have the same size')
        ld = LoadData(data_directory='../../data')
        for d in ld.data:
            assert(ld.data[d]['attributes']['width'] == ld.width_dicom)
            assert (ld.data[d]['attributes']['height'] == ld.height_dicom)

    def test_generator(self):
        ld = LoadData(data_directory='../../data')
        training_data = ld.load_data_generator(batch_size=8, random_order=True)
        X = dict()
        for n in range(1000):
            x,y = next(training_data)
            for _ in y:
                _ = str(_)
                X[_] = X[_]+1 if _ in X else 1
        res=[]
        for n in X:
            res.append(X[n])
        print(res)

        # Expect values to be uniformly distributed

if __name__ == '__main__':
    unittest.main()


# from dataprep.dataprep.load_data import LoadData; print(next(LoadData().load_data_generator(data_directory='dataprep/data')))
# from dataprep.dataprep.load_data import LoadData; ld=LoadData();r=ld.load_data_generator(data_directory='dataprep/data'); print(next(r))