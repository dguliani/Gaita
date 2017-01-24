# Gaita

## Electrical/Hardware Documentation

In order to be able to successfully use/change the schematics, ensure first that you have:

1. Installed Eagle
2. Cloned the repository to a local location

Having done those two things, there are a few modifications that may need to be made to ensure all the utlized libraries can be loaded on Eagle. First:

1. Open/Launch Eagle
2. Go to File -> Options -> Directories

You will notice that the paths for each of the various Eagle categories are set up here, for things like Libraries, Documentation, Design Rules and Projects. The two primary paths that will need modifications will be Libraries and Projects.

### Projects

Add the local path to the soleful directory in this repository by either appending the currently given path on Eagle with a colon (:) on Mac, or a semi-colon (;) on Windows. The resulting path may look like this:

`$EAGLEDIR/projects/examples:$HOME/<path-to-locally-cloned-git-repo>/eagle/soleful`

### Libraries

Similarly, this project uses the following Libraries:

1. SparkFun Eagle Libraries (https://github.com/sparkfun/SparkFun-Eagle-Libraries)
2. Pyboard Eagle (https://github.com/micropython/pyboard)
3. Adafruit BNO055 Library (https://github.com/adafruit/Adafruit-BNO055-Breakout-PCB)
4. Adafruit Eagle Library (https://github.com/adafruit/Adafruit-Eagle-Library)

Each of these libraries should be in the libraries folder of this repository, so append the path to each of these folders following a similar fashion as above in Eagle. An example is below:

`$EAGLEDIR/lbr:$HOME/<path-to-locally-cloned-git-repo>/eagle/libraries/SparkFun-Eagle-Libraries-master:<so on for each library>`

## Using Eagle

Follow the tutorials below to get a good sense of how to use Eagle, and it's various different functions.

1. Schematic (https://learn.sparkfun.com/tutorials/using-eagle-schematic)
2. Layout (https://learn.sparkfun.com/tutorials/using-eagle-board-layout) 
