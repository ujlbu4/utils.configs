#!/usr/bin/env bash
########################
# Step 1: Setup virtualenv
# This step is only for Jenkins. Travis and CircleCI will ignore this step.
########################
if [ ! -d "venv" ]; then
    python3 -m venv ./venv1
fi
. venv/bin/activate

########################
# Step 2: Execute Test
########################
#nosetests --with-xunit --all-modules --traverse-namespace --with-xcoverage --cover-package=me.maxwu --cover-inclusive --logging-level=INFO --debug=me.maxwu -s -v --xunit-file ci-stat_nose_xunit.xml --cover-html ./test
python -m pytest ./
#EOF