'''
Created on Aug 24, 2012

@author: Anthony Honstain

This is collection of higher level scripts for administrator or key section of code
to process or cleanup data in the database.

'''
from django.db import connection

from core.models import (
    LapTimes,
    SingleRaceResults,
    Racer,
    OfficialClassNames,
    AliasClassNames)

import logging
log = logging.getLogger('defaultlogger')

class _ProcessRacer():
    '''
    _ProcessRacer handles the work of identifying alias names and collapsing them
    to the alias with the most results.

    I have a number of different racer names, and many of them represent
    the same person but have slightly different spelling, structure, letter case.

    For the time being I need a quick and easy way to push these to a single name, so
    that people can get their data in a single place.
    '''
    def __init__(self, racer_data):
        '''
        The constructor does the bulk of the work for this object.

        racer_data: has a very specific format. Each element should have the form:
            [<racer key>, <racer preferredname string>, <number of raceresults for this name>]

            Example: [ [1, 'hovarter,kevin', 5], [2, 'gripentrog, kurt', 5], [3, 'Collins, Brandon', 2]
        '''

        # This will contain the primary names that all others will be aliases of.
        # This should be the name which is most frequently raced under.
        self._primaryName_dict = {}

        # I need to start identifying duplicates, these are several of the
        # most obvious reasons:
        #     Character Case - upper/lower
        #     FName - LName order
        #
        # I think I can save myself some grief if I assume names with more races should be the
        # original, so that when I run this in the future, I am less likely to have updates.
        # for result in results:
        #    print result

        for result in racer_data:
            # We need to calculate the formated name (no case, reverse ordering of fname/lname).
            tempname = result[1].lower()

            comma_index = tempname.find(',')
            if (comma_index > -1):
                # This probably contains a name of the format "<lname>, <fname>"
                fname = tempname[comma_index + 1:].strip()
                lname = tempname[0: comma_index].strip()
                tempname = fname + " " + lname

            # print result
            # print '\t' + tempname

            # Now with the name formated, we can see it belongs in the dictionary
            if (tempname not in self._primaryName_dict):

                # Before we add this as a new key, we are going to check if there
                # are any similarly spelled names.
                actual_spelling = self._check_edit_distance(tempname)

                # if _check_edit_distance found a key, that is the key will will
                # put this name under.
                if (actual_spelling != ""):
                    self._primaryName_dict[actual_spelling].append(result)
                else:
                    self._primaryName_dict[tempname] = [result]

            else:
                # This means it was an unkown name with no aliases found.
                self._primaryName_dict[tempname].append(result)

        # Filter the results so that we have just possible aliases
        self.likely_aliases = filter(lambda x: len(x[1]) > 1, self._primaryName_dict.items())

        # print "Prining all the likely_aliases"
        # for key in likely_aliases:
        #    print '\t', key

    def _check_edit_distance(self, tempname):
        for key in self._primaryName_dict.keys():
            if (len(key) == len(tempname) and self._misspell_count(key, tempname) == len(key) - 1):
                return key
        return ""

    def _misspell_count(self, origional_str, test_str):
        same_count = 0
        for i in range(min(len(origional_str), len(test_str))):
            if (origional_str[i] == test_str[i]):
                same_count += 1
        return same_count


def collapse_racer_names():
    '''
    collapsenames uses the _ProcessRacer object to identify aliases in the Racer's
    and collapse them to a single name.

    This modifies and cleans up several of the core tables.

    WARNING - this does not touch anything in ranking (if rankings are computed and the
        names are later aliased and collapsed, there is nothing that can be done but
        RECOMPUTE the ranking).
    '''

    # First step is to get all the racer names and their ids.
    # Info - We use the singleraceresults table to give us an
    # idea of how many racers their are for each name, more popular
    # names will be the root (that others are collapsed to).
    get_racers_cmd = '''
        SELECT racer.id, racer.racerpreferredname, COUNT(rresult.id)
        FROM core_racer as racer ,
            core_singleraceresults as rresult
        WHERE racer.id = rresult.racer_id
        GROUP BY racer.id
        ORDER BY COUNT(rresult.id) desc;
        '''
    cursor = connection.cursor()
    cursor.execute(get_racers_cmd)
    results = cursor.fetchall()
    # Example results
    # [ [1, 'hovarter,kevin', 5], [2, 'gripentrog, kurt', 5], [3, 'Collins, Brandon', 2]

    processRacerObj = _ProcessRacer(results)

    for canidate in processRacerObj.likely_aliases:

        primary_name = canidate[1][0]
        alias_list = canidate[1][1:]

        # Helpful information to look at when investigating problems
        # print
        # print "Primary:", primary_name
        # print "Lkely Alias:", alias_list
        # print 'COLLAPSING IN SQL'
        '''
            Example output:
                Primary: (3, u'Charlie, Jon', 2L)
                Lkely Alias: [(7, u'Charlee, Jon', 1L)]
                COLLAPSING IN SQL

                Primary: (1, u'Anthony Honstain', 2L)
                Lkely Alias: [(10, u'Honstain, Anthony', 1L)]
                COLLAPSING IN SQL

                Primary: (2, u'lowercase jim', 2L)
                Lkely Alias: [(6, u'LOWERCASE JIM', 1L)]
                COLLAPSING IN SQL
                Anthony Honstain
                lowercase jim
                Charlie, Jon
                Delta, Jon
                Echo, Jon
                Hotel, Jon
                Golf, Jon
        '''

        for alias in alias_list:

            alias_id = alias[0]
            new_racer_obj = Racer.objects.get(pk=primary_name[0])
            # ===================================
            # Update the race results
            # ===================================
            raceresult_set = SingleRaceResults.objects.filter(racer__exact=alias_id).update(racer=new_racer_obj)

            # ===================================
            # Update the lap times
            # ===================================
            laptimes_set = LapTimes.objects.filter(racer__exact=alias_id).update(racer=new_racer_obj)

            # ===================================
            # Remove the alias racer
            # ===================================
            racer_obj = Racer.objects.get(pk=alias_id)
            racer_obj.delete()

            log.debug('metric=CollapseRacerNames primary="%s" primary_id=%d '\
                'aliasToDelete="%s" alias_id=%d',
                primary_name[1], primary_name[0], alias[1], alias[0])


def collapse_alias_classnames(queryset):
    '''
    collapse_alias_classnames takes a queryset of SingleRaceDetails and will use
    the mapping between OfficialClassNames and AliasClassNames to clean up
    the classnames.

    This means setting the correct case on the class name if it is different from the official.
    This means changing an alias to the offical class name if they differ.

    History:
        Oct 25, 2012 - Anthony: I move the information about the main events
        to a separate column. No reason to have dead code in here.
    '''

    # First we need to construct an efficient structure for checking

    # Note - all the of the keys in lookup and offical_classnames are LOWERCASE
    lookup = {}
    official_classnames = {}  # This is where the official names (unmodified case) are stored.

    officalclass_queryset = OfficialClassNames.objects.all()
    for officialclass in officalclass_queryset:
        lookup[officialclass.raceclass.lower()] = None
        official_classnames[officialclass.raceclass.lower()] = officialclass.raceclass

    alliasclass_queryset = AliasClassNames.objects.all()
    for alliasclass in alliasclass_queryset:
        lookup[alliasclass.raceclass.lower()] = alliasclass.officialclass.raceclass

    #
    # Look at each of the race details from the query set, and update the
    # class name if needed.
    #
    for racedetail in queryset:
        raceclass = racedetail.racedata

        if raceclass.lower() in lookup:
            # print "HIT:", raceclass.lower(), racedetail.racedata
            #
            # We found a hit, this is either an official class, or we will change it.
            #
            if (lookup[raceclass.lower()] == None):
                # This is an official class, we just need to check if case is good.
                if (official_classnames[raceclass.lower()] != raceclass):
                    # The class is named correctly, but we are going to fix the case.
                    log.debug('metric=CollapseClassNames original=%s new=%s', raceclass, official_classnames[raceclass.lower()])
                    racedetail.racedata = official_classnames[raceclass.lower()]
                    # print "CASE FIXED:", racedetail.racedata
                    racedetail.save()
            else:
                # We need to UPDATE the race to use the official class name.
                log.debug('metric=CollapseClassNames original=%s new=%s', raceclass, lookup[raceclass.lower()])
                racedetail.racedata = lookup[raceclass.lower()]
                # print "ALIAS FIXED:", racedetail.racedata
                racedetail.save()
