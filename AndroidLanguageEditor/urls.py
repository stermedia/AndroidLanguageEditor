from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^signin/$', 'ale.views.sign_in', name='sign in'),
                       url(r'^signup/$', 'ale.views.sign_up', name='sign in'),
                       url(r'^logout/$', 'ale.views.log_out', name='log out'),
                       url(r'^$', 'ale.views.dashboard', name='dashboard'),
                       url(r'^project/create/$', 'ale.views.create_project', name='dashboard'),
                       url(r'^project/import/(?P<project_path>.*)/$', 'ale.io_views.import_user_project',
                           name='import'),
                       url(r'^project/export/(?P<project_path>.*)/$', 'ale.io_views.export_user_project',
                           name='import'),
                       url(r'^project/(?P<project_path>.*)/$', 'ale.views.show_user_project', name='project'),
                       url(r'^json/project/(?P<project_path>.*)/cell/modify/$', 'ale.views.modify_cell',
                           name='modify cell'),
                       url(r'^json/project/(?P<project_path>.*)/$', 'ale.views.cells_data_json', name='project json'),


                       url(r'^json/shares/project/(?P<project_path>.*)/$', 'ale.share_views.get_shares',
                           name='get shares'),
                       url(r'^json/share/project/(?P<project_path>.*)/$', 'ale.share_views.share_project',
                           name='share project'),
                       url(r'^json/share/remove/project/(?P<project_path>.*)/$', 'ale.share_views.remove_share',
                           name='remove share'),
                       url(r'^share/(?P<hash_key>.*)/$', 'ale.share_views.show_shared_project', name='shared project'),
                       url(r'^json/share/cells/(?P<hash_key>.*)/$', 'ale.share_views.get_json_shared_cells',
                           name='shared project cells'),
                       url(r'^json/share/modify/cell/(?P<hash_key>.*)/$', 'ale.share_views.modify_shared_project_cell',
                           name='modify shared project'),
                       url(r'^import/shared/(?P<hash_key>.*)/$', 'ale.share_views.import_shared_project',
                           name='import shared project'),
                       url(r'^export/shared/(?P<hash_key>.*)/$', 'ale.share_views.export_shared_project',
                           name='export shared project'),


                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),
)