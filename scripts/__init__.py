# coding: utf8


def log(what, nl=True):
    from sys import stdout
    write = stdout.write
    if len(what) > 100:
        what = '%s…' % what[:99]
    what = '{:100}'.format(what)
    if not nl:
        write('\r')
    elif not log.lastnl:
        write('\n')
    stdout.write(what)
    if nl:
        write('\n')
    stdout.flush()
    log.lastnl = nl
log.lastnl = True
