from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # ex: /
    #    url(r'^$', views.index, name='index'),

    url(r'^$', RedirectView.as_view(url='/workflows')),

    # list all workflows
    url(r'^workflows/$', views.render_workflows),
    url(r'^api/workflows/?$', views.workflow_list),

    # users
    url(r'^api/user/$', views.user_info),

    # workflows
    url(r'^workflows/(?P<pk>[0-9]+)/$', views.render_workflow),
    url(r'^api/workflows/(?P<pk>[0-9]+)/?$', views.workflow_detail),

    url(r'^api/workflows/(?P<pk>[0-9]+)/addmodule/?$', views.workflow_addmodule),

    url(r'^api/workflows/(?P<pk>[0-9]+)/(?P<action>(undo|redo))/?$', views.workflow_undo_redo),

    # modules
    url(r'^api/modules/?$', views.module_list),
    url(r'^api/modules/(?P<pk>[0-9]+)/?$', views.module_detail),

    url(r'^api/initmodules/$', views.init_modules2),
    url(r'^api/importfromgithub/?$', views.import_from_github),
    url(r'^api/refreshfromgithub/?$', views.refresh_from_github),

    # WfModules (Modules applied in a workflow)
    url(r'^api/wfmodules/(?P<pk>[0-9]+)/?$', views.wfmodule_detail),
    url(r'^api/wfmodules/(?P<pk>[0-9]+)/render$', views.wfmodule_render),
    url(r'^api/wfmodules/(?P<pk>[0-9]+)/input$', views.wfmodule_input),
    url(r'^api/wfmodules/(?P<pk>[0-9]+)/dataversion', views.wfmodule_dataversion),

    url(r'^public/moduledata/live/(?P<pk>[0-9]+)\.(?P<type>(csv|json))?$', views.wfmodule_public_output),

    # Parameters
    url(r'^api/parameters/(?P<pk>[0-9]+)/?$', views.parameterval_detail),
    url(r'^api/parameters/(?P<pk>[0-9]+)/event/?$', views.parameterval_event),

    url(r'^public/paramdata/live/(?P<pk>[0-9]+).png$', views.parameterval_png),

    # URL endpoint to trigger internal cron jobs
    url(r'^runcron$', views.runcron)
]
