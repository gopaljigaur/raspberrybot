import logging
import subprocess
from urllib.request import urlopen

from raspberrybot import config
from raspberrybot.models import Torrent

log = logging.getLogger(__name__)


def system_call_with_response(command):
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) as task:
        output = task.stdout.read()
        task.wait()
        return output.decode("utf-8").strip()


def get_local_ip():
    ips = system_call_with_response('hostname -I')
    return ips


def get_public_ip():
    with urlopen("http://ipecho.net/plain") as f:
        rxval = f.read().decode("utf-8")
        if(len(rxval)>0):
            return rxval
        else:
            return "Could not determine the Public IP"


def get_uptime():
    return system_call_with_response("uptime")


def torrent_add(url):
    command = "transmission-remote -n %s:%s -a '%s'" % (config.TRANSMISSION_USER, config.TRANSMISSION_PASSWORD, url)
    response = system_call_with_response(command)
    log.debug("Response from add torrent: %s", response)
    return response


def torrent_remove(torrent_id):
    command = "transmission-remote -n %s:%s -t %d -i" % \
              (config.TRANSMISSION_USER, config.TRANSMISSION_PASSWORD, int(torrent_id))
    response = system_call_with_response(command)
    if(len(response)==0):
        response = "This torrent does not exist"
    else:
        command = "transmission-remote -n %s:%s -t %d --remove-and-delete" % \
                  (config.TRANSMISSION_USER, config.TRANSMISSION_PASSWORD, int(torrent_id))
        response = system_call_with_response(command)
        log.debug("Response from remove torrent: %s", response)
        if("success" in response):
            response = "Successfully removed torrent"
    return response


def torrent_list():
    command = "transmission-remote -n %s:%s -l" % (config.TRANSMISSION_USER, config.TRANSMISSION_PASSWORD)
    response = system_call_with_response(command)
    log.debug("Response from list torrents: %s", response)

    lines = response.split("\n")[1:-1]  # header in first line, summary in last line
    torrents = []
    for x in lines:
        words = [w.strip() for w in x.split("  ") if w]
        torrents.append(Torrent(*words))
    return torrents


def torrent_info(torrent_id):
    command = "transmission-remote -n %s:%s -t %d -i" % \
              (config.TRANSMISSION_USER, config.TRANSMISSION_PASSWORD, int(torrent_id))
    response = system_call_with_response(command)
    if(len(response)<=0):
        response = "Couldn't get info for this torrent"
    return response
