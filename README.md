# tcx_relaps
Replace laps for Garmin tcx file.

## Purpose
An interval workout is done with some interval (like 400m), and Garmin defaults to 1 mile laps.  The result is the intervals are mixed with the recovery and averaged for the 1 mile lap.

## Usage
Download the workout from the Garmin website in tcx format.  Create a pyenv and download tcx.py.  Do this:

`python tcx.py <your_activity>.tcx > <updated_activity>.tcx`

Then go back to the Garmin website and upload the tcx.

## Limitations
This is a quick thing with some hard-coded stuff (like 400m is the desired lap distance) that worked in one case.  It likely lost some info and perhaps calculated things a bit fudgey.  It's a starting point.
