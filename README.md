[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)


# pkg_tracker

`pkg_tracker` continuously update the package installed with pip.
Although it works only on CircleCI now, but I want to make this package work fine on other CI tool eventually.

## Installation
```
pip install pkg-tracker
```

## Prerequisites
This package currently works only with circleci　workflow.


## Usage
### Setting
### Getting your Github access token.
1. access your [developer setting page](https://github.com/settings/depelopers).
2. click `Personal access tokens` tab.
3. you can generate personal access tokens.

### CircleCI Setting
After you get Github personal access token, add this token as an environment GITHUB_ACCESS_TOKEN in CircleCI.

### Change your circleci.yml
for example:
```
version: 2
jobs:
  build:
    # [...]
    update_requirements:
    docker:
      - image: circleci/python:3.6.2
    steps:
      - checkout
      - run:
          name : update_requirements
          command: |
            python -m venv .venv
            source .venv/bin/activate
            pip install pkg-tracker
            pkgtrack

workflows:
  version: 2
  build:
    jobs:
      - build:
          # [...]
  nightly:
    triggers:
      - schedule:
          cron: "00 10 * * 5"
          filters:
            branches:
              only: master
    jobs:
      - update_requirements
```

### Command line argument
### The first argument
The first argument is the branch name you want this command.
Such like this, 
```
pkg-tracker master,feature-foo,feature-bar
```
Default is only master.

### The second argument
The second argument is the branch name merged the commit into.
Such like this, 

```
pkg-tracker master develop,stg
```


## Contributing
Welcome.
if you notice bug, please create issue.
when you want to contribute, please open pull request.
