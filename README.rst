
**•	How did you verify that you are parsing the contours correctly?**

1. At first, through visual inspection. I used a jupyter notebook (`Exploration.ipynb`) to visualize the images and the contours and familiarize with the data.

2. Built an “anomaly detection” (see the method `anomaly_detector()`, inside `parse_data.py`). The method compares i-contours with o-contours (when both available) and checks that the coordinates of the inner contours are bounded by those of the outer contour. Algorithm:
  *	Check if both i-contour and o-contour are available for the same image, otherwise return.
  *	Bin all `x` coordinates for i-contours and o- contours using `round()`.
  *	For every `x`, check that the following condition is true: (y1_o < y1_i < y2_i < y2_o) within some tolerance value [tol=3] (“y1_o” is the smallest of the two y coordinates of the outer contour, whereas y2_o is the largest. If you think of one circle circumscribed to another, y1_o and y2_o are the ordinates of the outer circle for a fiven abscissa, while y1_i and y2_i are those of the inner circle).
  * If not, propagate a `warning`.
No anomaly of this such was detected, but I did not test this feature extensively. Another similar approach would be to measure the area of the two contours and checking that Area_inner<=Area_outer, but it might fail for objects that do not overlap. 


**•	What changes did you make to the code, if any, in order to integrate it into our production code base?**

1. Created a method `get_data()` to fetch the data ((contours, images, polygon), and perform a sanity check on the data) and save it to a dictionary data-structure. It also saves a directory containig each i-contour/dicom_image link, but I am currently not using this information directly (more below, where also the choice of a dictionary as data structure is discussed).

2. Handling of the InvalidDicomError exception, where now I `raise Exception('The DICOM image is not valid. Filename: {}'.format(filename))`


**•	Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in Part 2? If so, what? If not, is there anything that you can imagine changing in the future?**

1. Since I created a Class to load the data and generate training examples, I changed the `get_data()` (in `parse_data.py`) to return data to the class. 
In retrospect, loading all the data at once is a poor choice for large datasets, and a greedy evaluation (where I only load in memory each mini-batch) should be followed instead for datasets that wouldn’t all fit in memory.


**•	How do you/did you verify that the pipeline was working correctly?**

1. I implemented two unit tests:
  * 1: `test_parsing()` checks that the input images all have the same `width` and `height` (note this is a data check more than a unit test.) 
  * 2: `test_generator()` iterates through the dataset many times in a random or non-random (consecutive) order. The test then asserts that the same image has overall the same count with both modality.
Interestingly, the second test didn't pass at first. I think the problem might be with the test case and/or the data (I suspect that there are multiple identical images). With more time, I would look into this.


**•	Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in?**
Several things could be improved, many of which I have described in the previous points. Few additional `#ToDo`’s/comments.

1. I would add more test cases/sanity checks for the data. Eg., checking that there are no zero-byte images.

2. For the unit tests, focus on testing the code more than the data. Hence, generate toy data.

3. The data is located parsing strings via templates. Even small changes in the directories/files names would break the pipeline. I also didn’t write test cases for that.

4. A side point about the instructions for the generator to load batches (PART 2). The data challenge requires loading batches randomly within epoch, and across epochs. However, when choosing a `batch_size` that is not an factor of the `database_size` (eg.: `batch_size=9`, `database_size=100`), there could be instances where one or more samples are repeated in the same batch (this would happen when in the same batch there are samples from the last epoch as well as the new epoch). This has probably a small effect on training, but might explain why one of my test cases failed.
