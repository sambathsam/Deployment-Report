from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.HomePageView, name='home'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('userlist/' ,views.UserList.as_view(),name='userlist'),
    path('reports/',views.reportList, name='report_list'),
    path('editreports/',views.edit_report, name='edit_report'),
    path(r'report/create/', views.report_create, name='report_create'),
    url(r'^report/(?P<pk>\d+)/update/$', views.report_update, name='report_update'),
    url(r'^report/(?P<pk>\d+)/delete/$', views.report_delete, name='report_delete'),
    path('hr/ajax/load-cities/', views.load_subpro, name='ajax_load_cities'),
    url(r'^export/$', views.export_users_xls, name='export_users_xls'),
    url(r'^attendence/$', views.attendence, name='attendence_xls'),
    url(r'^reportlist/$', views.reportlist, name='reportlist'),
    url(r'^reportlist/(?P<eid>\d+)$', views.reportlist_emp, name='reportlist_emp'),
    url(r'^useredit/(?P<eid>\d+)$', views.edit_user, name='edit_user'),
    url(r'^review/(?P<eid>\d+)$', views.review, name='review'),
    url(r'^reviewlist/$', views.reviewlist, name='reviewlist'),
    url(r'^reviewlist/(?P<eid>\d+)$', views.reviewlist_emp, name='reviewlist_emp'),
]