#   Copyright 2017, 2018 - Kroll
#   All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

##################################################################
# Carbon Black Live Response Triage Script Module.
##################################################################

import os
import csv
import sys
import time
import json
import struct
import shutil
import binascii
from datetime import datetime, timedelta
from cbapi.live_response_api import LiveResponseError
from cbapi.response.models import Binary, Sensor, SensorGroup

ROOT_DIR = "DEFAULT"
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))+"\\"


def tprint(string):
    """ Wrapper function to print strings along with UTC date and time.
    """
    print("{0} - {1}".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), string))


class GetWevtutilEvent(object):
    """ Retrieve wevtutil 7045 events.
    """
    path = "Wevtutil"
    command = 'cmd /c wevtutil qe System "/q:*[System [(EventID=7045)]]" /f:xml'
    ext = "xml"

    def __init__(self, sensor, nics):
        """ Standard constructor
        """
        self.hostname = sensor.hostname
        self.os = sensor.os
        self.nics = nics

    @staticmethod
    def init_check():
        """ The static method to check class's initial requirements.
        """
        return

    def run(self, session):
        """ Function to execute commands on remote endoint.
        """
        if 'XP' not in self.os or '2000' not in self.os or '2003' not in self.os:
            tprint("Executing command <{0}> for host {1} ({2})".format(GetWevtutilEvent.command, self.hostname, session.sensor_id))
            try:
                cmd_data = session.create_process(GetWevtutilEvent.command, wait_timeout=300, wait_for_completion=True)
                session.close()
                self.print_result(session.sensor_id, cmd_data)
            except LiveResponseError:
                session.close()
                self.print_result(session.sensor_id, None)
        else:
            return 0

    def print_result(self, sensor_id, output):
        """ Function to print/retrieve results on this system.
        """
        if output is not None:
            open("{5}\\{0}\\{0}_{1}_{2}{3}.{4}"\
                 .format(GetWevtutilEvent.path, sensor_id, self.hostname, self.nics, GetWevtutilEvent.ext, ROOT_DIR), 'wb').write(output)

        tprint("Retrieved wevtutil events for sensor {1} ({0})".format(sensor_id, self.hostname))


class RetrieveAutoRuns(object):
    """ Retrieves autoruns from the remote endpoints.
    """
    path = "Autoruns"
    command = r'cmd /c "autorunsc.exe -accepteula -nobanner -a * -c -h -s -t * > autoruns.csv"'
    binary = r'autorunsc.exe'
    ext = "csv"

    def __init__(self, sensor, nics):
        """ Standard constructor.
        """
        self.hostname = sensor.hostname
        self.nics = nics

    @staticmethod
    def init_check():
        """ The static method to check class's initial requirements.
        """
        if not os.path.isfile('Dependencies/'+RetrieveAutoRuns.binary):
            tprint("File doesn't exist: %s" % RetrieveAutoRuns.binary)
            exit()

    def run(self, session):
        """ Function to execute commands on remote endoint.
        """
        tprint("Uploading binaries at host {0} ({1})".format(self.hostname, session.sensor_id))
        try:
            with open('Dependencies/'+RetrieveAutoRuns.binary, 'rb') as tfile:
                try:
                    session.put_file(tfile.read(), RetrieveAutoRuns.binary)
                except LiveResponseError:
                    pass

            tprint("Executing command <{0}> at host {1} ({2})".format(RetrieveAutoRuns.command, self.hostname, session.sensor_id))
            session.create_process(RetrieveAutoRuns.command, wait_timeout=900, wait_for_completion=True)

            self.print_result(session)
            self.cleanup(session)
            session.close()

        except LiveResponseError:
            self.cleanup(session)
            session.close()

    def cleanup(self, session):
        """ Cleanup module.
        """
        tprint("Deleting binaries from host {0}.".format(self.hostname))

        try:
            session.delete_file(RetrieveAutoRuns.binary)
        except LiveResponseError:
            pass

    def print_result(self, session):
        """ Function to print/retrieve logs on this system.
        """
        open("{5}\\{0}\\{0}_{1}_{2}{3}.{4}".\
             format(RetrieveAutoRuns.path, session.sensor_id, self.hostname, self.nics, RetrieveAutoRuns.ext, ROOT_DIR), 'wb')\
                   .write(session.get_file("autoruns.csv").decode('utf-16-le').encode('utf-8'))

        tprint("Retrieved autoruns from sensor {1} ({0})".format(session.sensor_id, self.hostname))