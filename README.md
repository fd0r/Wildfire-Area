# Wildfire Area Prediction

_Authors: Corentin Ambroise, Bastien Galmiche, Luis Montero and Margaux Zaffran_

Predicting how much a wildfire is going to expand would be very useful in order to allocate the good number of firefighter, with the appropriate equipment. This could obviously help to reduce the damages, but also to have a better management of the available resources in heavy loaded period, like summer, that are unfortunately going to be more frequent with climate change.

Thus, the goal of this challenge is to predict the total area that is going to burn (or have burnt) when the signal of a start of fire is given.

## Set up

This starting kit obviously requires python, but also needs some libraries:

- pandas
- numpy
- scipy
- matplotlib
- scikit-learn
- geopandas
- shapely
- jupyter
- googledrivedownloader

If you need to install some of them, you can simply execute ```pip install -r requirements.txt``` on your terminal.

## Environment

You will need to install the ramp workflow library. If it is not already done, this is the appropriate command line:
```
pip install git+https://github.com/paris-saclay-cds/ramp-workflow.git
```
Then, follow the [ramp-kits instruction](https://github.com/paris-saclay-cds/ramp-workflow/wiki/Getting-started-with-a-ramp-kit).

## Local submissions

To test a submission, named __my_sub__ for example, the `submissions` folder should contain another folder named __my_sub__, containing 2 scripts python, `feature_extractor.py` and `regressor.py`. Then, you can execute the following command line:
```
ramp_test_submission --submission my_sub
```

So, for example, if you want to test our starting_kit you just have to run:
```
ramp_test_submission --submission starting_kit
```
