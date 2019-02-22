## Automated Facial Recognition

### Aim 
1. Researching practical aspects of facial recognition systems.
2. Proposing and demonstrating end to end pipeline.

### Introduction
1. FaceNet generates 128-d embeddings.
2. Problem: Direct usage bad, only 65% accuracy.
3. Previous semester work.
4. Need of research. We brought it to 98%. 
5. Structure of paper.
	- Data acquisition
	- Clustering for faster training.
	- Pipeline description
	- Classifiers
	- Web Apps
	- Evaluation
	- Future Work

### Data acquisition
We take different poses for four people at a time.

### Clustering for faster training
1. Modified agglomerative clustering generates bins. 
2. Write the pseudo code (looks awesome like in theoretical CS papers).

### Pipeline description
1. One line each on size of training data, specs of GPU, detection and recognition models.
2. Flow chart (awesome one).
3. Basic description of how facenet was trained and formation of hypothetical spheres.
4. Leads to why we need a new classifier?

### Classifiers 
All of them have been modified such that they do not label same person twice in one image. Mention two lines or pseudo for each.
1. Mean distance classifier
2. KNN classifier
3. K-Mean-classifier without threshold
4. K-Mean-classifier with threshold

### Web App
Saket write 2-3 lines here.

### Evaluation (main focus)
1. Evaluating classifiers - Use labelled data

**Stat table**

| Name of Classifier | Total faces | Skipped faces | Labelled faces | Accuracy|
| ------------------| ---------------| ---------------| --------|
| Mean distance classifier| __ | __ | __ | 0.66 |
| KNN classifier| __ | __ | __ | 0.67 |
| K Mean classifier without threshold | __ |  __ | __ | 0.66 |
| K Mean with threshold | __ | __ | __ | 0.97 |

2. Evaluating attendance system - Use all 6 sessions

| Session Id | Total images | Total faces | # Students- Truth | # Students -after aggregation |
| ------------------| ---------------| ---------------| -------------| ---------------- |
| Session 1 | 100| 800| 28| 25| 
| Session 2 | 100| 800| 32| 26| 
  
