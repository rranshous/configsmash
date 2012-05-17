#!/usr/bin/python
from functools import partial
from ConfigParser import ConfigParser
try:
    from paste.deploy.converters import asbool, asint, aslist
except ImportError, ex:
    print 'Warning: native config values not available. Please install paste deploy'
    def _r(*args,**kwargs): raise ValueError('Paste not available')
    asbool = asint = aslist = _r

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
        config_dict = self._config_to_dict(self.config)

        # update the values to be native types if we can
        self._set_native_types(config_dict)

        # and we're done
        return config_dict

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

    @classmethod
    def _set_native_types(cls, config_dict):
        """
        goes through the config setting the values to native types
        as it can. bool, int, list
        """

        assert isinstance(config_dict, dict), 'Must be mapping'
        converters = [
            (asint,lambda v: v.isdigit()),
            (asbool,lambda v: v.lower() in ('t','f','true','false')),
            (partial(aslist,sep=';',strip=True), lambda v: ';' in v)
        ]
        for k, v in config_dict.items():
            new_value = None
            for converter, condition in converters:
                if new_value is not None:
                    continue
                try:
                    if isinstance(v, dict):
                        new_value = cls._set_native_types(v)
                    elif condition and condition(v):
                        new_value = converter(v)
                    elif not condition:
                        new_value = converter(v)
                    if new_value != None:
                        config_dict[k] = new_value
                except ValueError, ex:
                    # not right
                    pass
        return config_dict


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
