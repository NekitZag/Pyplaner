import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from accessDB import name, password, ip_address_stat, ip_address
import calendar
import datetime
import fdb
import django
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import *
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db import connection
import logging
import pytz

index_select_db = 1
db_selector = [ip_address_stat, ip_address]
list_sessions_time = [datetime.time(hour=0, minute=5), datetime.time(hour=4, minute=10),
                      datetime.time(hour=8, minute=15),
                      datetime.time(hour=13, minute=15), datetime.time(hour=17, minute=20)]
list_technical_time = [datetime.time(hour=12, minute=45), datetime.time(hour=22)]

logging.basicConfig(
    level=logging.DEBUG,
    filename="ConnectLog.log",
    format=f"%(levelname)s - %(message)s"
)


def editor_permission(*group_names):  # Декоратор для проверки групп пользователей
    """Requires user membership in at least one of the groups passed in."""

    def in_groups1(u1):
        if bool(u1.groups.filter(name__in=group_names)) | u1.is_superuser:
            return True

    return user_passes_test(in_groups1)


@login_required
def switching_database(request, select_db):
    con = fdb.connect(dsn=ip_address, user=name, password=password, charset='WIN1251')
    response = JsonResponse({"db_info": con.db_info(fdb.isc_info_db_id), "index_select_db": select_db})
    con.close()
    return response


@login_required
def index(request, month_now=datetime.datetime.now().month, year_now=datetime.datetime.now().year):
    context = {'count_day': days(month_now, year_now),
               'working_trainers': [[[["None"] * 10] * 4] * 5] * calendar.monthrange(year_now, month_now)[1],
               }
    ip_connected = get_client_ip(request)
    time_log = datetime.datetime.now() + datetime.timedelta(hours=3)  # реализовано для linux
    logging.info(f"{ip_connected}:{time_log.strftime('%d.%b.%y %H:%M:%S')} - вход")
    print(ip_connected)
    return render(request, 'pyplan/index.html', context)


@login_required
def seven_trainer_320(request, type_aircraft, simulator_number, month_search,
                      year_search, select_db, twork_id="TC"):  
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    if request.user.groups.filter(name="View_320").exists():
        if type_aircraft != '320':
            response = JsonResponse({"error": "Вы не можете просматривать другие типы самолетов, кроме 320."})
            response.status_code = 501
            return response
    if request.user.groups.filter(name="View_330_350").exists():
        if not type_aircraft in ['330', '350']:
            response = JsonResponse({"error": "Вы не можете просматривать другие типы самолетов, кроме 330 и 350."})
            response.status_code = 501
            return response
    if request.user.groups.filter(name="View_737").exists():
        if type_aircraft != '737':
            response = JsonResponse({"error": "Вы не можете просматривать другие типы самолетов, кроме 737."})
            response.status_code = 501
            return response
    if request.user.groups.filter(name="View_777").exists():
        if type_aircraft != '777':
            response = JsonResponse({"error": "Вы не можете просматривать другие типы самолетов, кроме 777."})
            response.status_code = 501
            return response
    if request.user.groups.filter(name="View_all").exists():
        if not type_aircraft in ['320', '330', '350', '737', '777']:
            response = JsonResponse({"error": "Вы не можете просматривать другие типы самолетов"})
            response.status_code = 501
            return response

    # if (request.POST.getlist('arr_sessions_time[]')!=None):
    #     list_sessions_time=[datetime.datetime.strptime('1.1.2000 '+parse_time,'%d.%m.%Y %H:%M:%S').time() for parse_time in request.POST.getlist('arr_sessions_time[]')]
    # else:
    #     list_sessions_time = list_sessions_time
    # if (request.POST.getlist('arr_technical_time[]')!=None):
    #     list_technical_time= [datetime.datetime.strptime('1.1.2000 '+parse_time,'%d.%m.%Y %H:%M:%S').time()  for parse_time in request.POST.getlist('arr_technical_time[]')]
    # else:
    #     list_technical_time = list_technical_time

    start_apptime = time.time()

    beginning_selected_month = datetime.date(year=year_search, month=month_search, day=1)
    list_sessions_time.sort()
    list_technical_time.sort()
    field_prim = " wm.prim"
    request_month_column_headers = """
        select distinct """ \
        + ("'0'", "substring(wm.prim from position('"+simulator_number.replace('%','') +"',wm.prim) for "+ str(len(simulator_number.replace('%','')))+")")[simulator_number != "null"] +"""
        , stripdate1(wm.dat_beg),stripdate1(wm.dat_end)
        from wcrew_main wm 
        where wm.dat_beg between ? and ?
        and wm.twork_id='""" + twork_id + """'
        and (wm.tvs_id like """+type_aircraft+")"

    query_parameters = [beginning_selected_month, beginning_selected_month + relativedelta(months=1, minutes=-1)]
    if simulator_number != "null":
        request_month_column_headers += " and wm.prim like '" + simulator_number + '%' + "'"
    cur = con.cursor()
    try:
        cur.execute(request_month_column_headers + "order by 2,3", query_parameters)
    except Exception as exc:
        print(
            "--------------------Ошибка в выборке заголовка(времен) сессий таблицы расписания---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка в выборке заголовка(времен) сессий таблицы расписания"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        month_column_headers = cur.fetchall()
        print(simulator_number)
    finally:
        cur.close()
        cur.__del__()

    request_crew_in_session = """
            --           0             1           2            3          4           5           6          7         8
            select wm.id_wcrew, pm.id_pers, wm.dat_beg, wm.dat_end, ptvs.spec, ptvs.state, pm.f_name, pm.m_name, pm.l_name,
             --                                               9
            case when cr.status>1 then null else cr.status end as status,
             --    10          11        12         13 
            td.short_name, tks.color, tks.descr, tit.color, 
             --                                                  14           15           16         17               18             19          20
            case when pm.podraz_id=4622 then 1 else 0 end as Petersburg, tks.id_ttc, cr.comm_aim, cr.ttc_id,list(tp.short_name), cr.user_add, cr.dat_ins
            from wcrew_main wm
            left join wcrew_crew cr on cr.wcrew_id=wm.id_wcrew
            left join pers_main pm on cr.pers_id=pm.id_pers
            left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ((ptvs.spec<30 and pm.flight='Y') or (ptvs.spec=80 and pm.flight='N')) and (ptvs.tvs_id like """+type_aircraft.replace('wm.','ptvs.')+""") and ptvs.activ=1
            left join type_dolgn td on td.id_dolgn=pm.dolgn_id
            left join st_afl sta on sta.id_podraz=pm.podraz_id
            left join type_ktc_sesn as tks on wm.ttc_id=tks.id_ttc
            left join pers_instr_trng_new pit on pit.pers_id=cr.pers_id and (pit.tvs_id like """+type_aircraft.replace('wm.','pit.')+""")
            left join type_instr_trng tit on tit.id_grp = pit.grp_instr
            left join rezerv_ppls rp on rp.wcrew_id=wm.id_wcrew and rp.pers_id=pm.id_pers
            left join type_ppls tp on tp.id_ppls=rp.ppls_id
            where
              pm.state='Y'
              and wm.dat_beg between ? and ?
              and wm.twork_id = '""" + twork_id + """'
              and (wm.tvs_id like """+type_aircraft+""")
              --and ((ptvs.spec<30 and pm.flight='Y')
              --                                or
              --      (ptvs.spec=80 and pm.flight='N'))
            
        """
    query_parameters = [beginning_selected_month, beginning_selected_month + relativedelta(months=1, minutes=-1)]
    if simulator_number != "null":
        request_crew_in_session += " and wm.prim like '" + simulator_number + '%' + "'"
    cur2 = con.cursor()
    try:
        cur2.execute(request_crew_in_session +
                     "group by wm.id_wcrew, pm.id_pers, wm.dat_beg, wm.dat_end, ptvs.spec, ptvs.state, pm.f_name, pm.m_name, pm.l_name,"
                     "cr.status, td.short_name, tks.color, tks.descr, tit.color, Petersburg, tks.id_ttc, cr.comm_aim, cr.ttc_id, cr.user_add, cr.dat_ins "
                     "order by 3,4,10 desc,6 desc,5", query_parameters)
    except Exception as exc:
        print(
            "--------------------Ошибка в основном запросе на формирование таблицы расписания---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка в основном запросе на формирование таблицы расписания"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        simulator_schedule = cur2.fetchall()

    finally:
        cur2.close()
        cur2.__del__()
    request_empty_in_session = """
            --    0          1          2           3           4           5         
    select wm.id_wcrew, wm.dat_beg, wm.dat_end, tks.color, tks.descr , wm.ttc_id from wcrew_main wm
    left join type_ktc_sesn as tks on wm.ttc_id=tks.id_ttc
    where wm.dat_beg between ? and ? and (wm.tvs_id like """+type_aircraft+""")  and wm.twork_id = '""" + twork_id + """'
    """
    query_parameters = [beginning_selected_month, beginning_selected_month + relativedelta(months=1, minutes=-1)]
    if simulator_number != "null":
        query_parameters.append(simulator_number)
        request_empty_in_session += " and wm.prim like '" + simulator_number + '%' + "'"
    cur3 = con.cursor()
    try:
        cur3.execute(request_empty_in_session + "order by 2", query_parameters)
    except Exception as exc:
        print("--------------------Ошибка в выборке пустых сессий---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка в выборке пустых сессий"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        id_session_wcrew = cur3.fetchall()
    finally:
        cur3.close()
        cur3.__del__()      # 0      1
    List_sim_schedule = [[[["none", "None",
                            #                                  2
                            month_column_headers[i][1].replace(day=j + 1, month=month_search, year=year_search),
                            #                                  3
                            month_column_headers[i][2].replace(day=j + 1, month=month_search,
                                                               year=year_search) + relativedelta(
                                days=(1, 0)[month_column_headers[i][1].time() <= month_column_headers[i][2].time()]),
                            #  4     5     6  7    8     9  10  11  12  13  14    15
                            "None", "None", "", '', 'None', '', '', '', '', '', '', 'None']] for i in
                          range(len(month_column_headers))] for j in
                         range(calendar.monthrange(year_search, month_search)[1])]
    for i in range(len(List_sim_schedule)):
        for j in range(len(List_sim_schedule[i])):
            for k in range(len(id_session_wcrew)):
                if List_sim_schedule[i][j][0][2] == id_session_wcrew[k][1] and List_sim_schedule[i][j][0][3] == \
                        id_session_wcrew[k][2]:
                    List_sim_schedule[i][j][0][0] = id_session_wcrew[k][0]
                    List_sim_schedule[i][j][0][11] = id_session_wcrew[k][3]
                    List_sim_schedule[i][j][0][12] = id_session_wcrew[k][4]
                    List_sim_schedule[i][j][0][15] = id_session_wcrew[k][5]
    if len(simulator_schedule) == 0:
        response = JsonResponse({"html": render_to_string("schedule_table.html",
                                                          {
                                                              'working_trainers': List_sim_schedule,
                                                              'month_column_headers': month_column_headers,
                                                              'count_day': days(month_search,
                                                                                year_search),
                                                              'days_off': output_of_days_off(month_search,
                                                                                             year_search)
                                                          }),
                                 "db_info": con.db_info(fdb.isc_info_db_id)})
        con.close()
        return response
    index_select_people = 0
    # select_session = 0
    for select_day in range(len(List_sim_schedule)):
        select_session = 0
        while select_session < len(List_sim_schedule[select_day]):
            if index_select_people >= len(simulator_schedule):
                break
            while List_sim_schedule[select_day][select_session][0][2] == simulator_schedule[index_select_people][2] and \
                    List_sim_schedule[select_day][select_session][0][3] == simulator_schedule[index_select_people][3]:
                if List_sim_schedule[select_day][select_session][0][1] == "None":
                    List_sim_schedule[select_day][select_session][0] = simulator_schedule[index_select_people]
                else:
                    List_sim_schedule[select_day][select_session].append(simulator_schedule[index_select_people])
                index_select_people += 1
                if index_select_people >= len(simulator_schedule):
                    break
            select_session += 1

    # mass_sission_sim_schedule = []
    # people_in_day=[]
    # tmp_time = simulator_schedule[0][2].time()
    # for sim_shed in simulator_schedule:
    #     if sim_shed[2].time() == tmp_time:
    #         people_in_day.append(sim_shed)
    #     else:
    #         tmp_time=sim_shed[2].time()
    #         mass_sission_sim_schedule.append(people_in_day)
    #         people_in_day=[]
    #         people_in_day.append(sim_shed)
    # mass_day_sim_schedule=[]
    # tmp_mass_day=[]
    # tmp_day = simulator_schedule[0][2].day
    # for mass_sim in mass_sission_sim_schedule:
    #     if mass_sim[0][2].day == tmp_day:
    #         tmp_mass_day.append(mass_sim)
    #     else:
    #         tmp_day=mass_sim[0][2].day
    #         mass_day_sim_schedule.append(tmp_mass_day)
    #         tmp_mass_day=[]
    #         tmp_mass_day.append(mass_sim)
    # for m in mass_day_sim_schedule:
    #     print(m)
    #     print("---------------------------------Test")
    # for i in range(len(List_sim_schedule)):
    #     if i+1>len(mass_day_sim_schedule):
    #         break
    #     for List_sim in range(len(List_sim_schedule[i])) :
    #         for mass_day in range(len( mass_day_sim_schedule[i])):
    #             if List_sim_schedule[i][List_sim][0][2]==mass_day_sim_schedule[i][mass_day][0][2]:
    #                 List_sim_schedule[i][List_sim]=mass_day_sim_schedule[i][mass_day]

    """if len(simulator_schedule[0])>=3 and isinstance(simulator_schedule[0][2], datetime.datetime):
        tmp_day =  simulator_schedule[0][2].day
        tmp_time = simulator_schedule[0][2].time()
    else:
        tmp_day = 0
        tmp_time = 0"""

    """if i != len(simulator_schedule)-1 and simulator_schedule[i][2].day == tmp_day :
        if  simulator_schedule[i][2].time() == tmp_time:
            people_in_day.append(simulator_schedule[i])
        else:
            if len(people_in_day)<4:
                people_in_day.extend([['None']*10]*(4-len(people_in_day)))
            mass_day_sim_schedule.append(people_in_day)
            people_in_day=[]
            tmp_time = simulator_schedule[i][2].time()
            people_in_day.append(simulator_schedule[i])
    else:
        if len(people_in_day) < 4:
            people_in_day.extend([['None'] * 10] * (4 - len(people_in_day)))
        mass_day_sim_schedule.append(people_in_day)
        if len(mass_day_sim_schedule)<len(list_sessions_time):
            mass_day_sim_schedule.extend([[['None']*10]*4]* (len(list_sessions_time)-len(mass_day_sim_schedule)))
        for j in range(len(list_sessions_time)):
            tmp_day_time=datetime.datetime.combine(datetime.date(year=year_search, month=month_search, day=tmp_day),list_sessions_time[j])
            if len(mass_day_sim_schedule[j][0]) == 0:
                mass_day_sim_schedule[j][0].extend(['None']*10)
                mass_day_sim_schedule[j][0][2]=tmp_day_time
            if not isinstance(mass_day_sim_schedule[j][0][2], datetime.datetime):
                mass_day_sim_schedule[j][0][2] = tmp_day_time
            if list_sessions_time[j] != mass_day_sim_schedule[j][0][2].time():
                for mass_d in range(len(mass_day_sim_schedule)):
                    if len(mass_day_sim_schedule[mass_d][0]) != 0 and isinstance(mass_day_sim_schedule[mass_d][0][2], datetime.datetime) \
                            and mass_day_sim_schedule[mass_d][0][2].time() ==list_sessions_time[j]:
                        tmp_mass_d=mass_day_sim_schedule[mass_d]
                        mass_day_sim_schedule[mass_d] = mass_day_sim_schedule[j]
                        mass_day_sim_schedule[j]=tmp_mass_d
                        #print("HERE")
        #print("_______________-")
        List_sim_schedule.append(mass_day_sim_schedule)
        people_in_day=[]
        people_in_day.append(simulator_schedule[i])
        mass_day_sim_schedule = []
        tmp_day = simulator_schedule[i][2].day
        tmp_time = simulator_schedule[i][2].time()"""
    response = JsonResponse({"html": render_to_string("schedule_table.html", {'working_trainers': List_sim_schedule,
                                                                              'month_column_headers': month_column_headers,
                                                                              'count_day': days(month_search,
                                                                                                year_search),
                                                                              'days_off': output_of_days_off(
                                                                                  month_search,
                                                                                  year_search)
                                                                              }),
                             "db_info": con.db_info(fdb.isc_info_db_id)})
    cache.clear()
    print('cache is clear!')
    print("seven trainer 320 --- %s seconds ---" % (time.time() - start_apptime))
    con.close()
    return response


def days(month, year):
    week_day = ['Пн', 'Вт', 'Cр', 'Чт', 'Пт', 'Сб', 'Вс']
    mass_day = [[i + 1, week_day[datetime.datetime(year, month, i + 1).weekday()]] for i in
                range(calendar.monthrange(year, month)[1])]

    return (mass_day)


def output_of_days_off(month, year):
    con = fdb.connect(dsn=ip_address, user=name, password=password, charset='WIN1251')
    beginning_selected_month = datetime.date(year=year, month=month, day=1)
    query_db = 'select wd.dat FROM WORKDAY wd where wd.wgr_id=1 and wd.time_w=0 and wd.dat between ? and ? order BY 1'
    cur = con.cursor()
    try:
        cur.execute(query_db, (
            beginning_selected_month, beginning_selected_month.replace(day=calendar.monthrange(year, month)[1])))
    except Exception as exc:
        print("--------------------Ошибка в выборке выходных и праздничных дней----------------------------  \n" + str(
            exc))
        response = JsonResponse({"error": "Ошибка в выборке выходных и праздничных дней"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        date_off = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    data_db = []
    for i in range(calendar.monthrange(year, month)[1]):
        data_db.append(0)
        for j in range(len(date_off)):
            if date_off[j][0].day == i + 1:
                data_db[i] = date_off[j][0].day
                break
    """ j=0
    for i in range(len(mass_day)): #цикл для объединения массива выходных и дней месяца
        mass_day[i].append(0)
        if data[j]==mass_day[i][0]: 
            mass_day[i][2]=data[j]
            j+=1
        if j==len(data): break"""
    con.close()
    return data_db


def wcrew_add_check(request, pers_id, wcrew_id, select_db):  # проверка перед добавлением людей в расписание
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    check_message = [[]]
    show_message_add_check = """
        execute procedure wcrew_add_check1 (?,?)
    """
    cur = con.cursor()
    try:
        cur.execute(show_message_add_check, [pers_id, wcrew_id])
    except Exception as exc:
        print(
            "--------------------Ошибка в процедуре проверки пересечений(отпуска, больничных и т.д.)---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка в процедуре проверки пересечений(отпуска, больничных и т.д.)"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        check_message = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    print(check_message)
    for i in range(len(check_message)):
        if isinstance(check_message[i][1], datetime.datetime) and isinstance(check_message[i][2], datetime.datetime):
            check_message[i] = [check_message[i][0], check_message[i][1].strftime('%d.%m.%y'),
                                check_message[i][2].strftime('%d.%m.%y')]
    con.close()

    return JsonResponse({'message_add_check': check_message})


@editor_permission('editor')
def displayTabPilots(request, type_aircraft, number_group,
                     selected_month, select_db, year,
                     month):  # [4840 - SSJ-100, 4139 - A330/350, 5898 - A320 №1, 5899 - A320 №2, 4462 - СПБ , 2 - все из Аэрофлота]
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    # context = None
    # if request.user.has_perm('pyplan.delete_entry'):
    #                       0          1          2        3       4           5           6               7                8              9              10
    start_apptime = time.time()
    pilot = """select case
         when (pt.last_dat-pt.penultimate_dat)<? then 1
         else 2
         --    0
       end as GRP,
       --      1             2              3             4         5        6        7
       pt.last_dat, pt.penultimate_dat, pm.sap_tab, pm.id_pers ,pm.lname,pm.fname,pm.mname,
       --    8          9 
       ptvs.spec, ptvs.state, case
         when (ptvs.state)=3 then 'Пилот Инстр.'
         else td.short_name
         --       10             11
       end as short_name, sta.short_name, 
         --                                                 12                                     
       case when pm.podraz_id=4622 then 1 else 0 end as Petersburg, 
         --                                                                                  13          14             15
       case when ptvs.tvs_id='330' or ptvs.tvs_id='350' then pt.tvs_tren else null end as tvs_tren, pt.a330_350, ptp.dat_pp_ktc
    from stafl_getdown_id_lvl(2, -1) st
    left join pers_main pm on pm.podraz_id=st.id_get
    left join type_dolgn td on td.id_dolgn=pm.dolgn_id
    left join st_afl sta on sta.id_podraz=pm.podraz_id
    left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ptvs.spec<30
    left join pers_trenag_last_dat(pm.id_pers,ptvs.tvs_id, ?, ?) pt on 0=0
    left join pers_trng_pp ptp on pm.id_pers = ptp.pers_id
    left join list_person_for_programm_ffs_pl lp on lp.pers_id=pm.id_pers and lp.tvs_id=? and lp.dat_month between ? and ?
    where pm.state='Y' and pm.flight='Y'
      and pt.output_permission=1
      and ptvs.spec<30
      and ptvs.activ=1
      and ptvs.tvs_id=? 
      and (lp.hide_people<>1 or lp.hide_people is null) 
      and (pt.last_dat between ? and ? -- в выбранном месяце
      or pt.last_dat between ? and ?   -- полгода назад
      or pt.last_dat between ? and ?   -- год назад
      or pt.penultimate_dat between ? and ?) -- год назад
    UNION
    select case
         when (pt.last_dat-pt.penultimate_dat)< ? then 1
         else 2
       end as GRP, pt.last_dat, pt.penultimate_dat, pm.sap_tab, pm.id_pers ,pm.lname,pm.fname,pm.mname,
       ptvs.spec, ptvs.state, td.short_name, sta.short_name, case when pm.podraz_id=4622 then 1 else 0 end as Petersburg, 
       case when ptvs.tvs_id='330' or ptvs.tvs_id='350' then pt.tvs_tren else null end as tvs_tren, pt.a330_350, ptp.dat_pp_ktc
            from list_person_for_programm_ffs_pl list_pers
            left join pers_main pm on pm.id_pers=list_pers.pers_id
            left join type_dolgn td on td.id_dolgn=pm.dolgn_id
            left join st_afl sta on sta.id_podraz=pm.podraz_id
            left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ptvs.spec<30 and ptvs.activ=1
            left join pers_trenag_last_dat(pm.id_pers,ptvs.tvs_id, ?, ?) pt on 0=0
            left join pers_trng_pp ptp on pm.id_pers = ptp.pers_id
            where
            list_pers.tvs_id=? and list_pers.hide_people<>1 and  list_pers.dat_month between ? and  ?
    order by 1,3
        """
    cur = con.cursor()
    selected_month = datetime.datetime.strptime('1.' + selected_month, '%d.%Y-%m')
    count_between_day = 240
    try:
        cur.execute(pilot, [count_between_day,
                            selected_month, selected_month + relativedelta(months=1, minutes=-1),
                            # pers_trenaj_last_dat
                            type_aircraft, selected_month, selected_month + relativedelta(months=1, minutes=-1),
                            # left join по скрытым/раскрытым списком пилотов
                            type_aircraft,
                            selected_month + relativedelta(months=-6),
                            selected_month + relativedelta(months=-5, minutes=-1),
                            # последние посещение тренажера 6 месяцев назад
                            selected_month, selected_month + relativedelta(months=1, minutes=-1),
                            selected_month + relativedelta(months=-12),
                            selected_month + relativedelta(months=-11, minutes=-1),
                            selected_month + relativedelta(months=-12),
                            selected_month + relativedelta(months=-11, minutes=-1),
                            # первый запрос
                            count_between_day,
                            selected_month, selected_month + relativedelta(months=1, minutes=-1),
                            type_aircraft, selected_month,
                            selected_month + relativedelta(months=1, minutes=-1)])  # второй запрос
        print("Запрос на пилотов --- %s seconds ---" % (time.time() - start_apptime))
    except Exception as exc:
        print(
            "--------------------Ошибка выборки пилотов в зависимости от выбранного месяца---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка выборки пилотов в зависимости от выбранного месяца"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        entry_pilots = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    counter_pilots = len(entry_pilots)


@editor_permission('editor')
def display_pilots_and_instructors(request, type_aircraft, number_group,
                                   selected_month, select_db, year,
                                   month):  # [4840 - SSJ-100, 4139 - A330/350, 5898 - A320 №1, 5899 - A320 №2, 4462 - СПБ , 2 - все из Аэрофлота]
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    # context = None
    # if request.user.has_perm('pyplan.delete_entry'):
    #                       0          1          2        3       4           5           6               7                8              9              10
    start_apptime = time.time()
    pilot = """select case
         when (pt.last_dat-pt.penultimate_dat)<? then 1
         else 2
         --    0
       end as GRP,
       --      1             2              3             4         5        6        7
       pt.last_dat, pt.penultimate_dat, pm.sap_tab, pm.id_pers ,pm.lname,pm.fname,pm.mname,
       --    8          9 
       ptvs.spec, ptvs.state, case
         when (ptvs.state)=3 then 'Пилот Инстр.'
         else td.short_name
         --       10             11
       end as short_name, sta.short_name, 
         --                                                 12                                     
       case when pm.podraz_id=4622 then 1 else 0 end as Petersburg, 
         --                                                                                  13          14             15
       case when ptvs.tvs_id='330' or ptvs.tvs_id='350' then pt.tvs_tren else null end as tvs_tren, pt.a330_350, ptp.dat_pp_ktc
    from stafl_getdown_id_lvl(2, -1) st
    left join pers_main pm on pm.podraz_id=st.id_get and pm.state='Y' and pm.flight='Y'
    left join type_dolgn td on td.id_dolgn=pm.dolgn_id
    left join st_afl sta on sta.id_podraz=pm.podraz_id
    left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ptvs.spec<30
    and ptvs.spec<30 and ptvs.activ=1
    left join pers_trenag_last_dat(pm.id_pers,ptvs.tvs_id, ?, ?) pt on 0=0
    left join pers_trng_pp ptp on pm.id_pers = ptp.pers_id
    left join list_person_for_programm_ffs_pl lp on lp.pers_id=pm.id_pers and (lp.tvs_id like """+type_aircraft.replace('wm.', 'lp.')+""") 
    where pm.state='Y' and pm.flight='Y'
      and pt.output_permission=1
      and ptvs.activ=1
      and (ptvs.tvs_id like """+ type_aircraft.replace('wm.', 'ptvs.') +""") 
      and (lp.hide_people<>1 or lp.hide_people is null) 
      and (pt.last_dat between ? and ? -- в выбранном месяце
      or pt.last_dat between ? and ?   -- полгода назад
      or pt.last_dat between ? and ?   -- год назад
      or pt.penultimate_dat between ? and ?) -- год назад
    UNION
    select case
         when (pt.last_dat-pt.penultimate_dat)< ? then 1
         else 2
       end as GRP, pt.last_dat, pt.penultimate_dat, pm.sap_tab, pm.id_pers ,pm.lname,pm.fname,pm.mname,
       ptvs.spec, ptvs.state, td.short_name, sta.short_name, case when pm.podraz_id=4622 then 1 else 0 end as Petersburg, 
       case when ptvs.tvs_id='330' or ptvs.tvs_id='350' then pt.tvs_tren else null end as tvs_tren, pt.a330_350, ptp.dat_pp_ktc
            from list_person_for_programm_ffs_pl list_pers
            left join pers_main pm on pm.id_pers=list_pers.pers_id
            left join type_dolgn td on td.id_dolgn=pm.dolgn_id
            left join st_afl sta on sta.id_podraz=pm.podraz_id
            left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ptvs.spec<30 and ptvs.activ=1
            left join pers_trenag_last_dat(pm.id_pers,ptvs.tvs_id, ?, ?) pt on 0=0
            left join pers_trng_pp ptp on pm.id_pers = ptp.pers_id
            where
            (list_pers.tvs_id like """+ type_aircraft.replace('wm.', 'list_pers.') +""") and list_pers.hide_people<>1 and  list_pers.dat_month between ? and  ?
    order by 1,3
        """
    cur = con.cursor()
    selected_month = datetime.datetime.strptime('1.' + selected_month, '%d.%Y-%m')
    count_between_day = 240
    try:
        cur.execute(pilot, [count_between_day,
                            selected_month, selected_month + relativedelta(months=1, minutes=-1),
                            # pers_trenaj_last_dat
                            # selected_month, selected_month + relativedelta(months=1, minutes=-1), # left join по скрытым/раскрытым списком пилотов
                            selected_month + relativedelta(months=-6),
                            selected_month + relativedelta(months=-5, minutes=-1),
                            # последние посещение тренажера 6 месяцев назад
                            selected_month, selected_month + relativedelta(months=1, minutes=-1),
                            selected_month + relativedelta(months=-12),
                            selected_month + relativedelta(months=-11, minutes=-1),
                            selected_month + relativedelta(months=-12),
                            selected_month + relativedelta(months=-11, minutes=-1),
                            # первый запрос
                            count_between_day,
                            selected_month, selected_month + relativedelta(months=1, minutes=-1), selected_month,
                            selected_month + relativedelta(months=1, minutes=-1)])  # второй запрос
        print("Запрос на пилотов --- %s seconds ---" % (time.time() - start_apptime))
    except Exception as exc:
        print(
            "--------------------Ошибка выборки пилотов в зависимости от выбранного месяца---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка выборки пилотов в зависимости от выбранного месяца"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        entry_pilots = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    counter_pilots = len(entry_pilots)

    instructor = """select pm.sap_tab, pm.id_pers, ptvs.spec, ptvs.state, pm.lname, pm.fname, pm.mname,
                    case when td.short_name is null then td.dolgn
                    else td.short_name
                    end as dolgn,
                    tit.color, pit.tvs_id, tit.id_grp, ptp.dat_pp_ktc
                from pers_instr_trng_new pit
                left join pers_main pm on pm.id_pers=pit.pers_id
                left join type_dolgn td on td.id_dolgn=pm.dolgn_id
                left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ((ptvs.spec<30 and pm.flight='Y') or (ptvs.spec=80 and pm.flight='N')) and (ptvs.tvs_id like """+ type_aircraft.replace('wm.', 'ptvs.') +""") and ptvs.activ=1 
                left join type_instr_trng tit on tit.id_grp = ?
                left join pers_trng_pp ptp on pm.id_pers = ptp.pers_id
                where
                pm.state='Y'  
                and (pit.tvs_id like """+ type_aircraft.replace('wm.', 'pit.') +""")
                and pit.grp_instr=? 
                order by tit.id_grp,pm.lname"""
    cur1 = con.cursor()
    cur2 = con.cursor()
    beginning_selected_month = datetime.date(year=year, month=month, day=1)
    ended_selected_month = beginning_selected_month + relativedelta(months=1, minutes=-1)

    expired_instr_admission = """
                            select ID_PERS,  NAME, TVS_ID,  FLPROV_ID,  MAX_DATE
                            from GET_EXPIRED_DOP_INSTRTREN(?, ?, ?, ?)
                             """
    try:
        cur1.execute(instructor, [number_group, number_group])
        print("Запрос на инструкторов --- %s seconds ---" % (time.time() - start_apptime))
        cur2.execute(expired_instr_admission,
                     [('330',type_aircraft)[type_aircraft!="'33_' or wm.tvs_id like '35_'"], number_group, beginning_selected_month, ended_selected_month])
        print("Запрос на допуски--- %s seconds ---" % (time.time() - start_apptime))
    except Exception as exc:
        print(
            "--------------------Ошибка выборки инструкторов в зависимости от группы---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка выборки инструкторов в зависимости от группы"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        entry_instructor = cur1.fetchall()
        expired_adm = cur2.fetchall()
    finally:
        cur1.close()
        cur1.__del__()
        cur2.close()
        cur2.__del__()
    if django.db.connection.ensure_connection() is None:
        print("ok connection")
    context = {'instructors': entry_instructor, 'pilots': entry_pilots, 'count_pilots': counter_pilots,
               'ex_admission': expired_adm}
    print("display instructors--- %s seconds ---" % (time.time() - start_apptime))
    con.close()
    return JsonResponse({"html": render_to_string("selected_people.html", context)})


@editor_permission('editor')
def display_all_instructors(request, tvs_id, select_db, year, month):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    start_apptime = time.time()
    all_instructors = """select pm.sap_tab, pm.id_pers, ptvs.spec, ptvs.state, pm.lname, pm.fname, pm.mname,
                       case when td.short_name is null then td.dolgn
                       else td.short_name
                       end as dolgn,
                       tit.color, pit.tvs_id, tit.id_grp
                   from pers_instr_trng_new pit
                   left join pers_main pm on pm.id_pers=pit.pers_id
                   left join type_dolgn td on td.id_dolgn=pm.dolgn_id
                   left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ((ptvs.spec<30 and pm.flight='Y') or (ptvs.spec=80 and pm.flight='N')) and (ptvs.tvs_id like """+ tvs_id.replace('wm.', 'ptvs.') +""") and ptvs.activ=1
                   left join type_instr_trng tit on tit.id_grp = pit.grp_instr
                   where
                   pm.state='Y' 
                   and (pit.tvs_id like """+ tvs_id.replace('wm.', 'pit.') +""")  
                   order by tit.id_grp,pm.lname                   
                   """

    expired_instr_admission = """
                            select ID_PERS,  NAME, TVS_ID,  FLPROV_ID,  MAX_DATE
                                from GET_EXPIRED_FOR_ALLDOPINSTR(?, ?, ?)
                           """
    cur = con.cursor()
    cur1 = con.cursor()
    beginning_selected_month = datetime.date(year=year, month=month, day=1)
    ended_selected_month = beginning_selected_month + relativedelta(months=1)

    try:
        cur.execute(all_instructors )
        cur1.execute(expired_instr_admission, [('330',tvs_id)[tvs_id!="'33_' or wm.tvs_id like '35_'"], beginning_selected_month, ended_selected_month])

    except Exception as exc:
        print("--------------------Ошибка выборки всех инструкторов---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка выборки всех инструкторов"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        entry_instructors = cur.fetchall()
        expired_instr_admission = cur1.fetchall()
    finally:
        cur.close()
        cur.__del__()
        cur1.close()
        cur1.__del__()
    if django.db.connection.ensure_connection() is None:
        print('Коннект есть')
    context = {'instructors': entry_instructors, 'ex_admission': expired_instr_admission}
    print("display all instructors--- %s seconds ---" % (time.time() - start_apptime))
    con.close()
    return JsonResponse({"html": render_to_string("selected_people.html", context)})


def create_global_colors(request, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    colors = """
           select id_ttc, '#'||color, descr from
           type_ktc_sesn
           order by 1
       """
    cur = con.cursor()
    try:
        cur.execute(colors)
    except Exception as exc:
        print("--------------------Ошибка выборки всех цветовых групп---------------------------- \n " + str(exc))
        response = JsonResponse({"error": "Ошибка выборки всех цветовых групп"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        entry_groups = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    return JsonResponse({"colors": entry_groups})


@editor_permission('editor')
def update_groups_selected(request, aircraft, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    aircraft=aircraft.replace('wm.','')
    groups = """
        select * from
        type_ktc_sesn
        where (tvs_id like """+aircraft+""")
    """
    cur = con.cursor()
    try:
        cur.execute(groups)
    except Exception as exc:
        print("--------------------Ошибка выборки цветовых групп---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка выборки цветовых групп"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        entry_groups = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    context = {"groups": entry_groups}
    con.close()
    return JsonResponse({"html": render_to_string("selected_group.html", context)})


def show_refresh_number_group(request, month_search, year_search, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    start_apptime = time.time()
    request_refresh_in_session = """
    select * from wcrew_ktc_pair wk
    left join wcrew_main wm on wm.id_wcrew=wk.wcrew_id1
    where wm.dat_beg between ? and ?
    order by  dat_beg
    """
    cur_refresh = con.cursor()
    beginning_selected_month = datetime.date(year=year_search, month=month_search, day=1)
    try:
        cur_refresh.execute(request_refresh_in_session,
                            [beginning_selected_month, beginning_selected_month + relativedelta(months=1, minutes=-1)])
    except Exception as exc:
        print(
            "--------------------Ошибка выборки номеров всех пар Refresh/Check на выбранный месяц---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка выборки номеров всех пар Refresh/Check на выбранный месяц"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        refresh_db = cur_refresh.fetchall()
    finally:
        cur_refresh.close()
        cur_refresh.__del__()
    print('Обновление REFRESH')
    mass_refresh = []
    for i in range(len(refresh_db)):
        mass_refresh.append([refresh_db[i][0], refresh_db[i][2]])
    for i in range(len(refresh_db)):
        mass_refresh.append([refresh_db[i][1], refresh_db[i][2]])
    print("show_refresh --- %s seconds ---" % (time.time() - start_apptime))
    con.close()
    return JsonResponse({"mass_refresh": mass_refresh})


@editor_permission('editor')
def delete_pair_refresh_group(request, wcrew_id_one, wcrew_id_two, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    request_delete_from_session = """
    delete from wcrew_ktc_pair wkp where (wkp.wcrew_id1=? and wkp.wcrew_id2=?) or (wkp.wcrew_id1=? and wkp.wcrew_id2=?)
    """
    cur_delete_refresh1 = con.cursor()
    try:
        cur_delete_refresh1.execute(request_delete_from_session,
                                    [wcrew_id_one, wcrew_id_two, wcrew_id_two, wcrew_id_one])
    except Exception as exc:
        print("--------------------Ошибка удаления пары Refresh/Check---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка удаления пары Refresh/Check"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur_delete_refresh1.close()
        cur_delete_refresh1.__del__()
    con.close()
    return JsonResponse({"info": 'DELETE pair refresh is sucсess'})


list_db = []


@editor_permission('editor')
def update_color_DB(request, group_id, id_crew, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    print(group_id, id_crew)
    query_update_color = """
    update wcrew_main set 
        TTC_ID = ?
    where id_wcrew = ?
    """
    cur = con.cursor()
    try:
        cur.execute(query_update_color, [(group_id, None)[group_id == 43], id_crew])
    except Exception as exc:
        print(
            "--------------------Ошибка обновления цели(цветовой группы) сессии (wcrew_main)---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка обновления цели(цветовой группы) сессии (wcrew_main)"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    print(group_id, id_crew)
    # response = JsonResponse({'error':'ERROR'})
    # return response
    con.close()
    ip_connected = get_client_ip(request)
    time_log = datetime.datetime.now() + datetime.timedelta(hours=3)  # реализовано для linux
    logging.info(f"{ip_connected}:{time_log.strftime('%d.%b.%y %H:%M:%S')}- изменение группы сесиии")
    print(ip_connected)
    return JsonResponse({"error": "ОШИБКА"})


@editor_permission('editor')
def upd_color_for_refresh_check(request, wcrew_id_one, wcrew_id_two, number, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    query_update_refresh = """
    insert into WCREW_KTC_PAIR(WCREW_ID1, WCREW_ID2, NUM) values (?, ?, ?)
    """
    cur = con.cursor()
    try:
        cur.execute(query_update_refresh, [wcrew_id_one, wcrew_id_two, number])
    except Exception as exc:
        print("--------------------Ошибка вставки пары Refresh/Check---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка вставки пары Refresh/Check"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    return JsonResponse({"none": "none"})


@editor_permission('editor')
def write_in_DB(request, id_pers, status_pers, spec, wcrew_id, tvs_id, simulator_number, ttc_id, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    # query_check_wcrew_main= """select * from wcrew_main wm
    #                         where wm.dat_beg = ? and  wm.dat_end= ? and wm.twork_id='TC' and wm.tvs_id=? and wm.prim=? """
    # tmp_check = cur.execute(query_check_wcrew_main,[dat_beg, dat_end, tvs_id, simulator_number]).fetchone()
    # if tmp_check == None:  #если в расписании тренажеров еще не появилась такая сессия с датой начала, датой окончания и типом самолета, то добавить
    #     print("No entries session!")
    #     query_insert_wcrew_main = """ insert into wcrew_main(dat_beg, dat_end, twork_id, tvs_id, prim) values (?,?,?,?,?) """
    #     cur.execute(query_insert_wcrew_main,[dat_beg,dat_end,'TC',tvs_id, simulator_number])
    #     con.commit()
    #     tmp_check = cur.execute(query_check_wcrew_main, [dat_beg, dat_end, tvs_id, simulator_number]).fetchone()
    # print(tmp_check[0])
    # print(dat_beg)
    query_write_person_with_id_crew = """insert into wcrew_crew(wcrew_id, pers_id, dolgn_id, status, ttc_id, user_add, dat_ins) values (?, ?, ?, ?, ?, ?, ?)"""
    # try: если insert невозможен по причине существования записи (найти except ошибки вставки)
    status_pers = (None, 1)[status_pers == 3]

    cur = con.cursor()
    id_user = (None, request.user.first_name)[request.user.first_name.isdigit()]
    try:
        if spec == 80: spec = 10
        cur.execute(query_write_person_with_id_crew,
                    [wcrew_id, id_pers, spec, status_pers, (ttc_id, None)[ttc_id == 0], id_user,
                     datetime.datetime.today().strftime('%d.%b.%y')])  # сменил с now на today из-за Вашуриной
    except Exception as exc:
        print(
            "--------------------Пилот уже размещен в сессии либо ошибка запроса---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Пилот уже размещен в сессии либо ошибка запроса"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    if (ttc_id in [1, 68,
                   75] and status_pers != 1):  # Если запись производится с группой Refresh/Check и человек является проверяемым
        cur1 = con.cursor()
        select_PPLS = """select id_ppls from type_ppls tp where tp.tvs_id=? and tp.tgroup_id=? and tp.short_name='ППЧЛЭ 3.1.1.'"""
        PPLS_ID = [None]
        try:
            cur1.execute(select_PPLS, [tvs_id, spec])
        except Exception as exc:
            print(
                "--------------------Ошибка выборки ППЛС при записи человека на сессию!---------------------------- \n" + str(
                    exc))
            response = JsonResponse({"error": "Ошибка выборки ППЛС при записи человека на сессию"})
            response.status_code = 501  # To announce that the user isn't allowed to publish
            con.close()
            return response
        else:
            PPLS_ID = cur1.fetchone()
        finally:
            cur1.close()
            cur1.__del__()
        if PPLS_ID[0] != None:
            cur2 = con.cursor()
            query_write_PPLS = """insert into rezerv_ppls(wcrew_id, pers_id, ppls_id, TYPE_PPLS_NPP) values (?, ?, ?, 1)"""
            try:
                cur2.execute(query_write_PPLS, [wcrew_id, id_pers, PPLS_ID[0]])
            except Exception as exc:
                print(
                    "--------------------ППЛС уже существует либо ошибка запроса---------------------------- \n" + str(
                        exc))
                response = JsonResponse({"error": "ППЛС уже существует либо ошибка запроса"})
                response.status_code = 501  # To announce that the user isn't allowed to publish
                con.close()
                return response
            else:
                con.commit()
                print("  Write PPLS with ppls_id = " + str(PPLS_ID[0]))
            finally:
                cur2.close()
                cur2.__del__()
    # print([wcrew_id, id_pers, status_pers, id_user, datetime.date.today().strftime("%d.%b.%y")])
    # #except :
    response = JsonResponse({"something": "something"})
    con.close()
    ip_connected = get_client_ip(request)
    time_log = datetime.datetime.now() + datetime.timedelta(hours=3)  # реализовано для linux
    logging.info(f"{ip_connected}:{time_log.strftime('%d.%b.%y %H:%M:%S')} - занесение пилота в сессию")
    print(ip_connected)
    return response


@editor_permission('editor')
def write_ppls_for_pilot(request, id_pers, status_pers, spec, wcrew_id, tvs_id, short_name_PPLS, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    if (status_pers != 3):
        cur1 = con.cursor()
        select_PPLS = """select id_ppls from type_ppls tp where tp.tvs_id=? and tp.tgroup_id=? and tp.short_name=?"""
        try:
            cur1.execute(select_PPLS, [tvs_id, spec, short_name_PPLS])
        except Exception as exc:
            print("--------------------Ошибка выборки ППЛС---------------------------- \n" + str(exc))
            response = JsonResponse({"error": "Ошибка выборки ППЛС"})
            response.status_code = 501  # To announce that the user isn't allowed to publish
            con.close()
            return response
        else:
            PPLS_ID = cur1.fetchone()
        finally:
            cur1.close()
            cur1.__del__()
        if PPLS_ID[0] != None:
            cur2 = con.cursor()
            query_write_PPLS = """insert into rezerv_ppls(wcrew_id, pers_id, ppls_id, TYPE_PPLS_NPP) values (?, ?, ?, 1)"""
            try:
                cur2.execute(query_write_PPLS, [wcrew_id, id_pers, PPLS_ID[0]])
            except Exception as exc:
                print(
                    "--------------------Ошибка вставки ППЛС для человека на сессии---------------------------- \n" + str(
                        exc))
                response = JsonResponse({"error": "Ошибка вставки ППЛС для человека на сессии"})
                response.status_code = 501  # To announce that the user isn't allowed to publish
                con.close()
                return response
            else:
                print("  Other PPLS whith ppls_id = " + str(PPLS_ID[0]))
                con.commit()
            finally:
                cur2.close()
                cur2.__del__()
    con.close()
    return JsonResponse({"None": "None"})


@editor_permission('editor')
def remove_PPLS_for_pilot(request, id_pers, status_pers, spec, wcrew_id, tvs_id, short_name_PPLS, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    if (status_pers != 3):
        cur1 = con.cursor()
        select_PPLS = """select id_ppls from type_ppls tp where tp.tvs_id=? and tp.tgroup_id=? and tp.short_name=?"""
        try:
            cur1.execute(select_PPLS, [tvs_id, spec, short_name_PPLS])
        except Exception as exc:
            print("--------------------Ошибка выборки ППЛС для удаления---------------------------- \n" + str(exc))
            response = JsonResponse({"error": "Ошибка выборки ППЛС для удаления"})
            response.status_code = 501  # To announce that the user isn't allowed to publish
            con.close()
            return response
        else:
            PPLS_ID = cur1.fetchone()
        finally:
            cur1.close()
            cur1.__del__()
        if PPLS_ID[0] != None:
            cur2 = con.cursor()
            query_remove_PPLS = "delete from rezerv_ppls where wcrew_id=? and pers_id=? and ppls_id=? and type_ppls_npp=1"
            try:
                cur2.execute(query_remove_PPLS, [wcrew_id, id_pers, PPLS_ID[0]])
            except Exception as exc:
                print(
                    "--------------------Ошибка удаления ППЛС для человека на сессии---------------------------- \n" + str(
                        exc))
                response = JsonResponse({"error": "Ошибка удаления ППЛС для человека на сессии"})
                response.status_code = 501  # To announce that the user isn't allowed to publish
                con.close()
                return response
            else:
                print("  Delete PPLS pers_id = " + str(id_pers) + " wcrew_id = " + str(wcrew_id))
                con.commit()
            finally:
                cur2.close()
                cur2.__del__()
    con.close()
    return JsonResponse({"None": "None"})


@editor_permission('editor')
def delete_person_from_table(request, wcrew_id, id_pers, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    query_delete_person = """
      DELETE FROM wcrew_crew WHERE wcrew_id = ? and pers_id = ?
    """
    cur = con.cursor()
    try:
        cur.execute(query_delete_person, [wcrew_id, id_pers])
    except Exception as exc:
        print("--------------------Ошибка удаления человека с cессии---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка удаления человека с cессии"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    ip_connected = get_client_ip(request)
    time_log = datetime.datetime.now() + datetime.timedelta(hours=3)  # реализовано для linux
    logging.info(f"{ip_connected}:{time_log.strftime('%d.%b.%y %H:%M:%S')} - удаление человека с сессии")
    print(ip_connected)
    return JsonResponse({"error": "ОШИБКА"})


def work_schedule(request, pers_id, month_search, year_search, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    query_display_otpusk = """
    select lg.TZAD_ID as ID, lg.NUMBER, pl.DAT_WORK_BEG, pl.DAT_WORK_END,
       CAST(-1 AS SMALLINT ) as TW_ID  from PERS_LEGS pl  left join LEGS lg on lg.ID_LEG=pl.LEG_ID where pl.PERS_ID=? -- 1
      and lg.ID_LEG=pl.LEG_ID
      and pl.DAT_WORK_BEG between ?-1 and ? -- 2 3
      and lg.DAT_DVG_OFF>?-27               --4
    union
    SELECT  WCR.ID_WCREW, twcr.name_work, CR.DAT_BEG, CR.DAT_END,
        TWCR.TWORK_ID
     FROM WCREW_CREW CR
      LEFT JOIN  WCREW_MAIN WCR ON CR.WCREW_ID=WCR.ID_WCREW
      LEFT JOIN TYPE_WORKCREW TWCR ON  TWCR.ID_TWORK= WCR.TWORK_ID
      -- left join TYPE_WORK tw on tw.id_twork=twcr.twork_id
      WHERE CR.PERS_ID=?        -- 5
        AND CR.DAT_BEG between ?-1 and ?  -- 6  7
        and CR.DAT_BEG<=CR.DAT_END
        AND CR.DAT_END>?  -- 8
    UNION
    select O.ID_PN AS id,tw.id_num,O.DAT_BEG, O.DATE_END,O.TWORK_ID from PERS_OTPUSKLIST O
      join TYPE_WORK tw on tw.ID_TWORK=O.TWORK_ID WHERE O.PERS_ID=?  --9
        and O.TWORK_ID>0
        --             10                11
        and O.DAT_BEG<=? AND O.DATE_END>=?
    UNION 
    SELECT pv.ID_VLAK , 'MK', pv.dat_plan,pv.dat_plan_end,
                  Po.TWORK_ID
    FROM
      PERS_VLAK PV
     LEFT JOIN PERS_OTPUSKLIST PO ON PO.ID_PN=PV.ID_WORK  LEFT JOIN TYPE_WORK TW ON TW.ID_TWORK= PO.TWORK_ID
    WHERE   PV.PERS_ID=? --12
    --                   13                  14                                                                                                                                                    
    and PV.dat_plan_end>=? AND  PV.dat_plan<=?
    UNION 
                                                                                                                                                --  15
    SELECT PM.ID_PK, tw.id_num, PM.DAT_B, PM.DAT_E, PM.TWORK_ID FROM  PERS_MISSION PM  join TYPE_WORK tw on tw.ID_TWORK=pm.TWORK_ID WHERE PM.PERS_ID=? and  PM.TWORK_ID=10
      --             16               17                                                                                                                                                                                
       AND PM.DAT_B<=?  AND PM.DAT_E>=?
    UNION 
                                                                                                                                                         -- 18
    SELECT PKV.ID_PK, tw.id_num, PKV.DAT_BEG, PKV.DAT_END, pkv. TWORK_ID FROM PERS_KVAL PKV  join TYPE_WORK tw on tw.ID_TWORK=pkv.TWORK_ID WHERE PKV.PERS_ID=?
              --           19                   20
          AND PKV.DAT_BEG<= ?  AND PKV.DAT_END>=?
          AND PKV.TWORK_ID>0
    UNION                                                                                                                                  --   21
    SELECT tb.ID_PK, tw.id_num , tb.DAT, tb.DAT, tb. TWORK_ID FROM PERS_TABEL tb  join TYPE_WORK tw on tw.ID_TWORK=tb.TWORK_ID WHERE tb.PERS_ID=?
             --             22     23
          AND tb.DAT between ? and ?
          AND (tb.TWORK_ID+0)=33
          and (tb.TWORK_ID+0)=57
    union
    select 0, 'ВЫХ', tz.datb_zvx,  tz.date_zvx, tz.gp_notes  from temp_zvx tz
             --          24
        where tz.pers_id=?
            --               25      26
    and  tz.datb_zvx between ?-1 and ?
       UNION                                                                                                                                  --   27
    SELECT tb.ID_PK, tw.id_num , tb.DAT, tb.DAT, tb. TWORK_ID FROM PERS_TABEL tb  join TYPE_WORK tw on tw.ID_TWORK=tb.TWORK_ID WHERE tb.PERS_ID=?
             --             28     29
          AND tb.DAT between ? and ?
          AND tw.ID_TWORK=57
       union                                                                                  --30
      select pub.id_pk, 'День Рождения', encode_date(iday(pub.birthday),imonth(pub.birthday), iyear(?)),
      --                                                        31
    encode_date(iday(pub.birthday),imonth(pub.birthday), iyear(?)), 0
    from pers_public pub
        --                32
        where pub.pers_id=?
        --                                               33      34                                                         35                  36
       and pub.birthday between encode_date(iday(?-1),imonth(?-1),iyear(pub.birthday)) and encode_date(iday(?),imonth(?),iyear(pub.birthday))
    ORDER BY 2
    """
    dat_beg = datetime.datetime(year=year_search, month=month_search, day=1)
    dat_end_birthday = dat_beg + relativedelta(months=1, minutes=-1)
    dat_end = dat_beg + relativedelta(months=1, days=7)
    dat_beg += relativedelta(days=-7)
    cur = con.cursor()
    try:
        cur.execute(query_display_otpusk,
                    # 1       2         3        4        5        6        7        8        9
                    [pers_id, dat_beg, dat_end, dat_beg, pers_id, dat_beg, dat_end, dat_beg, pers_id,
                     #  10       11       12       13       14       15       16       17       18
                     dat_end, dat_beg, pers_id, dat_beg, dat_end, pers_id, dat_end, dat_beg, pers_id,
                     #  19       20       21       22       23       24       25       26       27      
                     dat_end, dat_beg, pers_id, dat_beg, dat_end, pers_id, dat_beg, dat_end, pers_id,
                     # 28       29       30       31       32       33        34        35      36
                     dat_beg, dat_end, dat_beg, dat_beg, pers_id, dat_beg, dat_beg, dat_end_birthday,
                     dat_end_birthday])  # """"""
    except Exception as exc:
        print("--------------------Ошибка показа наряда(занятости) человека---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка показа наряда(занятости) человека"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        mass_display_otpusk = cur.fetchall()
        print(mass_display_otpusk)
    finally:
        cur.close()
        cur.__del__()
    List_otpusk = [[[], (dat_beg + relativedelta(days=j)).date(), None, None, None, False, False]
                   # Массив создания таблицы наряда в HTML
                   # задания      день месяца                нач.  кон. время  ноч.   спб.
                   for j in range((dat_end - dat_beg).days)]
    for j in range(len(mass_display_otpusk)):
        for i in range(len(List_otpusk)):
            if List_otpusk[i][1] >= mass_display_otpusk[j][2].date() and List_otpusk[i][1] <= mass_display_otpusk[j][
                3].date():
                if mass_display_otpusk[j][1] == 'Тренажер КТС':  # Добавление имени задания
                    List_otpusk[i][0].append('ТР')
                elif mass_display_otpusk[j][1] == 'Тренажер водный':
                    List_otpusk[i][0].append('ТВ')
                elif mass_display_otpusk[j][1] == 'Тренажер Суша':
                    List_otpusk[i][0].append('ТС')
                elif mass_display_otpusk[j][1] == 'УТ':
                    pass
                else:
                    List_otpusk[i][0].append(mass_display_otpusk[j][1])
                if List_otpusk[i][1] == mass_display_otpusk[j][2].date() and List_otpusk[i][
                    2] == None:  # Если дата нач. задания равна дню месяца таблицы,
                    List_otpusk[i][2] = mass_display_otpusk[j][
                        2]  # то записать начало задания в ячейку "начало 1-го задания"
                if List_otpusk[i][1] == mass_display_otpusk[j][
                    3].date():  # Если дата кон. задания равна дню месяца таблицы,
                    List_otpusk[i][3] = mass_display_otpusk[j][
                        3]  # то записать конец задания в ячейку "конец последнего"

    for i in range(len(List_otpusk)):
        List_otpusk[i][1] = List_otpusk[i][1].day
        if (i + 1 < len(List_otpusk)) and isinstance(List_otpusk[i + 1][2], datetime.datetime) and isinstance(
                List_otpusk[i][3], datetime.datetime):
            dif_task = List_otpusk[i + 1][2] - List_otpusk[i][3]
            minutes_dif = str(int((dif_task).total_seconds() / 60 % 60))
            List_otpusk[i][4] = str(int((dif_task).total_seconds() / 3600)) + ":" + \
                                ("", "0")[
                                    len(minutes_dif) == 1] + minutes_dif  # кол-во часов и минут между заданиями одного дня
        else:
            if (i + 1 < len(List_otpusk)) and not isinstance(List_otpusk[i + 1][2], datetime.datetime) and isinstance(
                    List_otpusk[i][3], datetime.datetime):
                j = i + 1
                while j < len(List_otpusk):
                    if isinstance(List_otpusk[j][2], datetime.datetime):
                        dif_task = List_otpusk[j][2] - List_otpusk[i][3]
                        minutes_dif = str(int((dif_task).total_seconds() / 60 % 60))
                        List_otpusk[i][4] = str(int((dif_task).total_seconds() / 3600)) + ":" + \
                                            ("", "0")[
                                                len(minutes_dif) == 1] + minutes_dif  # кол-во часов и минут между заданиями разницей более одного дня
                        break
                    j += 1
        if isinstance(List_otpusk[i][2], datetime.datetime):
            if datetime.time(hour=22) <= List_otpusk[i][2].time() or List_otpusk[i][2].time() <= datetime.time(hour=6):
                List_otpusk[i][5] = True  # ночное задание
            List_otpusk[i][2] = List_otpusk[i][2].strftime('%H:%M')  # Время начала задания
        if isinstance(List_otpusk[i][3], datetime.datetime):
            List_otpusk[i][3] = List_otpusk[i][3].strftime('%H:%M')  # Время очончания задания

    # otpusk_list = [[i[1], time.mktime(i[2].timetuple())*1000, time.mktime(i[3].timetuple())*1000]  for i in mass_display_otpusk]
    # print(otpusk_list)
    con.close()
    ip_connected = get_client_ip(request)
    time_log = datetime.datetime.now() + datetime.timedelta(hours=3)  # реализовано для linux
    logging.info(f"{ip_connected}:{time_log.strftime('%d.%b.%y %H:%M:%S')} - просмотр наряда человека")

    return JsonResponse({"mass_display_otpusk": List_otpusk,
                         "days_off_pre_month":output_of_days_off(dat_beg.month,dat_beg.year),
                         "days_off_next_month":output_of_days_off(dat_end.month,dat_end.year)})


@editor_permission('editor')
def redirect_page_add_people(request, type_aircraft, selected_month, select_db):
    print("render")
    context = {'type_vs': type_aircraft, 'selected_month': selected_month}
    return JsonResponse({"html": render_to_string("pyplan/add_people.html", context)})


@editor_permission('editor')
def search_sap(request, sap_tab, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    query = """select pm.sap_tab,pm.id_pers,pm.lname,pm.fname,pm.mname, ptvs.spec, ptvs.state,
            case when td.short_name is null then td.dolgn
            else td.short_name
            end as dolgn,
            case when sta.short_name is null then sta.full_name
            else sta.short_name
            end as podraz,
            ptvs.tvs_id
            from stafl_getdown_id_lvl(2, -1) st
            left join pers_main pm on pm.podraz_id=st.id_get
            left join type_dolgn td on td.id_dolgn=pm.dolgn_id
            left join st_afl sta on sta.id_podraz=pm.podraz_id
            left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ptvs.spec<30
            where
            pm.state='Y' and pm.flight='Y' and pm.fd_cc=0 and ptvs.activ=1 and pm.sap_tab = ?
            and ptvs.activ=1 """  # and  td.short_name = 'пилот инстр.'
    cur = con.cursor()
    try:
        cur.execute(query, [sap_tab])
    except Exception as exc:
        print("------------------------Ошибка поиска по SAP номеру---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка поиска по SAP номеру"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        pilots = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    print(pilots)
    if django.db.connection.ensure_connection() is None:
        print("ok connection")
    context = {'add_pilots': pilots}
    con.close()
    return JsonResponse({"html": render_to_string("template_add_people.html", context), "pilot_id": pilots})


@editor_permission('editor')
def add_pilots_in_active_list(request, pers_id, dat_month, tvs_id, hide_people, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    add_pilots = """update or insert into list_person_for_programm_ffs_pl(pers_id, dat_month, tvs_id,hide_people) values (?,?,?,?) """
    cur = con.cursor()
    try:
        cur.execute(add_pilots, [pers_id, dat_month, tvs_id, hide_people])
    except Exception as exc:
        print("---------------------------Ошибка добавления пилота в ручной список------------------------- \n" + str(
            exc))
        response = JsonResponse({"error": "Ошибка добавления пилота в ручной список"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    print('Добавлен пилот в ручной список: ' + str(pers_id) + " " + dat_month + " " + '0')
    # except :
    response = JsonResponse({"error": "ОШИБКА"})
    con.close()
    return response


def delete_pilots_in_active_list():
    pass


@editor_permission('editor')
def read_comment_person(request, wcrew_id, pers_id, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    r_comm_pers = """select comm_aim from wcrew_crew wcr where wcr.wcrew_id=? and wcr.pers_id=?"""
    cur = con.cursor()
    try:
        cur.execute(r_comm_pers, [wcrew_id, pers_id])
    except Exception as exc:
        print(
            "----------------------------Ошибка чтения комментария для человека на сессии---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка чтения комментария для человека на сессии"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        comment = cur.fetchone()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    return JsonResponse({"comment": comment})


def get_client_ip(request):
    nickname = request.user.last_name
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(', ')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip, nickname


@editor_permission('editor')
def write_comment_person(request, comm_aim, wcrew_id, pers_id, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    r_comm_pers = """update wcrew_crew set 
        comm_aim = ?
    where wcrew_id = ? and pers_id= ?
    """
    cur = con.cursor()
    try:
        cur.execute(r_comm_pers, [(comm_aim, None)[comm_aim == '`'], wcrew_id, pers_id])
    except Exception as exc:
        print(
            "----------------------------Ошибка записи комментария для человека на сессии-------------------------------  \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка записи комментария для человека на сессии"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    return JsonResponse({"comment": comm_aim})


@editor_permission('editor')
def delete_return_task_for_people(request, wcrew_id, pers_id, ttc_id, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    wr_ttc_pers = """update wcrew_crew set 
            ttc_id = ?
        where wcrew_id = ? and pers_id= ?
        """
    cur = con.cursor()
    try:
        cur.execute(wr_ttc_pers, [(ttc_id, None)[ttc_id == 0 or ttc_id == 43], wcrew_id, pers_id])
    except Exception as exc:
        print(
            "------------------------------Ошибка удаления/записи задачи (ttc_id) для человека на сессии------------------------------\n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка удаления/записи задачи (ttc_id) для человека на сессии"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    return JsonResponse({"comment": 'ttc'})


def get_days_of_instructors_330_350(request, tvs_id, selected_month, select_db):
    con = fdb.connect(dsn=db_selector[select_db], user=name, password=password, charset='WIN1251')
    request_instructor_days = """
        select wc.pers_id,  list(distinct extract(day from wc.dat_beg)) from wcrew_main wm 
        left join wcrew_crew wc on wm.id_wcrew=wc.wcrew_id
        where wc.status=1
        and wm.tvs_id= ?
        and wm.dat_beg between ? and ? 
        and wm.twork_id = 'TC'
        group by 1"""
    cur = con.cursor()
    beginning_selected_month = datetime.datetime.strptime('1.' + selected_month, '%d.%Y-%m')
    try:
        cur.execute(request_instructor_days,
                    [tvs_id, beginning_selected_month, beginning_selected_month + relativedelta(months=1, minutes=-1)])
    except Exception as exc:
        print(
            "--------------------Ошибка выборки дней тренажеров для инструкторов 330/350---------------------------- \n" + str(
                exc))
        response = JsonResponse({"error": "Ошибка выборки дней тренажеров для инструкторов 330/350"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        tmp_days = cur.fetchall()
        instructor_days = []
        for inst_d in tmp_days:
            mass_days = [int(item) for item in inst_d[1].split(',')]
            instructor_days.append([inst_d[0], mass_days])
    finally:
        cur.close()
        cur.__del__()
        con.close()
    return JsonResponse({'instructor_days': instructor_days})


@editor_permission('editor')
def pilot_editor(request, user_add):
    try:
        tmp = User.objects.get(first_name=user_add).last_name
        print(f"pilot-editor - {tmp}")
    except:
        tmp = None
    return JsonResponse({'editor': tmp})


@editor_permission('editor')
def instructor_edit_page(request):
    if request.user.is_staff:
        return render(request, 'pyplan/instr_edit.html')


@editor_permission('editor')
def instructor_edit_show(request, group_id, tvs_id):
    try:
        con = fdb.connect(dsn=db_selector[1], user=name, password=password, charset='WIN1251')  # ебаный хадркод
        cur = con.cursor()
        query_db = """select pm.sap_tab, pm.id_pers, ptvs.spec, ptvs.state, pm.lname, pm.fname, pm.mname,
                case when td.short_name is null then td.dolgn
                else td.short_name
                end as dolgn,
                tit.color, pit.tvs_id, tit.id_grp, ptp.dat_pp_ktc
            from pers_instr_trng_new pit
            left join pers_main pm on pm.id_pers=pit.pers_id
            left join type_dolgn td on td.id_dolgn=pm.dolgn_id
            left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ((ptvs.spec<30 and pm.flight='Y') or 
            (ptvs.spec=80 and pm.flight='N')) and ptvs.tvs_id = ? and ptvs.activ=1 
            left join type_instr_trng tit on tit.id_grp = ?
            left join pers_trng_pp ptp on pm.id_pers = ptp.pers_id
            where
            pm.state='Y'  
            and pit.tvs_id = ?
            and pit.grp_instr=? 
            order by tit.id_grp,pm.lname
        """
        cur.execute(query_db, [str(tvs_id), group_id, str(tvs_id), group_id])
        request = cur.fetchall()
        con.close()
        cur.close()
        cur.__del__()
        context = {'instr_uses': request}
        return JsonResponse({"html": render_to_string("instr/instr_show.html", context)})
    except:
        print('DB is not worK! WAITING!')
        return JsonResponse({"html": render_to_string("instr/instr_show.html", context)})


@editor_permission('editor')
def instructor_edit_show_new(request, sap_id):
    con = fdb.connect(dsn=db_selector[1], user=name, password=password, charset='WIN1251')  # ебаный хадркод
    query = """   select pm.id_pers,pm.lname, pm.fname,pm.mname,case when td.short_name is null then td.dolgn
                    else td.short_name
                    end as dolgn
                  from pers_main pm
                  left join type_dolgn td on td.id_dolgn=pm.dolgn_id
                  where pm.sap_tab = ?
                  """
    cur = con.cursor()
    try:
        cur.execute(query, [sap_id])
    except Exception as exc:
        print("------------------------Ошибка поиска по SAP номеру---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка поиска по SAP номеру"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        pilots = cur.fetchall()
    finally:
        cur.close()
        cur.__del__()
    if django.db.connection.ensure_connection() is None:
        print("ok connection")
    context = {'add_pilots': pilots}
    con.close()
    return JsonResponse({"html": render_to_string("instr/instr_show_new.html", context)})


@editor_permission('editor')
def instructor_edit_insert(request, pers_id, group, tvs_id):
    con = fdb.connect(dsn=db_selector[1], user=name, password=password, charset='WIN1251')  # ебаный хадркод
    query = """ insert into pers_instr_trng_new (PERS_ID, GRP_INSTR, TVS_ID) values (?, ?, ?)"""
    cur = con.cursor()
    try:
        cur.execute(query, [pers_id, group, tvs_id])
    except Exception as exc:
        print("------------------------Ошибка поиска по SAP номеру---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка поиска по SAP номеру"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    return JsonResponse({"html": render_to_string("instr/instr_show.html")})


@editor_permission('editor')
def instructor_edit_delete(request, pers_id, group, tvs_id):
    con = fdb.connect(dsn=db_selector[1], user=name, password=password, charset='WIN1251')  # ебаный хадркод
    query = """delete from pers_instr_trng_new pp
                where pp.PERS_ID = ? 
                and GRP_INSTR = ?
                and TVS_ID = ? 
    """
    cur = con.cursor()
    try:
        cur.execute(query, [pers_id, group, tvs_id])
    except Exception as exc:
        print("------------------------Ошибка поиска по SAP номеру---------------------------- \n" + str(exc))
        response = JsonResponse({"error": "Ошибка поиска по SAP номеру"})
        response.status_code = 501  # To announce that the user isn't allowed to publish
        con.close()
        return response
    else:
        con.commit()
    finally:
        cur.close()
        cur.__del__()
    con.close()
    return JsonResponse({"html": render_to_string("instr/instr_show.html")})


@editor_permission('editor')
def adminPanel(request):
    if request.user.is_superuser:
        return render(request, 'admin panel/admin_panel.html')


@editor_permission('editor')
def takeUserId(request, pers_id):
    con = fdb.connect(dsn=ip_address, user=name,
                      password=password, charset='WIN1251')  # Подключение к базе данных
    cur = con.cursor()
    query_db = """
                        select us.id_user from users  us
                        left join pers_main pm on pm.id_pers = us.pers_id
                        where pm.id_pers = ?
                        """
    cur.execute(query_db, [pers_id])
    request = cur.fetchone()
    con.close()
    cur.close()
    cur.__del__()
    context = {'userId': request}
    return JsonResponse({"html": render_to_string("admin panel/useriddiv.html", context)})


@editor_permission('editor')
def displayAllPilots(request):
    if request.user.is_superuser:
        return render(request, 'trash/trash.html')


@editor_permission('editor')
def displayedPilot(request, tvs_id):
    con = fdb.connect(dsn=ip_address, user=name,
                      password=password, charset='WIN1251')  # Подключение к базе данных
    cur = con.cursor()
    query_db = """ select pm.sap_tab, pm.id_pers ,pm.lname,pm.fname,pm.mname,
           ptvs.spec, ptvs.state, ptvs.tvs_id,
            case
             when (ptvs.state)=3 then 'Пилот Инстр.'
             else td.short_name
           end as short_name, sta.short_name, 
           case when pm.podraz_id=4622 then 1 else 0 end as Petersburg,
           wc.dat_beg,wc.dat_end,twcr.name_work,twcr.TWORK_ID
            from stafl_getdown_id_lvl(2, -1) st
            left join pers_main pm on pm.podraz_id=st.id_get and pm.state='Y' and pm.flight='Y'
            left join type_dolgn td on td.id_dolgn=pm.dolgn_id
            left join st_afl sta on sta.id_podraz=pm.podraz_id
            left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ptvs.spec<30
            left join wcrew_crew wc on wc.pers_id = pm.id_pers
            left join wcrew_main wm on wm.id_wcrew = wc.wcrew_id
             LEFT JOIN TYPE_WORKCREW TWCR ON TWCR.ID_TWORK= wm.TWORK_ID
            and ptvs.spec<30 and ptvs.activ=1
            left join list_person_for_programm_ffs_pl lp on lp.pers_id=pm.id_pers
        where pm.state='Y' and pm.flight='Y'
          and ptvs.activ=1
          and (wc.status is null or wc.status<>1)
          and (wc.ttc_id=1 or wc.ttc_id=68 or wc.ttc_id=69
          or  wc.ttc_id=75 or  wc.ttc_id=76)
          and wm.twork_id='ТС'
          and ptvs.tvs_id=?
        UNION
        select pm.sap_tab, pm.id_pers ,pm.lname,pm.fname,pm.mname,
           ptvs.spec, ptvs.state, td.short_name, sta.short_name, ptvs.tvs_id,
           case when pm.podraz_id=4622 then 1 else 0 end as Petersburg,
            wc.dat_beg,wc.dat_end,twcr.name_work,twcr.TWORK_ID
                from list_person_for_programm_ffs_pl list_pers
                left join pers_main pm on pm.id_pers=list_pers.pers_id
                left join wcrew_crew wc on wc.pers_id = pm.id_pers
                left join wcrew_main wm on wm.id_wcrew = wc.wcrew_id
                LEFT JOIN TYPE_WORKCREW TWCR ON TWCR.ID_TWORK= wm.TWORK_ID
                left join type_dolgn td on td.id_dolgn=pm.dolgn_id
                left join st_afl sta on sta.id_podraz=pm.podraz_id
                left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers
                and ptvs.spec<30 and ptvs.activ=1
                where ptvs.spec is not null and ptvs.state is not null
                and twcr.id_twork = 'TC'
    --            and wc.dat_beg between :dat_beg and :dat_end
    --            and wc.dat_beg != :dat_beg
                and ptvs.tvs_id=?
        order by 2 asc, 12 DESC
                                """
    cur.execute(query_db, [tvs_id, tvs_id])
    request = cur.fetchall()
    con.close()
    cur.close()
    cur.__del__()
    old_pers_id = 0
    count = 0
    listAllPilots = []
    while count < len(request):
        new_pers_id = request[count][1]
        if new_pers_id != old_pers_id:
            old_pers_id = new_pers_id
            for i in range(4):
                print(
                    f"{old_pers_id} {request[count][2]} {request[count][3]} "
                    f"{request[count][4]} {request[count][11].strftime('%d.%b.%y %H:%M:%S')}-{request[count][12].strftime('%d.%b.%y %H:%M:%S')}")
                listAllPilots.append(request[count])
                count += 1
        count += 1
    context = {'list': listAllPilots}
    return JsonResponse({"html": render_to_string("trash/trash_output.html", context)})



# def only_watching(request):
#     return render(request, 'only_watch.html')


# def print_sim7000_5000(request, type_aircraft, simulator_number, month_search,
#                        year_search, select_db, twork_id="TC"):  # аргумент list_dat строго по возрастанию
#     con = fdb.connect(dsn=db_selector[select_db], user=name, password=password)
#     # if (request.POST.getlist('arr_sessions_time[]')!=None):
#     #     list_sessions_time=[datetime.datetime.strptime('1.1.2000 '+parse_time,'%d.%m.%Y %H:%M:%S').time() for parse_time in request.POST.getlist('arr_sessions_time[]')]
#     # else:
#     #     list_sessions_time = list_sessions_time
#     # if (request.POST.getlist('arr_technical_time[]')!=None):
#     #     list_technical_time= [datetime.datetime.strptime('1.1.2000 '+parse_time,'%d.%m.%Y %H:%M:%S').time()  for parse_time in request.POST.getlist('arr_technical_time[]')]
#     # else:
#     #     list_technical_time = list_technical_time
#
#     start_apptime = time.time()
#
#     beginning_selected_month = datetime.date(year=year_search, month=month_search, day=1)
#     list_sessions_time.sort()
#     list_technical_time.sort()
#     field_prim = " w.prim"
#     request_month_column_headers = """
#         select distinct substr(""" + ("'0'", field_prim)[simulator_number != "null"] + ",1," + str(
#         len(simulator_number)) + """), stripdate1(w.dat_beg),stripdate1(w.dat_end)
#         from wcrew_main w
#         where w.dat_beg between ? and ?
#         and w.twork_id='""" + twork_id + """'
#         and w.tvs_id=?"""
#     query_parameters = [beginning_selected_month, beginning_selected_month + relativedelta(months=1), type_aircraft]
#     if simulator_number != "null":
#         request_month_column_headers += " and w.prim like '" + simulator_number + '%' + "'"
#     cur = con.cursor()
#     try:
#         cur.execute(request_month_column_headers + "order by 2,3", query_parameters)
#     except Exception as exc:
#         print(
#             "--------------------Ошибка в выборке заголовка(времен) сессий таблицы расписания---------------------------- \n" + str(
#                 exc))
#         response = JsonResponse({"error": "Ошибка в выборке заголовка(времен) сессий таблицы расписания"})
#         response.status_code = 501  # To announce that the user isn't allowed to publish
#         con.close()
#         return response
#     else:
#         month_column_headers = cur.fetchall()
#         print(simulator_number)
#     finally:
#         cur.close()
#         cur.__del__()
#
#     request_crew_in_session = """
#             --           0             1           2            3          4           5           6          7         8
#             select crm.id_wcrew, pm.id_pers, crm.dat_beg, crm.dat_end, ptvs.spec, ptvs.state, pm.f_name, pm.m_name, pm.l_name,
#              --                                               9
#             case when cr.status>1 then null else cr.status end as status,
#              --    10          11        12         13
#             td.short_name, tks.color, tks.descr, tit.color,
#              --                                                  14           15           16         17               18             19          20
#             case when pm.podraz_id=4622 then 1 else 0 end as Petersburg, tks.id_ttc, cr.comm_aim, cr.ttc_id,list(tp.short_name), cr.user_add, cr.dat_ins
#             from wcrew_main crm
#             left join wcrew_crew cr on cr.wcrew_id=crm.id_wcrew
#             left join pers_main pm on cr.pers_id=pm.id_pers
#             left join pers_tvs ptvs on ptvs.pers_id = pm.id_pers and ((ptvs.spec<30 and pm.flight='Y') or (ptvs.spec=80 and pm.flight='N')) and ptvs.tvs_id = ? and ptvs.activ=1
#             left join type_dolgn td on td.id_dolgn=pm.dolgn_id
#             left join st_afl sta on sta.id_podraz=pm.podraz_id
#             left join type_ktc_sesn as tks on crm.ttc_id=tks.id_ttc
#             left join pers_instr_trng pit on pit.pers_id=cr.pers_id and pit.tvs_id=?
#             left join type_instr_trng tit on tit.id_grp = pit.grp_instr
#             left join rezerv_ppls rp on rp.wcrew_id=crm.id_wcrew and rp.pers_id=pm.id_pers
#             left join type_ppls tp on tp.id_ppls=rp.ppls_id
#             where
#               pm.state='Y'
#               and crm.dat_beg between ? and ?
#               and crm.twork_id = '""" + twork_id + """'
#               and crm.tvs_id = ?
#               --and ((ptvs.spec<30 and pm.flight='Y')
#               --                                or
#               --      (ptvs.spec=80 and pm.flight='N'))
#
#         """
#     query_parameters = [type_aircraft, type_aircraft, beginning_selected_month,
#                         beginning_selected_month + relativedelta(months=1), type_aircraft]
#     if simulator_number != "null":
#         request_crew_in_session += " and crm.prim like '" + simulator_number + '%' + "'"
#     cur2 = con.cursor()
#     try:
#         cur2.execute(request_crew_in_session +
#                      "group by crm.id_wcrew, pm.id_pers, crm.dat_beg, crm.dat_end, ptvs.spec, ptvs.state, pm.f_name, pm.m_name, pm.l_name,"
#                      "cr.status, td.short_name, tks.color, tks.descr, tit.color, Petersburg, tks.id_ttc, cr.comm_aim, cr.ttc_id, cr.user_add, cr.dat_ins "
#                      "order by 3,4,10 desc,6 desc,5", query_parameters)
#     except Exception as exc:
#         print(
#             "--------------------Ошибка в основном запросе на формирование таблицы расписания---------------------------- \n" + str(
#                 exc))
#         response = JsonResponse({"error": "Ошибка в основном запросе на формирование таблицы расписания"})
#         response.status_code = 501  # To announce that the user isn't allowed to publish
#         con.close()
#         return response
#     else:
#         simulator_schedule = cur2.fetchall()
#     finally:
#         cur2.close()
#         cur2.__del__()
#     request_empty_in_session = """
#             --    0          1          2           3           4           5
#     select wm.id_wcrew, wm.dat_beg, wm.dat_end, tks.color, tks.descr , wm.ttc_id from wcrew_main wm
#     left join type_ktc_sesn as tks on wm.ttc_id=tks.id_ttc
#     where wm.dat_beg between ? and ? and wm.tvs_id=?  and wm.twork_id = '""" + twork_id + """'
#     """
#     query_parameters = [beginning_selected_month, beginning_selected_month + relativedelta(months=1), type_aircraft]
#     if simulator_number != "null":
#         query_parameters.append(simulator_number)
#         request_empty_in_session += " and wm.prim like '" + simulator_number + '%' + "'"
#     cur3 = con.cursor()
#     try:
#         cur3.execute(request_empty_in_session + "order by 2", query_parameters)
#     except Exception as exc:
#         print("--------------------Ошибка в выборке пустых сессий---------------------------- \n" + str(exc))
#         response = JsonResponse({"error": "Ошибка в выборке пустых сессий"})
#         response.status_code = 501  # To announce that the user isn't allowed to publish
#         con.close()
#         return response
#     else:
#         id_session_wcrew = cur3.fetchall()
#     finally:
#         cur3.close()
#         cur3.__del__()  # 0      1
#     List_sim_schedule = [[[["none", "None",
#                             #                                  2
#                             month_column_headers[i][1].replace(day=j + 1, month=month_search, year=year_search),
#                             #                                  3
#                             month_column_headers[i][2].replace(day=j + 1, month=month_search,
#                                                                year=year_search) + relativedelta(
#                                 days=(1, 0)[month_column_headers[i][1].time() < month_column_headers[i][2].time()]),
#                             #  4     5     6  7    8     9  10  11  12  13  14    15
#                             "None", "None", "", '', 'None', '', '', '', '', '', '', 'None']] for i in
#                           range(len(month_column_headers))] for j in
#                          range(calendar.monthrange(year_search, month_search)[1])]
#     for i in range(len(List_sim_schedule)):
#         for j in range(len(List_sim_schedule[i])):
#             for k in range(len(id_session_wcrew)):
#                 if List_sim_schedule[i][j][0][2] == id_session_wcrew[k][1] and List_sim_schedule[i][j][0][3] == \
#                         id_session_wcrew[k][2]:
#                     List_sim_schedule[i][j][0][0] = id_session_wcrew[k][0]
#                     List_sim_schedule[i][j][0][11] = id_session_wcrew[k][3]
#                     List_sim_schedule[i][j][0][12] = id_session_wcrew[k][4]
#                     List_sim_schedule[i][j][0][15] = id_session_wcrew[k][5]
#     if len(simulator_schedule) == 0:
#         response = JsonResponse({"html": render_to_string("schedule_table.html",
#                                                           {
#                                                               'working_trainers': List_sim_schedule,
#                                                               'month_column_headers': month_column_headers,
#                                                               'count_day': days(month_search,
#                                                                                 year_search),
#                                                               'days_off': output_of_days_off(month_search,
#                                                                                              year_search)
#                                                           }),
#                                  "db_info": con.db_info(fdb.isc_info_db_id)})
#         con.close()
#         return response
#     index_select_people = 0
#     select_session = 0
#     for select_day in range(len(List_sim_schedule)):
#         select_session = 0
#         while select_session < len(List_sim_schedule[select_day]):
#             if index_select_people >= len(simulator_schedule):
#                 break
#             while List_sim_schedule[select_day][select_session][0][2] == simulator_schedule[index_select_people][2] and \
#                     List_sim_schedule[select_day][select_session][0][3] == simulator_schedule[index_select_people][3]:
#                 if List_sim_schedule[select_day][select_session][0][1] == "None":
#                     List_sim_schedule[select_day][select_session][0] = simulator_schedule[index_select_people]
#                 else:
#                     List_sim_schedule[select_day][select_session].append(simulator_schedule[index_select_people])
#                 index_select_people += 1
#                 if index_select_people >= len(simulator_schedule):
#                     break
#             select_session += 1
#
#     # mass_sission_sim_schedule = []
#     # people_in_day=[]
#     # tmp_time = simulator_schedule[0][2].time()
#     # for sim_shed in simulator_schedule:
#     #     if sim_shed[2].time() == tmp_time:
#     #         people_in_day.append(sim_shed)
#     #     else:
#     #         tmp_time=sim_shed[2].time()
#     #         mass_sission_sim_schedule.append(people_in_day)
#     #         people_in_day=[]
#     #         people_in_day.append(sim_shed)
#     # mass_day_sim_schedule=[]
#     # tmp_mass_day=[]
#     # tmp_day = simulator_schedule[0][2].day
#     # for mass_sim in mass_sission_sim_schedule:
#     #     if mass_sim[0][2].day == tmp_day:
#     #         tmp_mass_day.append(mass_sim)
#     #     else:
#     #         tmp_day=mass_sim[0][2].day
#     #         mass_day_sim_schedule.append(tmp_mass_day)
#     #         tmp_mass_day=[]
#     #         tmp_mass_day.append(mass_sim)
#     # for m in mass_day_sim_schedule:
#     #     print(m)
#     #     print("---------------------------------Test")
#     # for i in range(len(List_sim_schedule)):
#     #     if i+1>len(mass_day_sim_schedule):
#     #         break
#     #     for List_sim in range(len(List_sim_schedule[i])) :
#     #         for mass_day in range(len( mass_day_sim_schedule[i])):
#     #             if List_sim_schedule[i][List_sim][0][2]==mass_day_sim_schedule[i][mass_day][0][2]:
#     #                 List_sim_schedule[i][List_sim]=mass_day_sim_schedule[i][mass_day]
#
#     """if len(simulator_schedule[0])>=3 and isinstance(simulator_schedule[0][2], datetime.datetime):
#         tmp_day =  simulator_schedule[0][2].day
#         tmp_time = simulator_schedule[0][2].time()
#     else:
#         tmp_day = 0
#         tmp_time = 0"""
#
#     """if i != len(simulator_schedule)-1 and simulator_schedule[i][2].day == tmp_day :
#         if  simulator_schedule[i][2].time() == tmp_time:
#             people_in_day.append(simulator_schedule[i])
#         else:
#             if len(people_in_day)<4:
#                 people_in_day.extend([['None']*10]*(4-len(people_in_day)))
#             mass_day_sim_schedule.append(people_in_day)
#             people_in_day=[]
#             tmp_time = simulator_schedule[i][2].time()
#             people_in_day.append(simulator_schedule[i])
#     else:
#         if len(people_in_day) < 4:
#             people_in_day.extend([['None'] * 10] * (4 - len(people_in_day)))
#         mass_day_sim_schedule.append(people_in_day)
#         if len(mass_day_sim_schedule)<len(list_sessions_time):
#             mass_day_sim_schedule.extend([[['None']*10]*4]* (len(list_sessions_time)-len(mass_day_sim_schedule)))
#         for j in range(len(list_sessions_time)):
#             tmp_day_time=datetime.datetime.combine(datetime.date(year=year_search, month=month_search, day=tmp_day),list_sessions_time[j])
#             if len(mass_day_sim_schedule[j][0]) == 0:
#                 mass_day_sim_schedule[j][0].extend(['None']*10)
#                 mass_day_sim_schedule[j][0][2]=tmp_day_time
#             if not isinstance(mass_day_sim_schedule[j][0][2], datetime.datetime):
#                 mass_day_sim_schedule[j][0][2] = tmp_day_time
#             if list_sessions_time[j] != mass_day_sim_schedule[j][0][2].time():
#                 for mass_d in range(len(mass_day_sim_schedule)):
#                     if len(mass_day_sim_schedule[mass_d][0]) != 0 and isinstance(mass_day_sim_schedule[mass_d][0][2], datetime.datetime) \
#                             and mass_day_sim_schedule[mass_d][0][2].time() ==list_sessions_time[j]:
#                         tmp_mass_d=mass_day_sim_schedule[mass_d]
#                         mass_day_sim_schedule[mass_d] = mass_day_sim_schedule[j]
#                         mass_day_sim_schedule[j]=tmp_mass_d
#                         #print("HERE")
#         #print("_______________-")
#         List_sim_schedule.append(mass_day_sim_schedule)
#         people_in_day=[]
#         people_in_day.append(simulator_schedule[i])
#         mass_day_sim_schedule = []
#         tmp_day = simulator_schedule[i][2].day
#         tmp_time = simulator_schedule[i][2].time()"""
#     response = JsonResponse({"html": render_to_string("schedule_table.html", {'working_trainers': List_sim_schedule,
#                                                                               'month_column_headers': month_column_headers,
#                                                                               'count_day': days(month_search,
#                                                                                                 year_search),
#                                                                               'days_off': output_of_days_off(
#                                                                                   month_search,
#                                                                                   year_search)
#                                                                               }),
#                              "db_info": con.db_info(fdb.isc_info_db_id)})
#     cache.clear()
#     print('cache is clear!')
#     print("print_sim7000_5000 --- %s seconds ---" % (time.time() - start_apptime))
#     con.close()
#     return response

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


# def update_or_create_KRS(request):
#     query = """select  pm.sap_tab, pm.fio,td.dolgn, d.full_name
#             from st_afl d
#             left join PERS_MAIN pm on pm.podraz_id=d.id_podraz
#             left join type_dolgn td on td.id_dolgn=pm.dolgn_id
#             left join PERS_TVS vs on vs.pers_id=pm.id_pers
#             where d.id_parent=4103
#             and d.type_podraz=2
#             and pm.state='Y' and pm.flight='Y'
#             and vs.state=3
#             and vs.activ=1
#             and vs.tvs_id=?"""
#     cur = con.cursor()
#     cur.execute(query, [type_aircraft])
#     entry_instructor = cur.fetchall()
#     for ent in entry_instructor:
#         KRS_according_staff_schedule.objects.update_or_create(SAP_TAB=ent[0], FULL_NAME=ent[1], DOLGN=ent[2],
#                                                               PODRAZ=ent[3])
#     return HttpResponse(json.dumps(list_db))


# def update_or_create_KRS_LIS_air_squadrons(request):
#     query = """ select pm.sap_tab, pm.fio, td.dolgn, s.full_name
#             from stafl_getdown_id_lvl(2,-1) d
#             left join st_afl s on s.id_podraz=d.id_get
#                         and (s.type_podraz=3 or s.id_podraz=4622)
#             left join PERS_MAIN pm on pm.podraz_id=d.id_get
#             left join type_dolgn td on td.id_dolgn=pm.dolgn_id
#             left join PERS_TVS vs on vs.pers_id=pm.id_pers
#             where (s.type_podraz=3 or s.id_podraz=4622)
#             and pm.state='Y' and pm.flight='Y'
#             and vs.state=3
#             and vs.activ=1
#             and td.dolgn<>'Командир воздушного судна'
#             and vs.tvs_id=?"""
#     cur = con.cursor()
#     cur.execute(query, [type_aircraft])
#     entry_instructor = cur.fetchall()
#     for ent in entry_instructor:
#         KRS_LIS_air_squadrons_according_staffing_table.objects.update_or_create(SAP_TAB=ent[0], FULL_NAME=ent[1],
#                                                                                 DOLGN=ent[2], PODRAZ=ent[3])
#     return HttpResponse(json.dumps(list_db))


# def update_or_create_freelance_instructor_CHECK(request):
#     query = """ select  pm.sap_tab, pm.fio, td.short_name,s.full_name, dpp.dat_end as DAT_PROV,dpt.dat_end as DAT_TREN
#             from stafl_getdown_id_lvl(4103,-1) d
#             left join st_afl s on s.id_podraz=d.id_get
#             left join PERS_MAIN pm on pm.podraz_id=d.id_get
#             left join type_dolgn td on td.id_dolgn=pm.dolgn_id
#             left join PERS_TVS vs on vs.pers_id=pm.id_pers
#             left join DATE_PERSEND_CHECKPARAM dpp on dpp.pers_id=pm.id_pers
#                                           and dpp.tvs_id=vs.tvs_id
#                                           and dpp.spec_id=10
#                                           and dpp.param_id=27
#             left join DATE_PERSEND_CHECKPARAM dpt on dpt.pers_id=pm.id_pers
#                                           and dpt.tvs_id=vs.tvs_id
#                                           and dpt.spec_id=10
#                                           and dpt.param_id=31
#             where pm.state='Y' and pm.flight='Y'
#             and vs.state=3
#             and vs.activ=1
#             and td.dolgn='Командир воздушного судна'
#             and vs.tvs_id=?
#             and dpp.dat_end>'today'
#             and dpt.dat_end>'today'"""
#       cur = con.cursor()
#     cur.execute(query, [type_aircraft])
#     entry_instructor = cur.fetchall()
#     print(entry_instructor)
#     for ent in entry_instructor:
#         freelance_instructor_pilots_check.objects.update_or_create(SAP_TAB=ent[0], FULL_NAME=ent[1], DOLGN=ent[2],
#                                                                    PODRAZ=ent[3], DAT_PROV=ent[4], DAT_TREN=ent[5])
#
#     return HttpResponse(json.dumps(list_db))

#
# def update_or_create_freelance_instructor(request):
#     query = """ select  pm.sap_tab, pm.fio,td.short_name, s.full_name, dpp.dat_end as DAT_PROV,dpt.dat_end as DAT_TREN
#             from stafl_getdown_id_lvl(4103,-1) d
#             left join st_afl s on s.id_podraz=d.id_get
#             left join PERS_MAIN pm on pm.podraz_id=d.id_get
#             left join type_dolgn td on td.id_dolgn=pm.dolgn_id
#             left join PERS_TVS vs on vs.pers_id=pm.id_pers
#             left join DATE_PERSEND_CHECKPARAM dpp on dpp.pers_id=pm.id_pers
#                                           and dpp.tvs_id=vs.tvs_id
#                                           and dpp.spec_id=10
#                                           and dpp.param_id=27
#             left join DATE_PERSEND_CHECKPARAM dpt on dpt.pers_id=pm.id_pers
#                                           and dpt.tvs_id=vs.tvs_id
#                                           and dpt.spec_id=10
#                                           and dpt.param_id=31
#             where pm.state='Y' and pm.flight='Y'
#             and vs.state=3
#             and vs.activ=1
#             and td.dolgn='Командир воздушного судна'
#             and vs.tvs_id=?
#             and (dpp.dat_end is null or dpp.dat_end<'today')
#             and dpt.dat_end>'today'"""
#     cur = con.cursor()
#     cur.execute(query, [type_aircraft])
#     entry_instructor = cur.fetchall()
#     for ent in entry_instructor:
#         freelance_instructor_pilots.objects.update_or_create(SAP_TAB=ent[0], FULL_NAME=ent[1], DOLGN=ent[2],
#                                                              PODRAZ=ent[3], DAT_PROV=ent[4], DAT_TREN=ent[5])
#     return HttpResponse(json.dumps(list_db))
#
#
# class InstructorsList(generics.ListAPIView):
#     queryset = Instructors.objects.all()
#     serializer_class = serializers.InstructorSerializer
#
#
# class KRSList(generics.ListAPIView):
#     queryset = KRS_according_staff_schedule.objects.all()
#     serializer_class = serializers.KRSSerializer
#
#
# class KRS_and_LISList(generics.ListAPIView):
#     queryset = KRS_LIS_air_squadrons_according_staffing_table.objects.all()
#     serializer_class = serializers.KRSandLISSerializer
#
#
# class freelance_pilots_CHECKList(generics.ListAPIView):
#     queryset = freelance_instructor_pilots_check.objects.all()
#     serializer_class = serializers.FreelansePilots_CheckSerializer
#
#
# class freelance_pilotsList(generics.ListAPIView):
#     queryset = freelance_instructor_pilots.objects.all()
#     serializer_class = serializers.FreelansePilots_Serializer


# EXCEL ///////////////////////////////////////////////

# def excel_table(request):
#     source = urllib.request.urlopen('http://127.0.0.1:8000').read()
#     soup = BeautifulSoup(source,'html.parser')
#     headers = {}
#     rows = soup.find_all("tr")
#     thead = soup.find("thead").find_all("th")
#
#     for i in range(len(thead)):
#         headers[i] = thead[i].text.strip().lower()
#
#     data = []
#
#     for row in rows:
#         cells = row.find_all("td")
#
#     item = {}
#
#     for index in headers:
#         item[headers[index]] = cells[index].text
#         data.append(item)
#
#     print(data)
