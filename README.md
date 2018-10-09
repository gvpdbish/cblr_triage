Copyright 2017, 2018 - Kroll

All Rights Reserved

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Introduction

This repository contain scripts for forensic triage activities using Carbon Black Live Response. 

## Prerequisites

You will need to install the following before executing the scripts:

* [Python 2.7.*](https://www.python.org/downloads/) - Python installer
* pip (https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip)
* pip install cbapi

## Development

These scripts can be adapted to perform different tasks using very minimal modifications.

Basically, the functionalities for each script has been broken into following four steps:

* **Initialization** - The class objects are created in this step.
* **Execution** - The connections are established with the remote endpoints and the commands are executed.
* **Retrieval** - The data is pulled back from the remote endpoints and stored locally.
* **Cleanup** - The leftover proprietary binaries that were used in the tasks are cleaned up from the remote endpoints.
