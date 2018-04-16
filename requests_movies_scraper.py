from collections import defaultdict
import datetime
import itertools
import json
import requests
from operator import itemgetter

NI = 1
HN = 2
SV = 3
GT = 4
CR = 5


COUNTRY_CONFIG = {
    SV: {
        'url':'http://www.cinepolis.com.sv/Cartelera.aspx/GetNowPlayingByCity',
        'data':[
            {"claveCiudad":"san-salvador-el-salvador","esVIP":False},
            {"claveCiudad":"santa-ana-el-salvador","esVIP":False}
        ]
    },
    HN: {
        'url':'http://www.cinepolis.com.hn/Cartelera.aspx/GetNowPlayingByCity',
        'data': [
            {"claveCiudad":"tegucigalpa-honduras","esVIP":False},
        ]
    },
    GT: {
        'url':'http://www.cinepolis.com.gt/Cartelera.aspx/GetNowPlayingByCity',
        'data':[
            {"claveCiudad":"guatemala-guatemala","esVIP":False},
        ]
    }

}

HEADERS = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'keep-alive',
    'DNT': '1'
}


def get_schedules(country_id):
    import locale
    locale.setlocale(locale.LC_ALL,"es_NI.UTF-8")
    config = COUNTRY_CONFIG[country_id]

    out = []

    for params in config['data']:
        r = requests.post(
            config['url'],
            headers=HEADERS,
            data=json.dumps(params)
            )
        r_json = json.loads(r.content, encoding='utf-8')
        data = r_json['d']

        for sala in data['Cinemas']:
            # print "***********************"
            # print sala['Id'], "-", sala["Name"]
            row = {}
            row['sala_id'] = sala['Id']
            row['sala'] = sala['Name']
            # 7 dias, de jueves a Miercoles
            for dia in sala['Dates']:
                date_str = dia['ShowtimeDate'] + ' ' + str(datetime.date.today().year)
                date = datetime.datetime.strptime(date_str,"%d %B %Y").date()
                # print ">>>", date
                row['date'] = date
                for peli in dia['Movies']:
                    # print "####",peli['Id'], "-", peli["Title"]
                    row['pelicula_id'] = peli['Id']
                    row['pelicula'] = peli['Title']
                    row['rate'] = ": ".join([
                        peli.get('Rating') or '',
                        peli.get('RatingDescription') or ''
                    ])

                    print peli
                    for horario in peli['Formats']:
                        language = horario['Language'].title()
                        row['format'] = " ".join(horario["Name"].split()[:-1]) + " " + language
                        for h in horario['Showtimes']:
                        # print "********", horario['VistaId'], "-", horario["Language"]
                            row['time'] = h["ShowtimeAMPM"].lower()
                            out.append(dict(row))
    return out


def get_grouped_data(data, keys, aggregate_fn, result_key):
    grouper = itemgetter(*keys)
    result = []
    #obteniendo tipo de horario
    result = []
    for key, grp in itertools.groupby(sorted(data, key = grouper), grouper):
        temp_dict = dict(zip(keys, key))
        temp_dict[result_key] = aggregate_fn(grp)
        result.append(temp_dict)
    return result


def get_grouped_schedules(grp):
    schedules = defaultdict(list)
    sort_by = itemgetter('schedule_type')
    for schedule_type, schedule_type_values in itertools.groupby(sorted(grp, key=sort_by), sort_by ):
        format_sort_by = itemgetter('format')
        for f, times in itertools.groupby(sorted(schedule_type_values, key=format_sort_by), format_sort_by):
            schedules[schedule_type].append((f, [t['time'] for t in times]))
    return schedules


def get_movies_schedules(country_id, date_range=None):
    if country_id not in COUNTRY_CONFIG.keys():
        return []
    data = get_schedules(country_id)
    keys = ["sala_id","sala","pelicula_id","pelicula","rate","format","time"]
    result_key= "schedule_type"
    aggregate_fn = lambda grp: get_schedule_type([item["date"] for item in grp], date_range)
    data = get_grouped_data(data, keys, aggregate_fn, result_key)


    #obteniendo horarios agrupados por tipo y formato
    keys = ["sala_id","sala","pelicula_id","pelicula","rate"]
    result_key= "horarios"
    aggregate_fn = get_grouped_schedules
    data = get_grouped_data(data, keys, aggregate_fn, result_key)
    return data


def get_schedule_type(date_array, date_range=None):
    sorted_dates = sorted(date_array)
    start_date, end_date = date_range
    sorted_dates = [ d for d in sorted_dates if d >= start_date and d <= end_date]
    week_days = sorted([ d.isoweekday() for d in sorted_dates])

    all_week = range(1,8)
    weekend = [6, 7]
    long_weekend = [4,5,6, 7]
    if week_days == all_week:
        return u"Todos los días"
    elif week_days == weekend:
        return "Fin de Semana"
    elif week_days == long_weekend:
        return "Jueves a Domnigo"
    else:
        import locale
        locale.setlocale(locale.LC_ALL,"es_NI.UTF-8")
        result = ", ".join([d.strftime("%A").decode("utf-8") for d in sorted_dates])
        return result.title()
