# What is this?

This is the work-in-progress (WIP) repository for the brain-computer
interface API of [Senzing](http://senzing.com).

A [brain-computer interface
(BCI)](http://en.wikipedia.org/wiki/Brain–computer_interface) translates
brain activity into a control signal. It thus holds the promise to
*control things with your thoughts alone!* Although we made quite some
progress, we can't really read your minds. But some signals we can
detect reliably.

To explain the use of this API, we first need to outline several
components that need to work together for the BCI to work.


## The end-user application
Ultimately, we want to control _something_ with our thoughts, for
example a game. Somehow, this game has to be made aware of the state of
our brain. This can be done by asking the IDport server to analyze the
user's current brain activity.


## The pattern recognizer
The analysis of brain activity is done by a series of automatic
detectors, that process incoming
[EEG](http://en.wikipedia.org/wiki/Electroencephalography) signals.
These detectors are trained on lots of example recordings using advanced
machine learning methods. By training we mean that the algorithms
automatically learn to recognize important patterns. Distinguishing for
Senzing's IDport is that we work with _spontaneous_ brain activity, and
that recognize brain activity _without callibration_.

## Headset
We haven't explained where these electrical brain-signals signals come
from. Theses EEG signals can be picked up by sensors placed on your head
that measure the tiny potentials that your brain constantly emits.
Research-grade EEG sets are quite expensive, but cheaper alternatives
aimed at consumers do exist. But generally the quality of the signals is
a bit worse than the research sets.

The most prominent consumers headsets that are the [Emotiv
EPOC](http://www.emotiv.com), the [NeuroSky
MindWave](http://www.neurosky.com) and the [InteraXon
Muse](http://www.interaxon.ca/muse/).


## Fusing the component
The application, the pattern recognizer and the EEG headset have to work
together for the brain-computer interface to work. We have chosen to
build a central web service that can be asked to analyze the users
brain. That is all there exists from the perspective of the application.

For the EEG headset a small driver has to be written that writes
incoming samples to the same web service. As before, this driver only
communicates with the web service.

Finally, behind the scenes, this web service communicates with our
pattern detectors.

The IDPort API facilitates communication between these components.
