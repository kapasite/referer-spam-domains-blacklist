Referer Spam Blacklist
======================

[![Checks](https://img.shields.io/travis/desbma/referer-spam-domains-blacklist/master.svg?label=checks&style=flat)](https://travis-ci.org/desbma/referer-spam-domains-blacklist)

This is a frequently updated list of [referer spam domains](http://en.wikipedia.org/wiki/Referer_spam).

This repository is a fork of [Piwik's referrer spam blacklist](https://github.com/piwik/referrer-spam-blacklist), with the following main differences:

* Domains are added more frequently to keep up with the spammers (Piwik's list [requires](https://github.com/piwik/referrer-spam-blacklist/issues/26#issuecomment-125881499) a vote and a pull request per added domain, which slows down the update, and prevents [automatic updating](https://github.com/piwik/referrer-spam-blacklist/pull/87))
* Piwik's list changes are merged back regularly in this repository
* Large lists of confirmed referer spam domains from other contributors or projects are also merged back
* Dead domains are regularly removed from the list

As a result this list is **more than 5 times larger** (as of this writing) than Piwik's list.


## List format

The list is stored in this repository in [`spammers.txt`](https://raw.githubusercontent.com/desbma/referer-spam-domains-blacklist/master/spammers.txt), with one host per line, and Unix line endings.

Parsing the file should be pretty easy using your favorite language.

### Subdomains

Sub-string matching on domain names can be done with this list, so `semalt.com` is enough to block all subdomain referers too, such as `semalt.semalt.com`.

However, there are cases where you'd only want to add a subdomain but not the root domain. For example, add `refererspammer.tumblr.com` but not `tumblr.com`, otherwise all `*.tumblr.com` sites would be affected.

On the contrary, if you get spam with referer `www.domain.com`, you can safely assume that all `domain.com` subdomains are spam.

### Sorting

To make duplicate detection, and merges easier, the list is sorted with [Unix's sort](https://en.wikipedia.org/wiki/Sort_(Unix)), with the command:

`sort -uf -o spammers.txt spammers.txt`


## Usage with Fail2ban

This list can be used with [Fail2ban](http://www.fail2ban.org/wiki/index.php/Main_Page).

A [script](https://github.com/desbma/referer-spam-domains-blacklist/blob/master/update-fail2ban-referer-filter) is provided to automatically generate or update a filter (located in `/etc/fail2ban/filter.d/apache-referer.local`) that will watch Apache logs, and automatically ban IPs that send HTTP requests with a domain in the blacklist as referer.

It is recommended to run the script at least every week with cron, to keep the list up to date:

    curl https://raw.githubusercontent.com/desbma/referer-spam-domains-blacklist/master/update-fail2ban-referer-filter > /etc/cron.weekly/update-fail2ban-referer-filter
    chmod +x /etc/cron.weekly/update-fail2ban-referer-filter

You also need to edit `/etc/fail2ban/jail.local`, to locate the Apache logs, and configure ban time, eg.:

    [apache-referer]
    enabled = true
    maxretry = 1
    # 90 days
    bantime = 7776000
    port = http,https
    filter = apache-referer
    logpath = /var/log/apache*/*access.log

Then, run the script a first time to generate the filter:

    /etc/cron.weekly/update-fail2ban-referer-filter


## Contributing

Although the list is mostly updated by automated scripts, **contributions to the list are welcome**.

To add domain(s) either [open an issue]((https://github.com/desbma/referer-spam-domains-blacklist/issues/new)) or submit a pull request. The latter is prefered for large additions.
Either way, please **explain how you have found the referer domain(s)** (it is important to avoid false positives).

If you think a hostname was added but is not actually a spam domain, please open an issue.


## License

[WTFPLv2](http://www.wtfpl.net/txt/copying/)
