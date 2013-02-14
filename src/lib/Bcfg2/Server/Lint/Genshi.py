""" Check Genshi templates for syntax errors """

import sys
import Bcfg2.Server.Lint
from genshi.template import TemplateLoader, NewTextTemplate, MarkupTemplate, \
    TemplateSyntaxError
from Bcfg2.Server.Plugins.Bundler import BundleTemplateFile
from Bcfg2.Server.Plugins.Cfg.CfgGenshiGenerator import CfgGenshiGenerator


class Genshi(Bcfg2.Server.Lint.ServerPlugin):
    """ Check Genshi templates for syntax errors """

    def Run(self):
        """ run plugin """
        if 'Cfg' in self.core.plugins:
            self.check_cfg()
        if 'TGenshi' in self.core.plugins:
            self.check_tgenshi()
        if 'Bundler' in self.core.plugins:
            self.check_bundler()

    @classmethod
    def Errors(cls):
        return {"genshi-syntax-error": "error"}

    def check_cfg(self):
        """ Check genshi templates in Cfg for syntax errors """
        for entryset in self.core.plugins['Cfg'].entries.values():
            for entry in entryset.entries.values():
                if "hosts" in entry.name:
                    print "checking %s" % entry.name
                    print "  handles: %s" % self.HandlesFile(entry.name)
                    print "  is genshi: %s" % isinstance(entry, CfgGenshiGenerator)
                    if isinstance(entry, CfgGenshiGenerator):
                        print "  has template: %s" % bool(entry.template)
                if (self.HandlesFile(entry.name) and
                    isinstance(entry, CfgGenshiGenerator) and
                    not entry.template):
                    try:
                        entry.loader.load(entry.name,
                                          cls=NewTextTemplate)
                        if "hosts" in entry.name:
                            print "  loaded successfully"
                    except TemplateSyntaxError:
                        if "hosts" in entry.name:
                            print "  failed loading"
                        err = sys.exc_info()[1]
                        self.LintError("genshi-syntax-error",
                                       "Genshi syntax error: %s" % err)

    def check_tgenshi(self):
        """ Check templates in TGenshi for syntax errors """
        loader = TemplateLoader()

        for eset in self.core.plugins['TGenshi'].entries.values():
            for fname, sdata in list(eset.entries.items()):
                if self.HandlesFile(fname):
                    try:
                        loader.load(sdata.name, cls=NewTextTemplate)
                    except TemplateSyntaxError:
                        err = sys.exc_info()[1]
                        self.LintError("genshi-syntax-error",
                                       "Genshi syntax error: %s" % err)

    def check_bundler(self):
        """ Check templates in Bundler for syntax errors """
        loader = TemplateLoader()

        for entry in self.core.plugins['Bundler'].entries.values():
            if (self.HandlesFile(entry.name) and
                isinstance(entry, BundleTemplateFile)):
                try:
                    loader.load(entry.name, cls=MarkupTemplate)
                except TemplateSyntaxError:
                    err = sys.exc_info()[1]
                    self.LintError("genshi-syntax-error",
                                   "Genshi syntax error: %s" % err)
