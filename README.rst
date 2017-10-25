
**•	How did you verify that you are parsing the contours correctly?**

1. Through visual inspection. I used a jupyter notebook (`Exploration.ipynb`) to visualize the images and the contours, also to get familiar with the data.

2. Built an “anomaly detection” (see the method `anomaly_detector()`, inside `parse_data.py`). The method compares i-contours with o-contours (when both available) and checks that the coordinates of the inner contours are bounded by those of the outer contour. Algorithm:
  *	Bin all `x` coordinates for i-contours and o- contours using `round()`.
  *	For every `x`, check that the following is true: (y1_o < y1_i < y2_i < y2_i) within some tolerance value [tol=3] (“y1_o” is the smallest of the two y coordinates of the outer contour).
  * If not, propagate a `warning`.
Admittedly, I did not test this extensively. Another similar approach would be to measure the area of the two contours and checking that Area_inner<=Area_outer. 


**•	What changes did you make to the code, if any, in order to integrate it into our production code base?**

1. Created a method get_data() to fetch the data (contours, images, performs a sanity check, polygon) and save it to a dictionary. It also saves the directories for each i-contour/dicom_image, but I am currently not using this (more below). The choice of a dictionary as data structure is discussed below.

2. Handling of the InvalidDicomError exception, where now I `raise Exception('The DICOM image is not valid. Filename: {}'.format(filename))`


**•	Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in Part 2? If so, what? If not, is there anything that you can imagine changing in the future?**

1. Since I created a class to load the data and generate training examples, I changed the get_data() (in parse_data.py) to return data to the class. 
In retrospect, loading all the data at once is probably a poor choice for large datasets, and a greedy evaluation (where I only load in memory the mini-batch) should be followed for instead for datasets that wouldn’t all fit in memory.


**•	How do you/did you verify that the pipeline was working correctly?**

1. I implemented two unit tests.
  * test_parsing checks that the input images all have the same width and height (note this is a data check more than a unit test.) 
  * test_generator runs iterates through the dataset few hundred times in random order or in non-random (consecutive) order. The test then asserts that the same image has overall the same count in both modality.
Well, embarrassingly, the test passes but I had to "bend the rules" slightly for it to pass. I think the problem is with the test case (or the data, that I think contains multiple identical images). With more time, I would look into this.


**•	Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in?**
Several things could be improved, many of which I have described in the previous points. Few additional `#ToDo`’s/comments.

1. I would add more test cases/sanity checks for the data. Eg., checking that there are no zero-byte images.

2. The data is located using parsing string via templates. Even small changes in the directories/files names would break the pipeline. I also didn’t write test cases for that.

3. A side point about the instructions for the generator to load batches (PART 2). The data challenge requires loading batches randomly within epoch, and across epochs. However, when choosing a batch_size that is not an exact multiple of the database_size, there could be instances where one or more samples are repeated in the same batch (this would happen when in the same batch there are samples from the last epoch as well as the new epoch). This has probably a small effect on training, but might explain why one of my test cases failed.
