Referer Spam Blacklist
======================

This is a community-contributed list of [referer spam domains](http://en.wikipedia.org/wiki/Referer_spam)

This repository is a fork of [Piwik's referrer spam blacklist](https://github.com/piwik/referrer-spam-blacklist), with the following main highlights:

* Domains are added more frequently to keep up with the spammers (Piwik's list [requires](https://github.com/piwik/referrer-spam-blacklist/issues/26#issuecomment-125881499) a vote and a pull request per added domain, which slows down the update, and prevents [automatic updating](https://github.com/piwik/referrer-spam-blacklist/pull/87))
* Piwik's list changes are merged back regularly in this reposiory


## Usage

The list is stored in this repository in `spammers.txt`. This text file contains one host per line.

You can [download this file manually](https://raw.githubusercontent.com/desbma/referer-spam-domains-blacklist/master/spammers.txt), download the [whole folder as zip](https://github.com/desbma/referer-spam-domains-blacklist/archive/master.zip) or clone the repository using git:

```
git clone https://github.com/desbma/referer-spam-domains-blacklist.git
```

Parsing the file should be pretty easy using your favorite language.


## Contributing

To add a new referer spam domain to this list, [click here to edit the spammers.txt file](https://github.com/desbma/referer-spam-domains-blacklist/edit/master/spammers.txt) and create a pull request. Alternatively you can create a [new issue](https://github.com/desbma/referer-spam-domains-blacklist/issues/new). In your issue or pull request please **explain where the referrer domain(s) appeared and why you think it is coming from a spammer**. If you think a hostname was added but is not actually a spammer, please follow the same process.

If you open a pull request, it is appreciated if you keep one hostname per line, keep the list ordered alphabetically, and use [Linux line endings](http://en.wikipedia.org/wiki/Newline).

### Subdomains

Sub-string matching on domain names can be done with this list, so adding `semalt.com` is enough to block all subdomain referers too, such as `semalt.semalt.com`.

However, there are cases where you'd only want to add a subdomain but not the root domain. For example, add `refererspammer.tumblr.com` but not `tumblr.com`, otherwise all `*.tumblr.com` sites would be affected.

### Sorting

To keep the list sorted the same way across forks it is recommended to let the computer do the sorting. The list follows the merge sort algorithm as implemented in [sort](https://en.wikipedia.org/wiki/Sort_(Unix)). You can use sort to both sort the list and filter out doubles:

```
sort -uf -o spammers.txt spammers.txt
```


## License

[WTFPLv2](http://www.wtfpl.net/txt/copying/)
