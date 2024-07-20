from django.contrib.contenttypes.models import ContentType

from airadio.models import Library, StationPlaylist, Adverts, BrandingTOH


class Playlist(object):
    def __init__(self, station, location=None):
        self.station = station
        self.location = location
        self.iteration = 0
        self.rate_1_rotation = 0
        self.rate_2_rotation = 0
        self.rate_3_rotation = 0
        self.rate_4_rotation = 0
        self.rate_5_rotation = 0
        self.libraries = self.get_station_libraries()
        self.advert_count = 0
        self.branding_count = 0
        self.song_position = 0

    def generate_playlist(self):
        self.station.station_playlist.all().delete()
        schedule = self.get_scheduling()
        if schedule:
            playlist = self.generate_playlist_with_schedule(schedule)
        else:
            playlist = self.generate_playlist_without_schedule()
        return self.station.station_playlist.all()

    def get_library_playlist_count(self):
        largest = 0
        sequences = self.get_sequence()
        for sequence in sequences:
            libraries = self.get_library_items(sequence.rating)
            if libraries.count() > largest:
                largest = libraries.count()
        #        print largest
        return largest

    def generate_playlist_with_schedule(self, schedule):
        sequences = self.get_sequence()
        song_count = 0
        for i in range(self.get_library_playlist_count()):
            #            print i
            self.iteration = i
            for sequence in sequences:
                libraries = self.get_library_with_rating_and_schedule(
                    sequence.rating, schedule
                )

                if libraries:
                    if schedule.seperate_genres:
                        exist = self.check_for_same_generes(
                            schedule, libraries[0].library
                        )
                        if not exist:
                            self.create_playlist_item(libraries[0].library)
                            song_count = song_count + 1
                    else:
                        self.create_playlist_item(libraries[0].library)
                        song_count = song_count + 1

                    if schedule.advert > 0:
                        self.add_advert_to_playlist(song_count, schedule)

                    if schedule.branding > 0:
                        self.add_branding_to_playlist(song_count, schedule)

        return True

    def check_for_same_generes(self, schedule, song):
        LIB_TYPE = ContentType.objects.get_for_model(Library)
        libs = StationPlaylist.objects.filter(content_type=LIB_TYPE).order_by("id")
        exist = False
        if (
            schedule.seperate_genres_songs > 0
            and libs.count() >= schedule.seperate_genres_songs
        ):
            items = libs.reverse()[: schedule.seperate_genres_songs]
            for item in items:
                lib = LIB_TYPE.get_object_for_this_type(pk=item.object_id)
                if lib.genre == song.genre:
                    exist = True
        return exist

    def add_advert_to_playlist(self, song_count, schedule):
        all_adverts = self.get_adverts()
        if song_count % schedule.advert == 0:
            #            value = song_count / schedule.advert
            try:
                adverts = all_adverts[self.advert_count :]
                if adverts:
                    self.create_playlist_item(adverts[0])
                    self.advert_count = self.advert_count + 1
                else:
                    if all_adverts:
                        self.advert_count = 0
                        adverts = all_adverts[self.advert_count :]
                        self.create_playlist_item(adverts[0])
                        self.advert_count = self.advert_count + 1
            except Exception as e:
                pass

    def add_branding_to_playlist(self, song_count, schedule):
        all_brandings = self.get_brandings()
        if song_count % schedule.branding == 0:
            try:
                brandings = all_brandings[self.branding_count :]
                if brandings:
                    self.create_playlist_item(brandings[0])
                    self.branding_count = self.branding_count + 1
                else:
                    if all_brandings:
                        self.branding_count = 0
                        brandings = all_brandings[self.branding_count :]
                        self.create_playlist_item(brandings[0])
                        self.branding_count = self.branding_count + 1
            except Exception as e:
                pass

    def get_adverts(self):
        all_adverts = Adverts.objects.filter(location=None).order_by("id")
        results = [advert for advert in all_adverts]
        if self.location:
            loc_adverts = Adverts.objects.filter(location=self.location).order_by("id")
            results = results + [advert for advert in loc_adverts]
        return results

    def get_brandings(self):
        all_brandings = BrandingTOH.objects.filter(
            station=self.station, location=None
        ).order_by("id")
        results = [brand for brand in all_brandings]
        if self.location:
            local_brandings = BrandingTOH.objects.filter(
                station=self.station, location=self.location
            ).order_by("id")
            results = results + [brand for brand in local_brandings]
        return results

    def generate_playlist_without_schedule(self):
        sequences = self.get_sequence()
        for i in range(self.get_library_playlist_count()):
            self.iteration = i
            for sequence in sequences:
                libraries = self.get_library_with_rating_and_rotate(sequence.rating)
                if libraries:
                    self.create_playlist_item(libraries[0].library)
        return True

    def get_library_items(self, rating):
        libraries = []
        if rating == 1:
            libraries = self.libraries.filter(points__gte=1, points__lte=25)
        if rating == 2:
            libraries = self.libraries.filter(points__gte=26, points__lte=50)
        if rating == 3:
            libraries = self.libraries.filter(points__gte=51, points__lte=75)
        if rating == 4:
            libraries = self.libraries.filter(points__gte=76, points__lte=100)
        #            print libraries,'4'
        if rating == 5:
            libraries = self.libraries.filter(points__gte=101)
        return libraries

    def get_library_with_rating_and_rotate(self, rating):
        libraries = []
        all_songs_with_rating = self.get_library_items(rating)
        count = all_songs_with_rating.count()
        if rating == 1:
            rate_1_songs = all_songs_with_rating
            if self.rate_1_rotation < count:
                libraries = rate_1_songs[self.rate_1_rotation :]
            else:
                self.rate_1_rotation = 0
                libraries = rate_1_songs[self.rate_1_rotation :]
            self.rate_1_rotation = self.rate_1_rotation + 1

        if rating == 2:
            rate_2_songs = all_songs_with_rating
            if self.rate_2_rotation < count:
                libraries = rate_2_songs[self.rate_2_rotation :]
            else:
                self.rate_2_rotation = 0
                libraries = rate_2_songs[self.rate_2_rotation :]
            self.rate_2_rotation = self.rate_2_rotation + 1

        if rating == 3:
            rate_3_songs = all_songs_with_rating
            if self.rate_3_rotation < count:
                libraries = rate_3_songs[self.rate_3_rotation :]
            else:
                self.rate_3_rotation = 0
                libraries = rate_3_songs[self.rate_3_rotation :]
            self.rate_3_rotation = self.rate_3_rotation + 1

        if rating == 4:
            rate_4_songs = all_songs_with_rating
            if self.rate_4_rotation < count:
                libraries = rate_4_songs[self.rate_4_rotation :]
            else:
                self.rate_4_rotation = 0
                libraries = rate_4_songs[self.rate_4_rotation :]
            self.rate_4_rotation = self.rate_4_rotation + 1

        if rating == 5:
            rate_5_songs = all_songs_with_rating
            if self.rate_5_rotation < count:
                libraries = rate_5_songs[self.rate_5_rotation :]
            else:
                self.rate_5_rotation = 0
                libraries = rate_5_songs[self.rate_5_rotation :]
            self.rate_5_rotation = self.rate_5_rotation + 1
        return libraries

    def get_library_with_rating_and_schedule(self, rating, schedule):
        libraries = self.get_library_with_rating_and_rotate(rating)
        if rating == 1:
            return libraries[: schedule.rate_1] if schedule.rate_1 > 0 else libraries
        elif rating == 2:
            return libraries[: schedule.rate_2] if schedule.rate_2 > 0 else libraries
        elif rating == 3:
            return libraries[: schedule.rate_3] if schedule.rate_3 > 0 else libraries
        elif rating == 4:
            return libraries[: schedule.rate_4] if schedule.rate_4 > 0 else libraries
        elif rating == 5:
            return libraries[: schedule.rate_5] if schedule.rate_5 > 0 else libraries
        else:
            return libraries

    def get_sequence(self):
        return self.station.station_sequences.all()

    def get_station_libraries(self):
        return self.station.station_library.all()

    def get_scheduling(self):
        try:
            return self.station.station_schedules
        except:
            return None

    def create_playlist_item(self, object):
        self.song_position = self.song_position + 1
        library = StationPlaylist.objects.create(
            station=self.station,
            content_object=object,
            location=self.location,
            position=self.song_position,
        )
        return library
