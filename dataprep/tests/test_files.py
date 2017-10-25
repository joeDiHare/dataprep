import unittest

import dataprep
from dataprep.dataprep.parse_input import *
from dataprep.dataprep.load_data import LoadData


class TestData(unittest.TestCase):

    def setUp(self):
        pass

    def test_parsing(self):
        # data, data_binds = get_data(data_directory='../../data')
        # for d in data:
        pass

    def test_generator(self):
        ld = LoadData()
        data = ld.load_data_generator(data_directory='../../data', batch_size=8, random_order=False)
        X = dict()
        for n in range(1000):
            y, x = next(data)
            # print('LEN',len(y))
            for _ in y:
                if str(_) in X:
                    # print('here')
                    X[str(_)]+=1
                else:
                    # print('oh')
                    X[str(_)] = 1
        res=[]
        for n in X:
            res.append(X[n])
        print(res)

        # Expect values to be uniformly distributed

if __name__ == '__main__':
    unittest.main()


# from dataprep.dataprep.load_data import LoadData; print(next(LoadData().load_data_generator(data_directory='dataprep/data')))
# from dataprep.dataprep.load_data import LoadData; ld=LoadData();r=ld.load_data_generator(data_directory='dataprep/data'); print(next(r))