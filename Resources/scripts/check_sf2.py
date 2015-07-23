#!/usr/bin/python

import nagiosplugin
import argparse

import urllib2
import simplejson

"""

A simple check script for use with LiipMonitorBundle to monitor symfony apps.

Usage:

1. Place the script in your nagios plugin dir (or define a custom one)

2. Nagios config:
define command{
        command_name    check_symfony_health
        command_line    $USER1$/check_symfony2.py -w 0  -c 0 -u https://$HOSTNAME$
}

3. Restart nagios.

4. Profit.

5. Forgo profit as you just realized you are missing the nagiosplugin module.

To remedy the situation, do:
    pip install nagiosplugin


Author: Tarjei Huse, tarjei.huse@gmail.com

"""

class Symfony2Check(nagiosplugin.Resource):
    name = "Symfony2 health check"
    version = "2.0"
    username = None
    url = None
    hostUrl = None
    warning = None
    critical = None

    def __init__(self, args):
        self.warning = args.warning.rstrip('%')
        self.critical = args.critical.rstrip('%')
        if not args.url:
            raise Exception("Missing url option")
        self.url = args.url.strip()  + "/monitor/health/run"
        self.hostUrl = args.url.strip()
        if args.auth is not None:
            self.username, self.password = options.auth.split(":")
        else:
            self.username = None

    def probe(self):
        self.badChecks = []
        try:
            content = self.fetchResult()
            json = simplejson.loads(content)

            if json['globalStatus'] is not 'OK':
                self.badChecks = []
                for check in json['checks']:
                    if check['status']:
                        self.badChecks.append(check["checkName"])

        except Exception, e:
            self.badChecks.append("config_error_in_nagios")
            raise

        self.measures = [nagiosplugin.Metric("Num_failed_checks", len(self.badChecks), min=0, context="sf2" )]
        return self.measures
        
    def fetchResult(self):
        if self.username is not None:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            # this creates a password manager
            passman.add_password(None, self.url, self.username, self.password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
            urllib2.install_opener(opener)
        handle = urllib2.urlopen(self.url)
        data = handle.read()
        return data

def main():
    optparser = argparse.ArgumentParser(description='Health check of Symfony2 application')
    optparser.version = '1.0'
    optparser.add_argument(
      '-w', '--warning', default='1', metavar='RANGE',
      help='warning threshold (default: %default%)')
    optparser.add_argument(
      '-c', '--critical', default='1', metavar='RANGE',
      help='warning threshold (default: %default%)')
    optparser.add_argument(
      '-u', '--url', help='Url to check')
    optparser.add_argument(
      '-a', '--auth', help='Authentication', default=None)
    args = optparser.parse_args()
    check = nagiosplugin.Check(
        Symfony2Check(args),
        nagiosplugin.ScalarContext('sf2', args.warning, args.critical)) 
    check.main()

if __name__ == '__main__':
   main()
