import unittest

from dataprep.dataprep.load_data import LoadData


class TestData(unittest.TestCase):

    def setUp(self):
        """I should used this to generate toy data"""
        pass

    def test_parsing(self):
        """ Checks that the images have the same size amongst themselves
        """
        print('Check that all images have the same size')
        ld = LoadData(data_directory='../../data')
        for d in ld.data:
            assert(ld.data[d]['attributes']['width'] == ld.width_dicom)
            assert(ld.data[d]['attributes']['height'] == ld.height_dicom)

    def test_generator(self):
        """Test that the generator produces the same LONG-TERM results when using random or non-random sample selection
        (We'd expect images to be uniformly distributed after a large number of iterations)

        """
        print('Check that the generator produces the same outputs irrespective of order modality')

        # Generate data using random order
        ld = LoadData(data_directory='../../data')
        training_data = ld.load_data_generator(batch_size=8, random_order=True)
        X = dict()
        for n in range(8*500):
            x,y = next(training_data)
            for _ in y:
                _ = str(_)
                X[_] = X[_]+1 if _ in X else 1
        res, res2 = [], []
        for n in X:
            res.append(X[n])

        # Now generate data using non-random order
        training_data = ld.load_data_generator(batch_size=8, random_order=False)
        X = dict()
        for n in range(8*500):
            x, y = next(training_data)
            for _ in y:
                _ = str(_)
                X[_] = X[_] + 1 if _ in X else 1
        for n in X:
            res2.append(X[n])
        for x,y in zip(sorted(res), sorted(res2)):
            # Assert that the two values are roughly within 1%
            assert(abs(x-y)/x<.01)


if __name__ == '__main__':
    unittest.main()