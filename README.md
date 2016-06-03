# Potato
> You can't judge a book by its potato.

## What Potato does
Potato is a log files analyser.

Potato scans a log file and it classifies every line according to its likelihood, which is calculated through a simple
machine-learning-based prediction model.

Log lines are marked as:
- ```EXPECTED``` if the model predicts the line occurrence with likelihood between 75% and 100%;
- ```COMMON``` if 50% < likelihood <= 75%;
- ```UNUSUAL``` if 25% < likelihood <= 50%;
- ```WARNING``` if 5% < likelihood <= 25%;
- ```POTATO!``` if the likelihood is equals to 5% or below;
- ```SKIP``` if the line cannot be processed.


## What Potato is
According to [Wikipedia page on Log Analysis](https://en.wikipedia.org/wiki/Log_analysis), *Artificial Ignorance* is

> [...] a type of machine learning which is a process of discarding log entries which are known to be
> uninteresting. Artificial ignorance is a method to detect the anomalies in a working system.
> In log analysis, this means recognizing and ignoring the regular, common log messages that result from the normal
> operation of the system, and therefore are not too interesting.

Potato is therefore an Artificial Ignorance tool, which goal is to ease the pain of analysing large log files for
troubleshooting.

The idea behind Potato is pretty simple: identify the most relevant part of a log file -- i.e. anomalies -- so to ignore
the "noise" produced by the regular execution.

## How it works
Potato uses Markov Chains to build a model and predict the occurrence of a line in the file.

More info on Markov Chains can be found on [Wikipedia](https://en.wikipedia.org/wiki/Markov_chain).
A nice graphical explaination of Markov Chains models can be found [here](http://setosa.io/blog/2014/07/26/markov-chains/).

#### Markov Chain states
To process a log line, it's necessary to map it to a corresponding state of the Markov Chain.

In Potato, this mapping is implemented applying a regular-expression to the log line. If the line matches the regex, then
all the defined groups, toghether, are the corresponding state in the chain.

From the user standpoint, the regular-expression is also a tool used to select only the relevant info from a possibly large
log line. In fact, the regular expression should aim at selecting only the information required to identify the "business"
action, ignoring any technical detail.

##### Example
Given a log file with traces like this:
```
03:02:38:359|1100-00162:MYLIBRARY: Subscription {INFO} Action {Update} Pattern {PATTERN_NAME.} Snapshot {false} Record {PATTERN_NAME.XYZ} Code {123456} Value1 {1.25} Value2 {USD} Value3 {4321} Desc {The description} Id {XYZ} Thread {MyThread(my.test.stuff.com:24017)}
```
The following regular expression
```
\d+:\d+:\d+:\d+\|\d+-\d+:(\S+):\s*(\S+).+Action (\S+).+$
```
can be used to extract only those sub-strings that identify the business action described by the trace.

The corresponding state in the Markov Chain would be the tuple ```('MYLIBRARY', 'Subscription', 'Update')```

#### Markov Chain order
Potato supports *Markov Chains of order m* (see [Markov Chain Variations](https://en.wikipedia.org/wiki/Markov_chain#Variations) on Wikipedia).

When the order is set to ```m > 1```, every state of the Markov Chain is the concatenation of (the last) ```m``` states.
Nothing changes in the way the information are extracted from the log file.

Increasing the chain order "gives more memory" to the model and makes the outcome less affected by small variations in
the input.


## How to use it
Commands supported by Potato:
- ```init```: Initialize a new Potato analyser
- ```learn```: Read file and acquire new knowledge
- ```tag```: Tag each line according to its likelihood

Type ```python potato.py -h``` or ```python potato.py <command> -h```  to get the usual help messages.

#### Command: ```init```
Create a new instance of Potato analyser. Each instance is bound to a knowledge file (by default ```./potato.kb```)
that is used to store all the acquired data.
* The regular expression, needed to extract the info from the log lines, must be passed here as a parameter.
* Markov Chain order higher than one can be set on init.

#### Command: ```learn```
Load a Potato analyser instance and train it.
Use a "regular" log file to show the model how a "regular" log file should look like.
* The knowledge file is updated with the newly acquired knowledge.

#### Command: ```tag```
Load a Potato analyser instance and process a log file.
* Output is written on the standard output, so you may want to redirect it to a file.
* The tag and the likelihood of every trace are *appended* at the end of the line.
* The knowledge file is not updated in this case.

