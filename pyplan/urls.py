# """определяет схемы url для pyplan"""
from django.urls import path, include, re_path
from pyplan import views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url="/static/logo/favicon.ico", permanent = True)

app_name = 'pyplan'
urlpatterns = [
    path('accounts/', include('users.urls')),
    path('', views.index, name='index'),
    path('get_info_database/<int:select_db>', views.switching_database),
    path('wcrew_add_check/<int:pers_id>/<int:wcrew_id>/<int:select_db>', views.wcrew_add_check),
    path('write_db/<int:id_pers>/<int:status_pers>/<int:spec>/<int:wcrew_id>/<tvs_id>/<simulator_number>/<int:ttc_id>/<int:select_db>',
         views.write_in_DB),
    path('write_ppls_for_pilot/<int:id_pers>/<int:status_pers>/<int:spec>/<int:wcrew_id>/<tvs_id>/<short_name_PPLS>/<int:select_db>',
         views.write_ppls_for_pilot),
    path('remove_ppls_for_pilot/<int:id_pers>/<int:status_pers>/<int:spec>/<int:wcrew_id>/<tvs_id>/<short_name_PPLS>/<int:select_db>',
         views.remove_PPLS_for_pilot),

    path('delete_person_from_table/<int:wcrew_id>/<int:id_pers>/<int:select_db>', views.delete_person_from_table),
    path('upd_color/<int:group_id>/<int:id_crew>/<int:select_db>', views.update_color_DB, name='selected_group'),
    path('upd_color_for_refresh_check/<int:wcrew_id_one>/<int:wcrew_id_two>/<int:number>/<int:select_db>',
         views.upd_color_for_refresh_check),
    path('info_otpusklist/<int:pers_id>/<int:month_search>/<int:year_search>/<int:select_db>', views.work_schedule),

    path('create_global_colors/<int:select_db>', views.create_global_colors),
    path('color_group/<aircraft>/<int:select_db>', views.update_groups_selected),
    path('show_refresh_number_group/<int:month_search>/<int:year_search>/<int:select_db>', views.show_refresh_number_group),
    path('delete_pair_refresh_group/<int:wcrew_id_one>/<int:wcrew_id_two>/<int:select_db>', views.delete_pair_refresh_group),
    path('add_people/<type_aircraft>/<selected_month>/<int:select_db>', views.redirect_page_add_people),
    path('add_pilots_in_active_list/<int:pers_id>/<tvs_id>/<dat_month>/<int:hide_people>/<int:select_db>', views.add_pilots_in_active_list),

    path('search_sap/<int:sap_tab>/<int:select_db>', views.search_sap),
    path('read_comment_person/<int:wcrew_id>/<int:pers_id>/<int:select_db>', views.read_comment_person),
    path('write_comment_person/<comm_aim>/<int:wcrew_id>/<int:pers_id>/<int:select_db>', views.write_comment_person),

    path('display_pilots_and_instructors/<type_aircraft>/<int:number_group>/<selected_month>/<int:month>/<int:year>/<int:select_db>', views.display_pilots_and_instructors),
    path('display_all_instructors/<tvs_id>/<int:month>/<int:year>/<int:select_db>', views.display_all_instructors),

    path('show_table_of_schedule/<type_aircraft>/<simulator_number>/<int:month_search>/<int:year_search>/<int:select_db>', views.seven_trainer_320,
         name='schedule_table'),
    path('show_table_of_schedule/<type_aircraft>/<simulator_number>/<int:month_search>/<int:year_search>/<int:select_db>/<twork_id>', views.seven_trainer_320),
    path('delete_return_task_for_people/<int:wcrew_id>/<int:pers_id>/<int:ttc_id>/<int:select_db>', views.delete_return_task_for_people),
    re_path(r'^favicon\.ico$', favicon_view),
    path('find_days_of_instructors_330_350/<tvs_id>/<selected_month>/<int:select_db>', views.get_days_of_instructors_330_350),
    path('pilot_editor/<user_add>', views.pilot_editor),
    #path('i_am_watching_you', views.only_watching, name="only_watching"),
    path('instructor_edit/', views.instructor_edit_page, name="instructor_edit_page"),
    path('instructor_edit/<int:group_id>/<int:tvs_id>', views.instructor_edit_show),
    path('instructor_edit/<int:sap_id>', views.instructor_edit_show_new),
    path('instructor_edit/insert/<int:pers_id>/<int:group>/<int:tvs_id>', views.instructor_edit_insert),
    path('instructor_edit/delete/<int:pers_id>/<int:group>/<int:tvs_id>', views.instructor_edit_delete),
    path('admin_panel/', views.adminPanel),
    path('admin_panel/<int:pers_id>', views.takeUserId),
    path('alllist/', views.displayAllPilots),
    path('alllist/<int:tvs_id>', views.displayedPilot),
    # path('', views.print_sim7000_5000, name = 'printing'),
    # path('view_inst', views.InstructorsList.as_view()),
    # path('update_KRS', views.update_or_create_KRS ),
    # path('view_KRS', views.KRSList.as_view() ),
    # path('update_KRS_and_LIS', views.update_or_create_KRS_LIS_air_squadrons ),
    # path('view_KRS_and_LIS', views.KRS_and_LISList.as_view() ),
    # path('update_freelance_pilot_inst_cheek', views.update_or_create_freelance_instructor_CHECK ),
    # path('view_freelance_pilot_inst_cheek', views.freelance_pilots_CHECKList.as_view() ),
    # path('update_freelance_pilot_inst', views.update_or_create_freelance_instructor ),
    # path('view_freelance_pilot_inst', views.freelance_pilotsList.as_view() ),

    # path('', views.GroupCreate.as_view(), name='add_group'),
]