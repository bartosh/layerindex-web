#!/usr/bin/env python

# Update migration info in OE-Classic recipes in OE layer index database
#
# Copyright (C) 2013 Intel Corporation
# Author: Paul Eggleton <paul.eggleton@linux.intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import sys
import os.path

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

import optparse
import re
import utils
import logging

logger = utils.logger_create('LayerIndexClassicUpdate')


def main():

    parser = optparse.OptionParser(
        usage = """
    %prog [options]""")

    parser.add_option("-b", "--branch",
            help = "Specify branch to import into",
            action="store", dest="branch", default='oe-classic')
    parser.add_option("-l", "--layer",
            help = "Specify layer to import into",
            action="store", dest="layer", default='oe-classic')
    parser.add_option("-n", "--dry-run",
            help = "Don't write any data back to the database",
            action="store_true", dest="dryrun")
    parser.add_option("-d", "--debug",
            help = "Enable debug output",
            action="store_const", const=logging.DEBUG, dest="loglevel", default=logging.INFO)
    parser.add_option("-q", "--quiet",
            help = "Hide all output except error messages",
            action="store_const", const=logging.ERROR, dest="loglevel")

    options, args = parser.parse_args(sys.argv)

    utils.setup_django()
    from layerindex.models import LayerItem, LayerBranch, Recipe, ClassicRecipe
    from django.db import transaction

    logger.setLevel(options.loglevel)

    res = list(LayerItem.objects.filter(name=options.layer)[:1])
    if res:
        layer = res[0]
    else:
        logger.error('Specified layer %s does not exist in database' % options.layer)
        sys.exit(1)

    layerbranch = layer.get_layerbranch(options.branch)
    if not layerbranch:
        logger.error("Specified branch %s does not exist in database" % options.branch)
        sys.exit(1)

    transaction.enter_transaction_management()
    transaction.managed(True)
    try:
        def recipe_pn_query(pn):
            return Recipe.objects.filter(layerbranch__branch__name='master').filter(pn=pn).order_by('layerbranch__layer__index_preference')

        recipequery = ClassicRecipe.objects.filter(layerbranch=layerbranch).filter(cover_status__in=['U', 'N'])
        for recipe in recipequery:
            replquery = recipe_pn_query(recipe.pn)
            found = False
            for replrecipe in replquery:
                logger.debug('Matched %s in layer %s' % (recipe.pn, replrecipe.layerbranch.layer.name))
                recipe.cover_layerbranch = replrecipe.layerbranch
                recipe.cover_status = 'D'
                recipe.cover_verified = False
                recipe.save()
                found = True
                break
            if not found:
                if recipe.pn.endswith('-native') or recipe.pn.endswith('-nativesdk'):
                    searchpn, _, suffix = recipe.pn.rpartition('-')
                    replquery = recipe_pn_query(searchpn)
                    for replrecipe in replquery:
                        if suffix in replrecipe.bbclassextend.split():
                            logger.debug('Found BBCLASSEXTEND of %s to cover %s in layer %s' % (replrecipe.pn, recipe.pn, replrecipe.layerbranch.layer.name))
                            recipe.cover_layerbranch = replrecipe.layerbranch
                            recipe.cover_pn = replrecipe.pn
                            recipe.cover_status = 'P'
                            recipe.cover_verified = False
                            recipe.save()
                            found = True
                            break
                    if not found and recipe.pn.endswith('-nativesdk'):
                        searchpn, _, _ = recipe.pn.rpartition('-')
                        replquery = recipe_pn_query('nativesdk-%s' % searchpn)
                        for replrecipe in replquery:
                            logger.debug('Found replacement %s to cover %s in layer %s' % (replrecipe.pn, recipe.pn, replrecipe.layerbranch.layer.name))
                            recipe.cover_layerbranch = replrecipe.layerbranch
                            recipe.cover_pn = replrecipe.pn
                            recipe.cover_status = 'R'
                            recipe.cover_verified = False
                            recipe.save()
                            found = True
                            break


        if options.dryrun:
            transaction.rollback()
        else:
            transaction.commit()
    except:
        transaction.rollback()
        raise
    finally:
        transaction.leave_transaction_management()

    sys.exit(0)


if __name__ == "__main__":
    main()
