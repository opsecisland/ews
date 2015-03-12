# dockerized ewsposter


[ewsposter](https://github.com/dtag-dev-sec/ews) is a python application that collects information from multiple honeypot sources and posts it to central collection services like the DTAG early warning system and hpfeeds. 

This repository contains the necessary files to create a *dockerized* version of ewsposter. 

This dockerized version is part of the **[T-Pot community honeypot](http://dtag-dev-sec.github.io/)** of Deutsche Telekom AG. 

The `Dockerfile` contains the blueprint for the dockerized ewsposter and will be used to setup the docker image.  

The `ews.cfg` is tailored to fit the T-Pot environment. All important data is stored in `/data/ews/`.

The `supervisord.conf` is used to start ewsposter under supervision of supervisord. 

Using upstart, copy the `upstart/ews.conf` to `/etc/init/ews.conf` and start using

    service ews start

This will make sure that the docker container is started with the appropriate rights and port mappings. Further, it autostarts during boot.
