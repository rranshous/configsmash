#!/usr/bin/python
from ConfigParser import ConfigParser
class ConfigSmasher():
    def __init__(self,to_smash=None):
        self.to_smash = to_smash # files / dir paths to look for ini's
        self.config = ConfigParser()

    def smash(self):
        # we are going to go through the to_smash
        # list, read in anything that is a file,
        # and read in all ini's if it is a dir
        for path in self.to_smash:
            files = self._expand(path)
            self._update_config(files)

        # now that we have an updated config, we want
        # to return it as a dictionary
        return self._config_to_dict(self.config)

    def _config_to_dict(self,config):
        # { section: { key: value } }
        to_return = {}
        to_return.update(config.defaults())
        for section in config.sections():
            to_return.setdefault(section,{}).update(dict(config.items(section)))
        return to_return

    def _expand(self,path):
        to_return = []
        from os.path import isfile,isdir,abspath
        path = abspath(path)
        if isdir(path):
            from glob import glob
            to_return += map(abspath,glob('%s/*.ini' % path))
        elif isfile(path):
            to_return.append(path)
        return to_return

    def _update_config(self,paths):
        # paths can be a list or a single string

        # we are going to update our
        # config with this new config
        read = self.config.read(paths)

if __name__ == '__main__':
    # parse our args
    from optparse import OptionParser
    option_parser = OptionParser()
    option_parser.usage = "%prog [options] path path2 path3 ..."
    option_parser.description = "Will cascade together multiple (python config) ini files. Paths can be directories or files."
    option_parser.add_option('-j', '--json', dest='output_json', default=False,
                             help="output in json format", action="store_true")
    options, args = option_parser.parse_args()

    # now that we know what we're doing lets do it
    smasher = ConfigSmasher(args)
    r_dict = smasher.smash()
    # now the smasher object has the config on it, we want
    # to write it to stdout
    # do they want json?
    if options.output_json:
        import json
        print json.dumps(r_dict)
    else:
        from cStringIO import StringIO
        buffer = StringIO()
        smasher.config.write(buffer)
        print buffer.getvalue()
