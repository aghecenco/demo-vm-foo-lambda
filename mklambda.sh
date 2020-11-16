#!/bin/bash

rm -f ../myDeploymentPackage.zip
zip -r ../myDeploymentPackage.zip . -x '*.git*'
