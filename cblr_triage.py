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

##########################################################################
#
#  This Python script is used to perform various CB Live Response
#  operations on multiple endpoints simultaneously, using job scheduling.
#
#  Note: This script depends on the modules "triage.py" and "cli.py"
#
#  Optional:
#  -> "hosts.csv" file downloaded from CB Response via browser 
#     present in the script's working directory, if a specific IP,
#     hostname, or "all sensors" is not specified
#
##########################################################################

import os
import csv
import sys
import cli
import triage
import logging
import argparse
import threading
from datetime import date
from concurrent.futures import wait
from dateutil.relativedelta import relativedelta
from cbapi.response.models import Sensor
from cbapi.response import CbEnterpriseResponseAPI

def check_csv_header(csv_dict, args):
    """ Function to check if proper CSV header exists.
    """
    if "id" in csv_dict.fieldnames:
        return "id"
    elif "computer_name" in csv_dict.fieldnames:
        return "computer_name"
    elif "ip" in csv_dict.fieldnames:
        return "ip"
    else:
        print('Please place appropriate column header in "{0}" depending on the following conditions:'.format(args.sensorlist))
        print('1)  id \t\t\t- If the list contains sensor IDs.')
        print('2)  computer_name \t- If the list contains hostnames.')
        print('3)  ip \t\t\t- If the list contains IP addresses.')
        print('Note: If multiple remote endpoints have the same hostname, prefer using the list of sensor IDs.')
        exit()

def path_exists(TriageScript, sensor, nics):
    """ Checks if the output files already exists.
    """
    return (os.path.exists("{5}\\{0}\\{0}_{1}_{2}{3}.{4}"\
                           .format(TriageScript.path, sensor.id, sensor.hostname, nics, TriageScript.ext, triage.ROOT_DIR))\
            or os.path.exists("{5}\\{0}2\\{0}_{1}_{2}{3}.{4}"\
                              .format(TriageScript.path, sensor.id, sensor.hostname, nics, TriageScript.ext, triage.ROOT_DIR)))

def call_triage(cber, TriageScript, sensor, jobs, identifier, nics_flag):
    """ Function to call triage modules.
    """
    if sensor is not None:
        nics = ""
        if nics_flag:
            for nic in sensor.network_interfaces:
                nics = "{0}_{1}_{2}".format(nics, nic.ipaddr, nic.macaddr.replace(":", ""))
        if not path_exists(TriageScript, sensor, nics):
            if 'Windows' in sensor.os:
                if sensor.status == 'Online':
                    j = TriageScript(sensor, nics)
                    job = cber.live_response.submit_job(j.run, sensor.id)
                    if job is not None:
                        jobs.append(job)
                else:
                    tprint("Sensor is offline for host {0} ({1})".format(sensor.hostname, sensor.id))
            else:
                tprint("OS not supported for host {0} ({1})".format(sensor.hostname, sensor.id))
    else:
        tprint('Sensor not found {0}'.format(identifier))

def main():
    """ Main function for standardization.
    """
    parser = cli.parser("Carbon Black Live Response Universal Triage Script.")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    if args.profile:
        cber = CbEnterpriseResponseAPI(profile=args.profile)
    else:
        cber = CbEnterpriseResponseAPI()

    triage.ROOT_DIR = args.profile.upper()
    if not os.path.exists(triage.ROOT_DIR):
        os.mkdir(triage.ROOT_DIR)

    TriageScript = cli.tdict[args.tscript]
    TriageScript.init_check()

    if not os.path.exists("{0}\\{1}".format(triage.ROOT_DIR, TriageScript.path)):
        os.mkdir("{0}\\{1}".format(triage.ROOT_DIR, TriageScript.path))

    jobs = []

    if args.sensorid:
        sensor = cber.select(Sensor, args.sensorid)
        call_triage(cber, TriageScript, sensor, jobs, args.sensorid, args.nics)

    elif args.hostname:
        sensor = cber.select(Sensor).where("hostname:{0}".format(args.hostname)).first()
        call_triage(cber, TriageScript, sensor, jobs, args.hostname, args.nics)

    elif args.ipaddress:
        sensor = cber.select(Sensor).where("ip:{0}".format(args.ipaddress)).first()
        call_triage(cber, TriageScript, sensor, jobs, args.ipaddress, args.nics)

    elif args.allhosts:
        for sensor in cber.select(Sensor):
            call_triage(cber, TriageScript, sensor, jobs, sensor.id, args.nics)

    else:
        if not os.path.isfile(args.sensorlist):
            tprint("File not present - " + args.sensorlist)
            return 0

        csv_dict = csv.DictReader(open(args.sensorlist), delimiter = ',')
        sid = check_csv_header(csv_dict, args)

        for row in csv_dict:
            if "id" in sid:
                sensor = cber.select(Sensor, row[sid])
            elif "computer_name" in sid:
                sensor = cber.select(Sensor).where("hostname:{0}".format(row[sid])).first()
            elif "ip" in sid:
                sensor = cber.select(Sensor).where("ip:{0}".format(row[sid])).first()
            else:
                return 0

            call_triage(cber, TriageScript, sensor, jobs, row[sid], args.nics)

    wait(jobs)

if __name__ == "__main__":
    tprint = triage.tprint
    try:
        main()
    except KeyboardInterrupt:
        tprint('Keyboard interrupt received.')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
