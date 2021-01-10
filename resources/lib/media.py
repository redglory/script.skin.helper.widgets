#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    script.skin.helper.widgets
    media.py
    all media (mixed) widgets provided by the script
'''

from operator import itemgetter
import random
from metadatautils import kodi_constants
from resources.lib.utils import create_main_entry
from resources.lib.movies import Movies
from resources.lib.tvshows import Tvshows
from resources.lib.songs import Songs
from resources.lib.pvr import Pvr
from resources.lib.albums import Albums
from resources.lib.episodes import Episodes

class Media(object):
    '''all media (mixed) widgets provided by the script'''

    def __init__(self, addon, metadatautils, options):
        '''Initializations pass our common classes and the widget options as arguments'''
        self.metadatautils = metadatautils
        self.addon = addon
        self.options = options
        self.movies = Movies(self.addon, self.metadatautils, self.options)
        self.tvshows = Tvshows(self.addon, self.metadatautils, self.options)
        self.songs = Songs(self.addon, self.metadatautils, self.options)
        self.albums = Albums(self.addon, self.metadatautils, self.options)
        self.pvr = Pvr(self.addon, self.metadatautils, self.options)
        self.episodes = Episodes(self.addon, self.metadatautils, self.options)

    def listing(self):
        """main listing with all our media nodes"""
        tag = self.options.get("tag", "")
        extended_info_setting = self.options["extended_info"]
        if tag:
            label_prefix = u"%s - " % tag
        else:
            label_prefix = u""
        icon = "DefaultMovies.png"

        all_items = [
            (self.addon.getLocalizedString(32011), "inprogress&mediatype=media", icon),
            (self.addon.getLocalizedString(32070), "inprogressshowsandmovies&mediatype=media", icon),
            (self.addon.getLocalizedString(32071), "inprogressnextshowsandmovies&mediatype=media", icon),
            (self.addon.getLocalizedString(32005), "recent&mediatype=media", icon),
            (self.addon.getLocalizedString(32004), "recommended&mediatype=media", icon),
            (self.addon.getLocalizedString(32007), "inprogressandrecommended&mediatype=media", icon),
            (self.addon.getLocalizedString(32060), "inprogressandrandom&mediatype=media", icon),
            (self.addon.getLocalizedString(32022), "similar&mediatype=media", icon),
            (self.addon.getLocalizedString(32059), "random&mediatype=media", icon),
            (self.addon.getLocalizedString(32058), "top250&mediatype=media", icon),
            (self.addon.getLocalizedString(32001), "favourites&mediatype=media", icon),
            (self.addon.getLocalizedString(32075), "playlistslisting&mediatype=media",
             icon),
            (self.addon.getLocalizedString(32077), "playlistslisting&mediatype=media&tag=ref",
             icon)
        ]


        all_items = [
            (label_prefix + self.addon.getLocalizedString(32080), "inprogressepisodesandmovies&mediatype=media&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32088), "unwatchedshowsandmovies&mediatype=media&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32086), "watchagainshowsandmovies&mediatype=media&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32087), "newrelease&mediatype=media&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32081), "randomtop250&mediatype=media&tag=%s" % tag, icon),
            (label_prefix + self.addon.getLocalizedString(32004), "toprated&mediatype=media&tag=%s" % tag, icon)
        ]

        if extended_info_setting:
            all_items += [
                (self.addon.getLocalizedString(32100) +' - '+ self.addon.getLocalizedString(32090), "extendedpopulartmdb&mediatype=media", icon),
                (self.addon.getLocalizedString(32101) +' - '+ self.addon.getLocalizedString(32090), "extendedpopulartrakt&mediatype=media", icon),
                (self.addon.getLocalizedString(32101) +' - '+ self.addon.getLocalizedString(32102), "extendedtrending&mediatype=media", icon),
                (self.addon.getLocalizedString(32101) +' - '+ self.addon.getLocalizedString(32105), "extendedmostplayed&mediatype=media", icon),
                (self.addon.getLocalizedString(32101) +' - '+ self.addon.getLocalizedString(32108), "extendedmostwatched&mediatype=media", icon)
            ]

        return self.metadatautils.process_method_on_list(create_main_entry, all_items)

    def playlistslisting(self):
        '''get tv playlists listing'''
        #TODO: append (Movie playlist) and (TV Show Playlist)
        #TODO: only show playlists with appropriate type (Movie or TV Show)
        movie_label = self.options.get("movie_label")
        tag_label = self.options.get("tag")
        all_items = []
        for item in self.metadatautils.kodidb.files("special://videoplaylists/"):
            # replace '&' with [and] -- will get fixed when processed in playlist action
            label = item["label"].replace('&', '[and]')
            if tag_label == 'ref':
                if movie_label:
                    details = (item["label"], "refplaylist&mediatype=media&movie_label=%s&tv_label=%s" %
                               (movie_label, label), "DefaultTvShows.png")
                else:
                    details = (item["label"], "playlistslisting&mediatype=media&tag=ref&movie_label=%s" % label,
                               "DefaultMovies.png")
            else:
                if movie_label:
                    details = (item["label"], "playlist&mediatype=media&movie_label=%s&tv_label=%s" %
                               (movie_label, label), "DefaultTvShows.png")
                else:
                    details = (item["label"], "playlistslisting&mediatype=media&movie_label=%s" % label,
                               "DefaultMovies.png")
            all_items.append(create_main_entry(details))
        return all_items

    def playlist(self):
        '''get items in both playlists, sorted by recommended score'''
        movie_label = self.options.get("movie_label").replace('[and]', '&')
        tv_label = self.options.get("tv_label").replace('[and]', '&')
        movies = self.metadatautils.kodidb.movies(
            filters=[{"operator": "is", "field": "playlist", "value": movie_label}])
        tvshows = self.metadatautils.kodidb.tvshows(
            filters=[{"operator": "is", "field": "playlist", "value": tv_label}])
        tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
        all_items = self.sort_by_recommended(movies+tvshows)
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def refplaylist(self):
        '''get items similar to items in playlists '''
        movie_label = self.options.get("movie_label").replace('[and]', '&')
        tv_label = self.options.get("tv_label").replace('[and]', '&')
        ref_movies = self.metadatautils.kodidb.movies(
            filters=[{"operator": "is", "field": "playlist", "value": movie_label}])
        ref_tvshows = self.metadatautils.kodidb.tvshows(
            filters=[{"operator": "is", "field": "playlist", "value": tv_label}])
        movies = self.metadatautils.kodidb.movies(
            filters=[{"operator": "isnot", "field": "playlist", "value": movie_label}])
        tvshows = self.metadatautils.kodidb.tvshows(
            filters=[{"operator": "isnot", "field": "playlist", "value": tv_label}])
        tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
        all_items = self.sort_by_recommended(movies+tvshows, ref_movies+ref_tvshows)
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def recommended(self):
        ''' get recommended media '''
        if self.options["exp_recommended"]:
            # get all unwatched, not in-progess movies & tvshows
            movies = self.metadatautils.kodidb.movies(filters=[kodi_constants.FILTER_UNWATCHED])
            tvshows = self.metadatautils.kodidb.tvshows(filters=[kodi_constants.FILTER_UNWATCHED])
            tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow, tvshows)
            # return list sorted by recommended score, and capped by limit
            return self.sort_by_recommended(movies+tvshows)
        all_items = self.movies.recommended()
        all_items += self.tvshows.recommended()
        all_items += self.albums.recommended()
        all_items += self.songs.recommended()
        all_items += self.episodes.recommended()
        return sorted(all_items, key=lambda k: random.random())[:self.options["limit"]]

    def recent(self):
        ''' get recently added media '''
        all_items = self.movies.recent()
        all_items += self.albums.recent()
        all_items += self.songs.recent()
        all_items += self.episodes.recent()
        all_items += self.pvr.recordings()
        return sorted(all_items, key=itemgetter("dateadded"), reverse=True)[:self.options["limit"]]

    def recentshowsandmovies(self):
        """ get recently added movies and tvshows """
        all_items = self.movies.recent()
        all_items += self.tvshows.recent()
        return sorted(all_items, key=itemgetter("dateadded"), reverse=True)[:self.options["limit"]]

    def random(self):
        ''' get random media '''
        all_items = self.movies.random()
        all_items += self.tvshows.random()
        all_items += self.albums.random()
        all_items += self.songs.random()
        all_items += self.episodes.random()
        all_items += self.pvr.recordings()
        return sorted(all_items, key=lambda k: random.random())[:self.options["limit"]]

    def inprogress(self):
        ''' get in progress media '''
        all_items = self.movies.inprogress()
        all_items += self.episodes.inprogress()
        all_items += self.pvr.recordings()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]

    def inprogressshowsandmovies(self):
        ''' get in progress media '''
        all_items = self.movies.inprogress()
        all_items += self.episodes.inprogress()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]

    def inprogressepisodesandmovies(self):
        """ get in progress episodes and movies """
        all_items = self.movies.inprogress()
        all_items += self.episodes.inprogress()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]

    def inprogressnextshowsandmovies(self):
        """ get in-progress/next episodes AS TV Shows and in-progress movies """
        all_items = self.movies.inprogress()
        all_items += self.tvshows.nextshows()
        return sorted(all_items, key=itemgetter("lastplayed"), reverse=True)[:self.options["limit"]]

    def inprogressandrecommended(self):
        """ get recommended and in progress media """
        all_items = self.inprogress()
        all_titles = [item["title"] for item in all_items]
        for item in self.recommended():
            if item["title"] not in all_titles:
                all_items.append(item)
        return all_items[:self.options["limit"]]

    def inprogressandrandom(self):
        """ get in progress AND random movies """
        all_items = self.inprogress()
        all_ids = [item["movieid"] for item in all_items]
        for item in self.random():
            if item["movieid"] not in all_ids:
                all_items.append(item)
        return all_items[:self.options["limit"]]

    def watchagainshowsandmovies(self):
        """ get random recently watched movies and tv shows """
        filters = [kodi_constants.FILTER_WATCHED]
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        all_items = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                     filters=filters,
                                                     limits=(0, self.options["limit"]))
        all_items += self.metadatautils.process_method_on_list(
            self.tvshows.process_tvshow,
            self.metadatautils.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED,
                                              filters=filters + [kodi_constants.FILTER_INPROGRESS],
                                              filtertype="or",
                                              limits=(0, self.options["limit"])))
        return sorted(all_items, key=lambda k: random())[:self.options["limit"]]

    def extendedpopulartmdb(self):
        """gets popular movies and tvshows from tmdb"""
        all_items = []
        all_items += self.movies.extendedpopulartmdb()
        all_items += self.tvshows.extendedpopulartmdb()
        return sorted(all_items, key=itemgetter("extendedindex"))[:self.options["limit"]]

    def extendedpopulartrakt(self):
        """gets popular movies and tvshows from trakt"""
        all_items = []
        all_items += self.movies.extendedpopulartrakt()
        all_items += self.tvshows.extendedpopulartrakt()
        return sorted(all_items, key=itemgetter("extendedindex"))[:self.options["limit"]]

    def extendedtrending(self):
        """gets popular movies and tvshows from trakt"""
        all_items = []
        all_items += self.movies.extendedtrending()
        all_items += self.tvshows.extendedtrending()
        return sorted(all_items, key=itemgetter("extendedindex"))[:self.options["limit"]]

    def extendedmostplayed(self):
        """gets most played movies and tvshows from trakt"""
        all_items = []
        all_items += self.movies.extendedmostplayed()
        all_items += self.tvshows.extendedmostplayed()
        return sorted(all_items, key=itemgetter("extendedindex"))[:self.options["limit"]]

    def extendedmostwatched(self):
        """gets most watched movies and tvshows from trakt"""
        all_items = []
        all_items += self.movies.extendedmostwatched()
        all_items += self.tvshows.extendedmostwatched()
        return sorted(all_items, key=itemgetter("extendedindex"))[:self.options["limit"]]

    def browsegenres(self):
        """special entry which can be used to create custom genre listings
            returns each genre with poster/fanart artwork properties from 5
            random movies/tvshows in the genre."""
        # find matches
        movie_genres = self.metadatautils.kodidb.genres("movie")
        tvshow_genres = self.metadatautils.kodidb.genres("tvshow")
        media_genres = []
        for movie_genre in movie_genres:
            for tvshow_genre in tvshow_genres:
                if movie_genre["label"] == tvshow_genre["label"]:
                    media_genres.append(movie_genre["label"])
                    break
        # build genres
        all_items = []
        for genre in media_genres:
            all_items.append(self.process_genre(genre))
        return all_items

    def process_genre(self, genre):
        """method to create genre listitem from genre's label"""
        genre_json = {"art": {}, "label": genre, "title": genre,
                      "file": u"plugin://script.skin.helper.widgets/?action=forgenre&mediatype=media&genre=%s" % genre,
                      "isFolder": True, "IsPlayable": "false", "thumbnail": "DefaultGenre.png", "type": "genre"}
        # randomly select fanart/poster from tvshows OR movies
        flip_coin = randint(0, 1)
        if flip_coin:
            genre_items = self.movies.get_genre_movies(genre, False, 5, kodi_constants.SORT_RANDOM)
        else:
            genre_items = self.tvshows.get_genre_tvshows(genre, False, 5, kodi_constants.SORT_RANDOM)
        if genre_items:
            for count, item in enumerate(genre_items):
                genre_json["art"]["poster.%s" % count] = item["art"].get("poster", "")
                genre_json["art"]["fanart.%s" % count] = item["art"].get("fanart", "")
                if "fanart" not in genre_json["art"]:
                    # set genre's primary fanart image to first movie fanart
                    genre_json["art"]["fanart"] = item["art"].get("fanart", "")
        return genre_json

    def similar(self):
        ''' get similar movies and similar tvshows for given imdbid'''
        if self.options["exp_recommended"]:
            # get ref item, and check if movie
            ref_item = self.get_recently_watched_item()
            is_ref_movie = ref_item.has_key("uniqueid")
            # create list of all items
            if self.options["hide_watched_similar"]:
                all_items = self.metadatautils.kodidb.movies(filters=[kodi_constants.FILTER_UNWATCHED])
                all_items += self.metadatautils.process_method_on_list(
                    self.tvshows.process_tvshow, self.metadatautils.kodidb.tvshows(
                        filters=[kodi_constants.FILTER_UNWATCHED]))
            else:
                all_items = self.metadatautils.kodidb.movies()
                all_items += self.metadatautils.process_method_on_list(
                    self.tvshows.process_tvshow, self.metadatautils.kodidb.tvshows())
            if not ref_item:
                return None
            if is_ref_movie:
                # define sets for speed
                set_genres = set(ref_item["genre"])
                set_directors = set(ref_item["director"])
                set_writers = set(ref_item["writer"])
                set_cast = set([x["name"] for x in ref_item["cast"][:5]])
                sets = (set_genres, set_directors, set_writers, set_cast)
                # get similarity score for all items
                for item in all_items:
                    if item.has_key("uniqueid"):
                        # if item is also movie, check if it's the ref_item
                        if item["title"] == ref_item["title"] and item["year"] == ref_item["year"]:
                            # don't rank the reference movie
                            similarscore = 0
                        else:
                            # otherwise, use movie method for score
                            similarscore = self.movies.get_similarity_score(
                                ref_item, item, sets=sets)
                    else:
                        # if item isn't movie, use mixed method
                        similarscore = self.get_similarity_score(ref_item, item)
                    # set extraproperties
                    item["similarscore"] = similarscore
                    item["extraproperties"] = {"similartitle": ref_item["title"], "originalpath": item["file"]}
            else:
                # define sets for speed
                set_genres = set(ref_item["genre"])
                set_cast = set([x["name"] for x in ref_item["cast"][:10]])
                sets = (set_genres, set_cast)
                # get similarity score for all items
                for item in all_items:
                    if not item.has_key("uniqueid"):
                        # if item is also tvshow, check if it's the ref_item
                        if item["title"] == ref_item["title"] and item["year"] == ref_item["year"]:
                            # don't rank the reference movie
                            similarscore = 0
                        else:
                            # otherwise, use tvshow method for score
                            similarscore = self.tvshows.get_similarity_score(
                                ref_item, item, sets=sets)
                    else:
                        # if item isn't tvshow, use mixed method
                        similarscore = self.get_similarity_score(ref_item, item)
                    # set extraproperties
                    item["similarscore"] = similarscore
                    item["extraproperties"] = {"similartitle": ref_item["title"], "originalpath": item["file"]}
            # return list sorted by score and capped by limit
            return sorted(all_items, key=itemgetter("similarscore"), reverse=True)[:self.options["limit"]]
        all_items = self.movies.similar()
        all_items += self.tvshows.similar()
        all_items += self.albums.similar()
        all_items += self.songs.similar()
        return sorted(all_items, key=lambda k: random.random())[:self.options["limit"]]

    def top250(self):
        ''' get imdb top250 movies in library '''
        all_items = self.movies.top250()
        all_items += self.tvshows.top250()
        return sorted(all_items, key=itemgetter("top250_rank"))[:self.options["limit"]]

    def favourites(self):
        '''get favourite media'''
        from favourites import Favourites
        self.options["mediafilter"] = "media"
        return Favourites(self.addon, self.metadatautils, self.options).favourites()

    def favourite(self):
        '''synonym to favourites'''
        return self.favourites()

    def get_items_for_recommended(self):
        """get all items for recommended and top picks methods"""
        filters = [kodi_constants.FILTER_UNWATCHED]
        # get all unwatched, not in-progess movies & tvshows
        if self.options.get("tag"):
            filters.append({"operator": "contains", "field": "tag", "value": self.options["tag"]})
        movies = self.metadatautils.kodidb.movies(filters=filters)
        filters.append({"operator": "false", "field": "inprogress",
                        "value": ""})
        tvshows = self.metadatautils.process_method_on_list(self.tvshows.process_tvshow,
                                                            self.metadatautils.kodidb.tvshows(filters=filters))
        return movies + tvshows

    def get_recently_watched_item(self):
        ''' get a random recently watched movie or tvshow '''
        num_recent_similar = self.options["num_recent_similar"]
        # get recently played movies
        recent_items = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                        filters=[kodi_constants.FILTER_WATCHED],
                                                        limits=(0, num_recent_similar))
        # get recently played episodes
        recent_items += self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED,
                                                           filters=[kodi_constants.FILTER_WATCHED],
                                                           limits=(0, num_recent_similar))
        # sort all by last played, then randomly pick
        recent_items = sorted(recent_items, key=itemgetter("lastplayed"), reverse=True)[:num_recent_similar]
        item = random.choice(recent_items)
        # if item is an episode, get its tvshow
        if not item.has_key("genre"):
            show_title = item['showtitle']
            title_filter = [{"field": "title", "operator": "is", "value": "%s" % show_title}]
            tvshow = self.metadatautils.kodidb.tvshows(filters=title_filter, limits=(0, 1))
            return tvshow[0]
        return item

    def sort_by_recommended(self, all_items, ref_items=None):
        ''' sort list of mixed movies/tvshows by recommended score'''
        # use recent items if ref_items not given
        if not ref_items:
            num_recent_similar = self.options["num_recent_similar"]
            # get recently watched movies
            movies = self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                      filters=[kodi_constants.FILTER_WATCHED],
                                                      limits=(0, 2*num_recent_similar))
            # get recently watched episodes
            episodes = self.metadatautils.kodidb.episodes(sort=kodi_constants.SORT_LASTPLAYED,
                                                          filters=[kodi_constants.FILTER_WATCHED],
                                                          limits=(0, 2*num_recent_similar))
            # get tvshows from episodes
            tvshows = self.tvshows.get_tvshows_from_episodes(episodes)
            # combine lists and sort by last played recent
            items = sorted(movies + tvshows, key=itemgetter('lastplayed'), reverse=True)
            # find duplicates and set weights
            titles = set()
            ref_items = list()
            weights = dict()
            weight_sum = 0
            for item in items:
                title = item['title']
                if title in titles:
                    weights[title] += 0.5
                    weight_sum += 0.5
                else:
                    ref_items.append(item)
                    titles.add(title)
                    weights[title] = 1
                    weight_sum += 1
                if weight_sum >= num_recent_similar:
                    break
            del titles, items, weight_sum
        else:
            # set equal weights for pre-defined ref_items
            weights = dict()
            for item in ref_items:
                weights[item['title']] = 1
        # average scores together for every item
        for item in all_items:
            similarscore = 0
            for ref_item in ref_items:
                title = ref_item['title']
                # add all similarscores for item
                if ref_item.has_key("uniqueid") and item.has_key("uniqueid"):
                    # use movies method if both items are movies
                    similarscore += weights[title] * self.movies.get_similarity_score(ref_item, item)
                elif ref_item.has_key("uniqueid") or item.has_key("uniqueid"):
                    # use media method if only one item is a movie
                    similarscore += weights[title] * self.get_similarity_score(ref_item, item)
                else:
                    # use tvshows method if neither items are movies
                    similarscore += weights[title] * self.tvshows.get_similarity_score(ref_item, item)
            # average score and scale down based on playcount
            item["recommendedscore"] = similarscore / (1+item["playcount"]) / len(ref_items)
        # return sorted list capped by limit
        return sorted(all_items, key=itemgetter("recommendedscore"), reverse=True)[:self.options["limit"]]

    def get_references_last_played(self):
        """ sort list of mixed movies/tvshows by recommended score"""
        # get recently watched items
        num_recent_similar = self.options["num_recent_similar"]
        all_refs = []
        all_refs += self.metadatautils.kodidb.tvshows(sort=kodi_constants.SORT_LASTPLAYED,
                                                      filters=[kodi_constants.FILTER_WATCHED],
                                                      limits=(0, num_recent_similar))
        all_refs += self.metadatautils.kodidb.movies(sort=kodi_constants.SORT_LASTPLAYED,
                                                     filters=[kodi_constants.FILTER_WATCHED],
                                                     limits=(0, num_recent_similar))
        return all_refs

    def playlist_recommended(self, all_items):
        return self.sort_by_recommended(all_items)

    def playlist_random(self, all_items):
        return sorted(all_items, key=lambda k: random())[:self.options["limit"]]

    def playlist_recent(self, all_items):
        return sorted(all_items, key=itemgetter("dateadded"), reverse=True)[:self.options["limit"]]

    def playlist_year(self, all_items):
        return sorted(all_items, key=itemgetter("year"), reverse=True)[:self.options["limit"]]

    def playlist_title(self, all_items):
        return sorted(all_items, key=itemgetter("title"))[:self.options["limit"]]

    def get_similarity_score(self, ref_item, other_item):
        '''
            get a similarity score (0-.625) between movie and tvshow
        '''
        # get set of genres
        if ref_item.has_key("uniqueid"):
            set_genres = set(ref_item["genre"])
        else:
            # change genres to movie equivalents if tvshow
            set_genres = self.convert_tvshow_genres(ref_item["genre"])
        set_cast = set([x["name"] for x in ref_item["cast"][:5]])
        # calculate individual scores for contributing factors
        # genre_score = (numer of matching genres) / (number of unique genres between both)
        genre_score = 0 if not set_genres else \
            float(len(set_genres.intersection(other_item["genre"]))) / \
            len(set_genres.union(other_item["genre"]))
        # cast_score is normalized by fixed amount of 5, and scaled up nonlinearly
        cast_score = (float(len(set_cast.intersection([x["name"] for x in other_item["cast"][:5]])))/5)**(1./2)
        # rating_score is "closeness" in rating, scaled to 1
        if ref_item["rating"] and other_item["rating"] and abs(ref_item["rating"]-other_item["rating"]) < 3:
            rating_score = 1 - abs(ref_item["rating"]-other_item["rating"])/3
        else:
            rating_score = 0
        # year_score is "closeness" in release year, scaled to 1 (0 if not from same decade)
        if ref_item["year"] and other_item["year"] and abs(ref_item["year"]-other_item["year"]) < 10:
            year_score = 1 - abs(ref_item["year"]-other_item["year"])/10
        else:
            year_score = 0
        # calculate overall score using weighted average
        similarscore = .5*genre_score + .05*cast_score + .025*rating_score + .05*year_score
        return similarscore

    @staticmethod
    def convert_tvshow_genres(genres):
        ''' converts tvshow genres into movie genre equivalent '''
        mapped_genres = {'TV Documentaries': 'Documentary',
                         'TV Sci-Fi & Fantasy': 'Sci-Fi & Fantasy',
                         'TV Action & Adventure': 'Action & Adventure',
                         'TV Comedies': 'Comedy',
                         'TV Mysteries': 'Mystery',
                         'TV Westerns': 'Westerns',
                         'TV Dramas': 'Drama',
                         'TV Crime Dramas': 'Crime Dramas',
                        }
        for genre in genres:
            if mapped_genres.has_key(genre):
                genre = mapped_genres[genre]
        return set(genres)
