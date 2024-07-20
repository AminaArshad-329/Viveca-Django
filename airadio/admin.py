from django.contrib import admin

from .models import *


class DashboardTopSongsInlines(admin.TabularInline):
    model = DashboardTopSongs
    extra = 3


class StationBannerInlines(admin.TabularInline):
    model = StationBanner
    extra = 1


class StationTopicInlines(admin.TabularInline):
    model = TopicPrompts
    extra = 1


class StationPositionInlines(admin.TabularInline):
    model = PositionPrompts
    extra = 1


class MusicResearchDataInlines(admin.TabularInline):
    model = MusicResearchData
    extra = 1


class MusicResearchLibraryAdmin(admin.ModelAdmin):
    inlines = [
        MusicResearchDataInlines,
    ]


class RealTimeSkipDataInlines(admin.TabularInline):
    model = RealTimeSkipData
    extra = 1


class RealTimeSkipLibraryAdmin(admin.ModelAdmin):
    inlines = [
        RealTimeSkipDataInlines,
    ]


class DashboardAdmin(admin.ModelAdmin):
    inlines = [DashboardTopSongsInlines]


class StationPlaylistAdmin(admin.ModelAdmin):
    list_display = ("position", "station", "content_type", "object_id", "skipped")


class TSUAdminInlines(admin.TabularInline):
    model = TSUPerStation
    extra = 3


class AnalyticsAdmin(admin.ModelAdmin):
    inlines = [
        TSUAdminInlines,
    ]
    fieldsets = (
        (None, {"fields": ("date",)}),
        (
            "Top Contents",
            {"fields": ("unique_users", "current_users", "s3_data_usage", "db_load")},
        ),
        ("Age Profile", {"fields": ("male", "female")}),
        ("Platform Usage", {"fields": ("iphone", "android", "web_palyer")}),
    )


class LibraryAdmin(admin.ModelAdmin):
    search_fields = [
        "artistname",
        "title",
    ]


class AuthorizedRetailUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "domain",
        "ipaddress",
    ]
    list_editable = [
        "domain",
        "ipaddress",
    ]


class StationsAdmin(admin.ModelAdmin):
    list_display = ["station_name", "retail", "published"]
    list_editable = [
        "published",
    ]
    inlines = [StationBannerInlines, StationTopicInlines, StationPositionInlines]


class WidgetUserStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        "station",
        "user_count",
    ]


class ExportPlaylistItemInlines(admin.TabularInline):
    model = ExportPlaylistItem
    extra = 1


class ExportPlaylistAdmin(admin.ModelAdmin):
    inlines = [
        ExportPlaylistItemInlines,
    ]


class DJTracksAdmin(admin.ModelAdmin):
    list_display = ("title", "dj", "created")


admin.site.register(Stations, StationsAdmin)
admin.site.register(Locations)
admin.site.register(Library, LibraryAdmin)
admin.site.register(Wall)
admin.site.register(Links)
admin.site.register(Users)
admin.site.register(Playlist)
admin.site.register(Reports)
admin.site.register(ServerStats)
admin.site.register(Platforms)
admin.site.register(Research)
admin.site.register(Sequence)
admin.site.register(MediaUpload)
admin.site.register(Genres)
admin.site.register(PositionPrompts)
admin.site.register(TopicPrompts)
admin.site.register(Scheduling)
admin.site.register(BrandingTOH)
admin.site.register(Adverts)
admin.site.register(StationPlaylist, StationPlaylistAdmin)
admin.site.register(StationLibrary)
admin.site.register(GlobalPlaylist)
admin.site.register(DJUser)
admin.site.register(DJTracks, DJTracksAdmin)
admin.site.register(Analytics, AnalyticsAdmin)
admin.site.register(TSUPerStation)
admin.site.register(Dashboard)
admin.site.register(MusicResearchLibrary, MusicResearchLibraryAdmin)
admin.site.register(MusicResearchData)
admin.site.register(DashboardTopSongs)

admin.site.register(RealTimeSkipLibrary, RealTimeSkipLibraryAdmin)
admin.site.register(RealTimeSkipData)
admin.site.register(AuthorizedRetailUser, AuthorizedRetailUserAdmin)
admin.site.register(DJStationStatus)
admin.site.register(WidgetUserStatistics, WidgetUserStatisticsAdmin)
admin.site.register(ExportPlaylist, ExportPlaylistAdmin)
admin.site.register(ExportPlaylistItem)
admin.site.register(MarketStations)
admin.site.register(UserActivity)
admin.site.register(Installation)

# AI Radio
# admin.site.register(Voice)
# admin.site.register(Category)
# admin.site.register(Soundbyte)
# admin.site.register(Story)
# admin.site.register(StoryCategory)
