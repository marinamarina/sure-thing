![SureThing version number](https://img.shields.io/badge/version-0.1.0-lightgrey.svg) [![Build Status](https://magnum.travis-ci.com/marinamarina/sure-thing.svg?token=mjEQw6pBznfzG3bFcBry&branch=master)](https://magnum.travis-ci.com/marinamarina/sure-thing)
[![Dependency Status](https://www.versioneye.com/user/projects/54eba57748b34132bb000002/badge.png)](https://www.versioneye.com/user/projects/54eba57748b34132bb000002)


# Football Prediction Application
This repository contains the codebase for my Major Project (i.e. dissertation) at Robert Gordon University, and is currently a work in progress.

## Overview

The project aims to build a web application simulating football betting experience, addressing two main issues. Firstly, filling an existing void of a system that makes football match prediction customisable and transparent to the user. For each upcoming match the application will provide user with a overall prediction expressed in a probability of either of two teams winning the match. User would be able to adjust this prediction outcome by changing the weights of the factors that contributed to that result. Depending on the values of the weights, the system may deliver a different outcome to various users. In the longterm, users of the web application would be able to create their own "betting system" by keeping adjusting the default weights for each contributing factor. Secondly, allowing the users to analyse their past performance and compare their results and prediction weights with the other users of the application. 

The stated above would be achieved by taking several steps. On completion of a background research, 
current football prediction web applications will be researched and a set of requirements will be produced to assess users’ needs. After that a layout and overall design of the application will be produced, as well as the desired behavior of its features. Once the prototyping is completed, the main project deliverable, i.e. working web application will be produced and throughly tested. 

## Pre-requisites

* Python (version >= 2.7)

## Installation

Note: all of the commands in the rest of this README are relative to the root of the repository. Therefore, when you've downloaded the repo, make sure you `cd surething` to go into the top level of the repository.

* download repository
* install dependencies with pip (`pip install -r requirements.txt`)
* create production database: `sqlite3 data/production.db < data/db.sql`

to do...

## Deployment

* run `python manage.py runserver`
* go to http://localhost:5000/ in your browser
* you should now be able to register an account and log in using the forms provided

...to be completed

## Running tests

Run the unit tests:

run `python manage.py test`


Please see my [SureThing website](http://www.surething.click/) to see the working application. 

## License
This project is free and released as open source software covered by the terms of the [GNU Public License](http://www.gnu.org/licenses/gpl-3.0.html) (GPL v3). You may not use the software, documentation, and samples exc

