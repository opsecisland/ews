#!/usr/bin/env python

import ConfigParser
import socket
import argparse
import os
import sys
from moduls.elog import logme
from moduls.etoolbox import readcfg, readonecfg

def ecfg(name,version):
    MODUL = "EINIT"

    ECFG= {}

    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--configpath", help="Load configuration file from Path")
    parser.add_argument("-v","--verbose", help="set output verbosity",action="store_true")
    parser.add_argument("-d","--debug", help="set output debug",action="store_true")
    parser.add_argument("-s","--silent", help="silent mode without output",action="store_true")
    parser.add_argument("-S","--sendonly", help="only send unsend alerts",action="store_true")
    parser.add_argument("-E","--ewsonly", help="only generate ews alerts files",action="store_true")
    parser.add_argument("-dcr","--daycounter", help="reset and log daycounters for all honeypots",action="store_true")
    parser.add_argument("-V","--version", help="show the EWS Poster Version",action="version", version=name + " " + version)

    args = parser.parse_args()

    if args.verbose:
        ECFG["a.verbose"] = True
    else:
        ECFG["a.verbose"] = False
 
    if args.debug:
        ECFG["a.debug"] = True
    else:
        ECFG["a.debug"] = False

    if args.silent:
        ECFG["a.silent"] = True
    else:
        ECFG["a.silent"] = False

    if args.daycounter:
        ECFG["a.daycounter"] = True
    else:
        ECFG["a.daycounter"] = False

    if args.sendonly:
        ECFG["a.sendonly"] = True
    else:
        ECFG["a.sendonly"] = False

    if args.ewsonly:
        ECFG["a.ewsonly"] = True
    else:
        ECFG["a.ewsonly"] = False

    if args.configpath:
        ECFG["path2"] = args.configpath

        if os.path.isdir(args.configpath) is not True:
            logme(MODUL,"ConfigPath %s did not exist. Abort !" % (args.configpath),("P1","EXIT"),ECFG)
    else:
        ECFG["path2"] = ""

    # say hello

    logme(MODUL,name + " " + version + " (c) by Markus Schroer <markus.schroer@telekom.de>\n",("P0"),ECFG)

    # read EWSPoster Main Path

    ECFG["path"] = os.path.dirname(os.path.abspath(__file__)).replace("/moduls","")

    if ECFG["path2"] == "":
        ECFG["path2"] = ECFG["path"]

    if os.path.isfile(ECFG["path2"] + os.sep + "ews.cfg" ) is False:
        logme(MODUL,"Missing EWS Config %s. Abort !"%(ECFG["path2"] + os.sep + "ews.cfg"),("P1","EXIT"),ECFG)
    else:
        ECFG["cfgfile"] = ECFG["path2"] + os.sep + "ews.cfg"

    # Create IDX File if not exist

    if os.path.isfile(ECFG["path"] + os.sep + "ews.idx" ) is False:
        os.open(ECFG["path"] + os.sep + "ews.idx", os.O_RDWR|os.O_CREAT )
        logme(MODUL,"Create ews.idx counterfile",("P1"),ECFG)

    # Read Main Config Parameter

    ITEMS = ("homedir","spooldir","logdir","contact","del_malware_after_send","send_malware","sendlimit")
    MCFG = readcfg("MAIN",ITEMS, ECFG["cfgfile"])

    # IP Handling

    ewsip = ECFG["path2"] + os.sep + "ews.ip"

    MCFG["ip"] = readonecfg("MAIN","ip", ECFG["cfgfile"])

    if os.path.isfile(ewsip) is True:
        MCFG["ip"] = readonecfg("MAIN","ip", ewsip)
        if MCFG["ip"].lower() == "null":
             logme(MODUL,"Error IP Address in File " + ewsip + " not set. Abort !",("P1","EXIT"),ECFG)

    if MCFG["ip"].lower() == "null" or MCFG["ip"].lower() == "false":
        logme(MODUL,"Error IP Address in ews.cfg not set or null. Abort !",("P1","EXIT"),ECFG)

    # sendlimit expect

    if int(MCFG["sendlimit"]) > 400:
        logme(MODUL,"Error Sendlimit " + MCFG["sendlimit"] + " to high. Max 400 ! ",("P1","EXIT"),ECFG)
    elif int(MCFG["sendlimit"]) < 1:
        logme(MODUL,"Error Sendlimit " + MCFG["sendlimit"] + " to low. Min 1 ! ",("P1","EXIT"),ECFG)
    elif MCFG["sendlimit"] == "NULL" or MCFG["sendlimit"] == "UNKNOW":
        logme(MODUL,"Error Sendlimit " + MCFG["sendlimit"] + " Must set between 1 and 400. ",("P1","EXIT"),ECFG)

    # send_malware ?

    if MCFG["send_malware"].lower() == "true":
        MCFG["send_malware"] = True
    else:
        MCFG["send_malware"] = False

    # del_malware_after_send ?

    if MCFG["del_malware_after_send"].lower() == "true":
        MCFG["del_malware_after_send"] = True
    else:
        MCFG["del_malware_after_send"] = False

    # home dir available ?

    if os.path.isdir(MCFG["homedir"]) is not True:
        logme(MODUL,"Error missing homedir " + MCFG["homedir"] + " Abort !",("P1","EXIT"),ECFG)
    else:
        os.chdir(MCFG["homedir"])

    # spool dir available ?

    if os.path.isdir(MCFG["spooldir"]) is not True:
        logme(MODUL,"Error missing spooldir " + MCFG["spooldir"] + " Abort !",("P1","EXIT"),ECFG)

    # log dir available ?

    MCFG["logdir"] = readonecfg("MAIN","logdir", ECFG["cfgfile"])

    if MCFG["logdir"] != "NULL" and MCFG["logdir"] != "FALSE" and os.path.isdir(MCFG["logdir"]) is True:
        MCFG["logfile"] = MCFG["logdir"] + os.sep + "ews.log"
    elif MCFG["logdir"] != "NULL" and MCFG["logdir"] != "FALSE" and os.path.isdir(MCFG["logdir"]) is True:
        logme(MODUL,"Error missing logdir " + MCFG["logdir"] + " Abort !",("P1","EXIT"),ECFG)
    else:
        MCFG["logfile"] = "/var/log" + os.sep + "ews.log"

    # Proxy Settings ?

    MCFG["proxy"] = readonecfg(MODUL,"proxy", ECFG["cfgfile"])

    # Read EWS Config Parameter

    ITEMS = ("ews","username","token","rhost_first","rhost_second")
    EWSCFG = readcfg("EWS",ITEMS, ECFG["cfgfile"])

    # Set ews real true or false

    if EWSCFG["ews"].lower() == "true":
       EWSCFG["ews"] = True
    else:
       EWSCFG["ews"] = False

    # Read HPFEED Config Parameter 

    ITEMS = ("hpfeed","host","port","channels","ident","secret")
    HCFG = readcfg("HPFEED",ITEMS, ECFG["cfgfile"])

    if HCFG["hpfeed"].lower() == "true":
       HCFG["hpfeed"] = True
    else:
       HCFG["hpfeed"] = False

    # Read EWSJSON Config Parameter

    ITEMS = ("json","jsondir")
    EWSJSON = readcfg("EWSJSON",ITEMS, ECFG["cfgfile"])

    if EWSJSON["json"].lower() == "true":
       EWSJSON["json"] = True
    else:
       EWSJSON["json"] = False

    if EWSJSON["jsondir"] != "NULL" and  EWSJSON["jsondir"] != "FALSE" and os.path.isdir(EWSJSON["jsondir"]) is True:
         EWSJSON["jsondir"] =  EWSJSON["jsondir"] + os.sep + "ews.json"
    else:
        logme(MODUL,"Error missing jsondir " + EWSJSON["jsondir"] + " Abort !",("P1","EXIT"),ECFG)

    ECFG.update(MCFG)
    ECFG.update(EWSCFG)
    ECFG.update(HCFG)
    ECFG.update(EWSJSON)

    return ECFG


def locksocket(name):

    # create lock socket

    global lock_socket

    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        lock_socket.bind('\0' + name)
        return True
    except socket.error:
        return False

def daycounterreset(lock,ECFG):

    if lock == False:
        logme("ARGCHK","Lock Socket is busy ...",("P1"),ECFG)
        logme("ARGCHK","Waiting 300 seconds for getting lock socket.",("P1"),ECFG)
        for i in range(6000):
            if locksocket() == False:
                time.sleep(0.1)
            else:
                break
        if locksocket() == False:
            logme("daycounterreset","Daycounterreset fails. Socket over 300 sec busy",("P1","LOG"),ECFG)
            sys.exit(0)

    z = ConfigParser.RawConfigParser()
    z.read(ECFG["homedir"] + os.sep + "ews.idx")

    for i in z.sections():
        if z.has_option(i,"daycounter") == True:
            logme("daycounterreset","Daycounter " + i + " : " + z.get(i,"daycounter") + " alerts send." ,("LOG"),ECFG)
            z.set(i,"daycounter",0)

    with open(ECFG["homedir"] + os.sep + "ews.idx", 'wb') as countfile:
        z.write(countfile)
        countfile.close

    logme("daycounterreset","Daycounters successfull reset.",("P1"),ECFG)
    sys.exit(0)


if __name__ == "__main__":
    pass
