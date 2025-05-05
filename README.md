# TensorFlowTA

This repository is a prototype project for running mobile instrumentation test automation with the help of TensorFlow for Android. 

The repository contains a sample Python tool for creating and training simple TensorFlow .keras models. In addition a sample Android 
test automation project written in Kotlin is included for using the models in some test automation cases. 

################################################################################

The main points of this entire project are to figure out the following:

- How ML models could be utilized for testing applications.
- What benefits or downsides using them would introduce?
- Is such a solution feasible and more flexible over scripted tests?
- Will this reduce the amount of boilerplate code in a test automation project?

################################################################################

This is by no means meant to be a battle tested TA solution but more of a research and learning effort!

################################################################################

The scripts -folder inside TensorFoundry contains scripts to build a binary using pyinstaller (build.sh) or run directly
inside a generated virtual environment (run.sh). Make sure to grant sufficient permissions for these!

################################################################################

[o_o] The repository is still taking shape and support is being added for different OS... - WIP!
