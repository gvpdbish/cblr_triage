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
# Carbon Black Live Response Triage Script CLI Module.
##################################################################

import triage
import argparse

tdict = {'wevtutil'    : triage.GetWevtutilEvent,
         'autoruns'    : triage.RetrieveAutoRuns}

def parser(description):
    """ Standard command line builder.
    """
    parser = argparse.ArgumentParser(description="Carbon Black Live Response Universal Triage Script.")
    
    parser.add_argument("-u", "--cburl", help="CB server's URL.  e.g., http://127.0.0.1 ")
    parser.add_argument("-k", "--apitoken", help="API Token for Carbon Black server.")
    parser.add_argument("-s", "--no-ssl-verify", help="Do not verify server SSL certificate.", action="store_true", default=False)
    parser.add_argument("-p", "--profile", help="Profile to connect.", default="default")
    parser.add_argument("-l", "--sensorlist", help="CSV file containing sensor list.", default="hosts.csv")
    parser.add_argument("-a", "--allhosts", help="Utilize all sensors.", action="store_true", default=False)
    parser.add_argument("-n", "--nics", help="Stores NICs information (IPs and MACs) for each endpoint in the output file names. \
                        NOTE: Don't use this switch if the client uses DHCP.", action="store_true", default=False)
    parser.add_argument("-i", "--sensorid", help="Sensor ID of a remote endpoint.")
    parser.add_argument("-t", "--hostname", help="Hostname of a remote endpoint.")
    parser.add_argument("-d", "--ipaddress", help="IP address of a remote endpoint.")
    parser.add_argument("-v", "--verbose", help="Enable debug logging.", default=False, action='store_true')
    
    subparser = parser.add_subparsers(title='Triage Scripts (Pass one as an argument)', \
                                      description="The list of currently supported operations for the remote endpoints.", \
                                      dest="tscript")
    
    subparser.add_parser('wevtutil', help="Executes wevtutil for Event ID 7045 and retrieve the output in XML format.")
    subparser.add_parser('autoruns', help="Retrieves the autoruns data using Sysinternals tool.")

    return parser