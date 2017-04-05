# Table of Contents

* [How to use](README.md#how-to-use)
* [Requirements](README.md#requirements)
* [My goals and features](README.md#goal-in-my-code)
* [Personal Notes](README.md#personal-notes)
* [UML](README.md#basic-uml)
* [Event and Error Log files](README.md#log)
* [Sanitizing data](README.md#sanitizing-data)
* [Testing](README.md#sanitizing-data)
* [Personal notes](README.md#sanitizing-data)
* [TODOS](README.md#future-ideas)

## How to use

From root folder run as:

`$ ./run.sh`

or with custom parameters

`$ ./run.sh ./log_input/log.txt ./log_output/hosts.txt ./log_output/hours.txt ./log_output/resources.txt ./log_output/blocked.txt`


This code includes a test suite which can be use running:

`$ cd ./insight_testsuite execute`

`$ ./run_test.sh`

### Parameters

 `run.sh` expects 5 parameters which are files. If parameters are not specified default ones will be used

 * **./log_input/log.txt**. HTTP server log file with the following contents:
    * *host* making the request. A hostname when possible, otherwise the Internet address if the name could not be looked up.

    * *timestamp* in the format [DD/MON/YYYY:HH:MM:SS -0400], where DD is the day of the month, MON is the abbreviated name of the month, YYYY is the year, HH:MM:SS is the time of day using a 24-hour clock. The timezone is -0400.

    * *request* given in quotes.

    * *HTTP* reply code

    * *bytes* in the reply. Some lines in the log file will list - in the bytes field. For the purposes of this challenge, that should be interpreted as 0 bytes.

 * **./log_output/hosts.txt**
    * Output of feature 1
 * **./log_output/hours.txt**
    * Output of feature 2
 * **./log_output/resources.txt**
    * Output of feature 3
 * **./log_output/blocked.txt**
    * Output of feature 4

## Requirements

In order to run this code you need the follwing libraries

```
iconv:  1.11
python: 3.5.1.final.0
```

## Goal in my code

This library uses Python dictionaries and uses a custom ordered linked list to satisfy the following features.

### Feature 1

List the top 10 most active host/IP addresses that have accessed the site.

### Feature 2

Identify the 10 resources that consume the most bandwidth on the site

### Feature 3

List the top 10 busiest (or most frequently visited) 60-minute periods

### Feature 4

Detect patterns of three failed login attempts from the same IP address over 20 seconds so that all further attempts to the site can be blocked for 5 minutes. Log those possible security breaches.

## Basic UML

Basic UML sequence diagrams created via PlantUML in order to make them version-able.
@see ./features/uml/*.puml
@todo upload this part

## Log

@see ./log_output/event-log.txt` file for important events

## Sanitizing data

* run.sh will take care of cleaning the HTTP log file.

    * *why?* Optionally we could assume the input log file has a specific charset (such as ASCII or UTF-8) but what if the charset is not respected? (Requests could have weird characters if not sanitized beforehand ). This will avoid Python exceptions.

* Optionally lines in file will be reported into *./log_output/results.txt* @todo missing this.


##Testing

`./insight_testsuite/run_tests.sh`

##Personal notes

* Using regular Python hash tables to hold data from log file
* Using a custom ordered linked list for feature 1, feature 2, feature 3 and feature 4
* Alternatively, I was tempted to use Python collections, dictionaries and numpy to sort data easily. However, custom Data Structures are provided


## References


## Future ideas

I have several @todos in the code and they are explained here:

