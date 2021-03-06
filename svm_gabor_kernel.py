# -*- coding: utf-8 -*-
"""SVM_Gabor_Kernel.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fzo_rhxVBJKJpl5j227oJ84i_HSNb1qK

##Andrew Clark
##Investigation of SVM Performance on Images Passed Through Gabor Filters Vs. Unfiltered Images. SVM C Paramter Tuned via Gridsearch.

Train SVM On Unaugmented Images From MNIST
--------
"""

#use sklearn for the SVM and Data import
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

ds = fetch_openml('mnist_784')

x,y = ds.data, ds.target

#create training and validation sets 
x_train, x_val, y_train, y_val = train_test_split(x,y,test_size=0.2, random_state=42,shuffle=True)

#verify the data has been downloaded correctly 
import matplotlib.pyplot as plt
#len(xtrain[0])#returns 784.
a = x_train[0].reshape((28,28))
# show the first datum in x_train
plt.imshow(a)

#Plot the downsampled image
import cv2 
a = cv2.resize(a, (14,14))
plt.imshow(a)

#downsample the images in both the training set
import cv2
import numpy as np
downsampled_xtrain=np.ndarray(shape=(56000,196),dtype=float)
for i in range(0,len(x_train)-1):
  resized_1=x_train[i].reshape((28,28))
  resized_1=cv2.resize(resized_1,(14,14))
  reshaped=resized_1.reshape((196,))
  downsampled_xtrain[i]=reshaped

#Train the SVM classifier 
from sklearn import svm 
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
#create classifier object
classifier = svm.SVC(C=1.0, kernel='rbf', gamma= 'scale')
#create pipeline
#pipeline=make_pipeline(StandardScaler(),classifier)
#fit the model 
classifier.fit(downsampled_xtrain,y_train)

#Get number of support vectors for the SVM model 

print('Number of Support Samples:',sum(classifier.n_support_))
print('Total Number of Training Samples:',downsampled_xtrain.shape[0])

#downsample the x_val
downsampled_xval=np.ndarray(shape=(14000,196),dtype=float)
for i in range(0,len(downsampled_xval)-1):
  resized_1=x_val[i].reshape((28,28))
  resized_1=cv2.resize(resized_1,(14,14))
  reshaped=resized_1.reshape((196,))
  downsampled_xval[i]=reshaped

#Make predictions on the validation set and compute accuracy. 

#make predictions 
predictions=classifier.predict(downsampled_xval)
#compute validation accuray 
from sklearn.metrics import accuracy_score
validation_accuracy=accuracy_score(y_val,predictions)
print('Validation Accuracy:', validation_accuracy) #We see that the validation accuracy is 97.72%

validation_accuracy*100

#Create confusion matrix 
from sklearn.metrics import plot_confusion_matrix
plot_confusion_matrix(classifier,downsampled_xval, y_val)

#Create confusion matrix without the figure graphic
from sklearn.metrics import confusion_matrix
confusion_matrix(y_val,predictions)

"""Complete Grid Search for Hyper-Parameter C
---
"""

#Complete the grid search for the hyper-parameter C
from sklearn.model_selection import GridSearchCV

classifier = svm.SVC(C=1.0, kernel='rbf', gamma= 'scale')
parameters={'C':[0.1,0.5, 0.75, 1.0,10,50]}

classifier_1=GridSearchCV(classifier, parameters,scoring='accuracy')
#pipeline_2=make_pipeline(StandardScaler(),classifier)
classifier_1.fit(downsampled_xval,y_val) #FIT ON VALIDATION SET since we are finding more optimal hyperparameters

#Show the accuracies from the grid search for the hyper-parameter C
classifier_1.cv_results_

"""So we see that C=10.0 resulted in highest cross-validated accuracy (higher than C=1.0) and thus this is our new value of C.

Create balanced training and validation sets of only 500 images. 50 images per class. 
---
"""

#Create balanced training and validation sets of only 500 images. 50 images per class.  

labels_list=[str(0),str(1),str(2),str(3),str(4),str(5),str(6),str(7),str(8),str(9)]

smaller_xtrain_1=np.ndarray(shape=(500,196),dtype=float)
smaller_ytrain=[]

smaller_xval_1=np.ndarray(shape=(500,196),dtype=float)
smaller_yval=[]

count=0
for i in range(0,10):
  indexes=np.where(y_train==labels_list[i])
  for j in range(count,50+count):
    smaller_xtrain_1[j]=downsampled_xtrain[indexes[0][j]]
    smaller_ytrain.append(labels_list[i])
  count=count+50

#create validation set
for i in range(0,10):
  indexes=np.where(y_train==labels_list[i])
  for j in range(count,50+count):
    smaller_xval_1[j-500]=downsampled_xtrain[indexes[0][j]]
    smaller_yval.append(labels_list[i])
  count=count+50

#Create balanced training and validation sets of only 500 images. 50 images per class.  

from imblearn.under_sampling import RandomUnderSampler

undersampler=RandomUnderSampler(random_state=42)
X_res,y_res=undersampler.fit_resample(downsampled_xtrain,y_train)

x_train_small, x_val_small, y_train_small, y_val_small = train_test_split(X_res,y_res,train_size=500,test_size=500, random_state=42,shuffle=True)

"""Display a few different parameters for F, theta, and bandwith for the Gabor Filters
---
"""

#display a few different parameters for F, theta, and bandwith 

from skimage.filters import gabor_kernel, gabor
import numpy as np
freq, theta, bandwidth = 0.1, np.pi/4, 1
gk = gabor_kernel(frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(1); plt.clf(); plt.imshow(gk.real)
plt.figure(2); plt.clf(); plt.imshow(gk.imag)

# convolve the input image with the kernel and get co-efficients
# we will use only the real part and throw away the imaginary
# part of the co-efficients

#display a few different parameters for F, theta, and bandwith 
image = downsampled_xtrain[0].reshape((14,14))
coeff_real,_ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(3); plt.clf(); plt.imshow(coeff_real)

#display a few different parameters for F, theta, and bandwith 

freq, theta, bandwidth = (0.1/2), np.pi/8, 0.5
gk = gabor_kernel(frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(1); plt.clf(); plt.imshow(gk.real)
plt.figure(2); plt.clf(); plt.imshow(gk.imag)

# convolve the input image with the kernel and get co-efficients
# we will use only the real part and throw away the imaginary
# part of the co-efficients

#display a few different parameters for F, theta, and bandwith 
image = downsampled_xtrain[0].reshape((14,14))
coeff_real,_ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(3); plt.clf(); plt.imshow(coeff_real)

# display a few different parameters for F, theta, and bandwith 

freq, theta, bandwidth = (0.2), np.pi/2, 2
gk = gabor_kernel(frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(1); plt.clf(); plt.imshow(gk.real)
plt.figure(2); plt.clf(); plt.imshow(gk.imag)

# convolve the input image with the kernel and get co-efficients
# we will use only the real part and throw away the imaginary
# part of the co-efficients

#display a few different parameters for F, theta, and bandwith 
image = downsampled_xtrain[0].reshape((14,14))
coeff_real,_ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(3); plt.clf(); plt.imshow(coeff_real)

#Display a few different parameters for F, theta, and bandwith 
freq, theta, bandwidth = (0.3), np.pi, 3
gk = gabor_kernel(frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(1); plt.clf(); plt.imshow(gk.real)
plt.figure(2); plt.clf(); plt.imshow(gk.imag)

# convolve the input image with the kernel and get co-efficients
# we will use only the real part and throw away the imaginary
# part of the co-efficients

#display a few different parameters for F, theta, and bandwith 
image = downsampled_xtrain[0].reshape((14,14))
coeff_real,_ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
plt.figure(3); plt.clf(); plt.imshow(coeff_real)

#Plot and Create the filter bank 
from skimage.filters import gabor_kernel, gabor
import numpy as np

#define parameters for the filter bank 

#old params
#thetas=[np.pi/4, np.pi/2,(3*np.pi/4), np.pi]
#frequency=[0.05,0.25]
#bandwidths=[0.1,1]

thetas = np.arange(0,np.pi,np.pi/4)
frequency = np.arange(0.05,0.5,0.15)
bandwidths = np.arange(0.3,1,0.3)

#create and plot the filter bank
filter_bank_small=[]

count=0
for i in range(0,len(thetas)):
  for k in range(0,len(bandwidths)):
      for j in range(0,len(frequency)):
        freq, theta, bandwidth = frequency[j],thetas[i],bandwidths[k]
        gk = gabor_kernel(frequency=freq, theta=theta, bandwidth=bandwidth)
        plt.figure(count+1); plt.clf(); plt.imshow(gk.real)
        plt.figure(count+2); plt.clf(); plt.imshow(gk.imag)
        filter_bank_small.append(gk.real)
        count=count+1
      # convolve the input image with the kernel and get co-efficients
      # we will use only the real part and throw away the imaginary part of the co-efficients
      #image = smaller_xtrain_1[i].reshape((14,14))
      #coeff_real,_ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
      #plt.figure(count+3); plt.clf(); plt.imshow(coeff_real)

!pip install tqdm

"""Convolve the training and test images with Gabor Filters to investigate this effect on the SVM Performance
---
"""

#convovle the filters with the images in the training set
from tqdm import tqdm_notebook

thetas = np.arange(0,np.pi,np.pi/4)
frequency = np.arange(0.05,0.5,0.15)
bandwidths = np.arange(0.3,1,0.3)

gabor_x_train_1=np.ndarray(shape=(500,7056),dtype=float)

for j in tqdm_notebook(range(0,len(x_train_small))):
  feat_vec=[] #create a new list for each image
  #iterate through the 36 length filter bank for each image
  for i in range(0,len(thetas)):
    for k in range(0,len(bandwidths)):
      for l in range(0,len(frequency)):
        freq, theta, bandwidth = frequency[l],thetas[i],bandwidths[k]
        image = x_train_small[j].reshape((14,14))
        coeff_real, _ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
        feat_vec.append(coeff_real)
        row_1=np.concatenate(feat_vec).ravel() #flatten the list of lists into a numpy array
  gabor_x_train_1[j]=row_1#append to the training set

# #Convovle each training set image with each filter to create a single 7056 vector for each image
# from scipy import ndimage as nd
# from astropy.convolution import convolve

# gabor_x_train_1=np.ndarray(shape=(500,7056),dtype=float)

# #gabor_x_train=[]
# for j in range(0,len(x_train_small)):
#   feat_vec=[] #create a new list for each image
#   for i in range(0,len(filter_bank_small)): #iterate through the 16 length filter bank for each image 
#     #convovle the reshaped image
#     reshaped_image=x_train_small[j].reshape((14,14))
#     convolved_image=nd.convolve(reshaped_image,np.real(filter_bank_small[i]))
#     #convolved_image=convolve(reshaped_image,np.real(filter_bank_small[i]))
#     #append the convovled image to the feature vector list 
#     feat_vec.append(convolved_image)
# row_1=np.concatenate(feat_vec).ravel() #flatten the list of lists into a numpy array
# gabor_x_train_1[j]=row_1#append to the training set

#Train the SVM model on the new training set
from sklearn import svm 
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
#np.logspace(-3, 2, 6)}

from sklearn.model_selection import GridSearchCV

#classifier = svm.SVC(C=1.0, gamma= 'scale')
#parameters={'C':[0.1,0.5, 0.75, 1.0,10,50],'kernel':['rbf','ploy','linear']}

gabor_classifier_first = svm.SVC(C=50.0, kernel='poly', gamma= 'scale') 
#create pipeline
pipeline_gabor_1=make_pipeline(StandardScaler(),gabor_classifier_first)
#fit the model 
pipeline_gabor_1.fit(gabor_x_train_1,y_train_small)

#Convolve the Validation Set
from tqdm import tqdm_notebook

thetas = np.arange(0,np.pi,np.pi/4)
frequency = np.arange(0.05,0.5,0.15)
bandwidths = np.arange(0.3,1,0.3)

gabor_x_val_1=np.ndarray(shape=(500,7056),dtype=float)

for j in tqdm_notebook(range(0,len(x_val_small))):
  feat_vec=[] #create a new list for each image
  #iterate through the 36 length filter bank for each image
  for i in range(0,len(thetas)):
    for k in range(0,len(bandwidths)):
      for l in range(0,len(frequency)):
        freq, theta, bandwidth = frequency[l],thetas[i],bandwidths[k]
        image = x_val_small[j].reshape((14,14))
        coeff_real, _ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
        feat_vec.append(coeff_real)
        row_1=np.concatenate(feat_vec).ravel() #flatten the list of lists into a numpy array
  gabor_x_val_1[j]=row_1#append to the training set

from sklearn.metrics import accuracy_score
#make predictions on the validation set 
#make predictions 
predictions_1=pipeline_gabor_1.predict(gabor_x_val_1)
#compute validation accuray 
validation_accuracy_gabor_1=accuracy_score(y_val_small,predictions_1)
print('Validation Accuracy:', validation_accuracy_gabor_1) #We see that the validation accuracy is

"""So we see the validation accuracy with 36 filters is 79%. """

#Increase the number of filters in the filter bank and plot the filters. We now have 48 filters

thetas_new = np.arange(0,np.pi,np.pi/4)
Fs_new = np.arange(0.05,0.4,0.15)
bandwidths_new = np.arange(0.3,1.25,0.3)

#create the filter bank
filter_bank_new=[]

count=0
for i in range(0,len(thetas_new)):
  for j in range(0,len(Fs_new)):
    for k in range(0,len(bandwidths_new)):
      #print(theta,F,bandwidth)
      freq, theta, bandwidth = Fs_new[j],thetas_new[i],bandwidths_new[k]
      gk = gabor_kernel(frequency=freq, theta=theta, bandwidth=bandwidth)
      filter_bank_new.append(gk.real)
      plt.figure(count+1); plt.clf(); plt.imshow(gk.real)
      plt.figure(count+2); plt.clf(); plt.imshow(gk.imag)
      count=count+1

len(filter_bank_new) #48 filters will now be used

"""Expand the Filter Bank to 48 Gabor filters and Train the SVM again
---
"""

#Convovle each training set image with each of the now expanded filters in the filter bank to create a single 9048 vector for each image
from tqdm import tqdm_notebook

thetas_new = np.arange(0,np.pi,np.pi/4)
Fs_new = np.arange(0.05,0.4,0.15)
bandwidths_new = np.arange(0.3,1.25,0.3)

# thetas = np.arange(0,np.pi,np.pi/4)
# frequency = np.arange(0.05,0.5,0.15)
# bandwidths = np.arange(0.3,1,0.3)

gabor_x_train_2=np.ndarray(shape=(500,9408),dtype=float)

for j in tqdm_notebook(range(0,len(x_train_small))):
  feat_vec=[] #create a new list for each image
  #iterate through the 36 length filter bank for each image
  for i in range(0,len(thetas_new)):
    for k in range(0,len(bandwidths_new)):
      for l in range(0,len(Fs_new)):
        freq, theta, bandwidth = Fs_new[l],thetas_new[i],bandwidths_new[k]
        image = x_train_small[j].reshape((14,14))
        coeff_real, _ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
        feat_vec.append(coeff_real)
        row_1=np.concatenate(feat_vec).ravel() #flatten the list of lists into a numpy array
  gabor_x_train_2[j]=row_1#append to the training set

#Train the SVM model on the new expanded training set
from sklearn import svm 
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler # use standard scaler 

gabor_classifier_2 = svm.SVC(C=50.0, kernel='poly', gamma= 'scale')
#create pipeline
pipeline_gabor_2=make_pipeline(StandardScaler(),gabor_classifier_2)
#fit the model 
pipeline_gabor_2.fit(gabor_x_train_2,y_train_small)

thetas_new = np.arange(0,np.pi,np.pi/4)
Fs_new = np.arange(0.05,0.4,0.15)
bandwidths_new = np.arange(0.3,1.25,0.3)

# thetas = np.arange(0,np.pi,np.pi/4)
# frequency = np.arange(0.05,0.5,0.15)
# bandwidths = np.arange(0.3,1,0.3)

gabor_x_val_2=np.ndarray(shape=(500,9408),dtype=float)

for j in tqdm_notebook(range(0,len(x_train_small))):
  feat_vec=[] #create a new list for each image
  #iterate through the 36 length filter bank for each image
  for i in range(0,len(thetas_new)):
    for k in range(0,len(bandwidths_new)):
      for l in range(0,len(Fs_new)):
        freq, theta, bandwidth = Fs_new[l],thetas_new[i],bandwidths_new[k]
        image = x_val_small[j].reshape((14,14))
        coeff_real, _ = gabor(image, frequency=freq, theta=theta, bandwidth=bandwidth)
        feat_vec.append(coeff_real)
        row_1=np.concatenate(feat_vec).ravel() #flatten the list of lists into a numpy array
  gabor_x_val_2[j]=row_1#append to the training set

#Compute the validation accuracy for the new expanded filter set
from sklearn.metrics import accuracy_score
#make predictions on the validation set 
#make predictions 
predictions_2=pipeline_gabor_2.predict(gabor_x_val_2)
#compute validation accuray 
validation_accuracy_gabor_2=accuracy_score(y_val_small,predictions_2)
print('Validation Accuracy With More Filters Included (48 Filters Now):', validation_accuracy_gabor_2) #We see that the validation accuracy is