#!/bin/bash

rsync -r --exclude='.git/' . ehanelt@kratos2.ethz.ch:metaGclub/
