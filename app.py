import logging

import pandas as pd
import plotly.express as px
import streamlit as st

logging.getLogger("streamlit-bikila").setLevel(logging.DEBUG)

# -- Set page config
st.set_page_config(
    page_title="BiDD",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.bikila.de/',
        'Report a bug': "https://www.bikila.de/",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)


# -- SQL Connection
@st.cache_resource
def get_sql_connection():
    return st.connection("bikila-test", type="sql")


@st.cache_data
def get_events(_conn, sportsid=''):
    if not sportsid:
        events_sql = ("SELECT T1.von, T2.bez FROM event T1 INNER JOIN thesaur T2 ON T1.art = T2.nr AND T2.kategorie = \'wkart\' "
                      "WHERE T1.del =\'N\' ORDER BY T1.von")
        events_sql_df = conn.query(events_sql, ttl=600)
    else:
        events_sql = ("SELECT T1.von, T2.bez FROM event T1 INNER JOIN thesaur T2 ON T1.art = T2.nr AND T2.kategorie = \'wkart\' "
                      "WHERE T1.del =\'N\' AND T1.sportartid = :sportsid ORDER BY T1.von")
        events_sql_df = conn.query(events_sql, ttl=600, params={"sportsid": sportsid})
    #else:
    #    events_sql = ("SELECT T1.* FROM event T1 INNER JOIN thesaur T2 ON T1.art = T2.nr "
    #                  "WHERE T1.del =\'N\' AND YEAR(T1.von) = :event_date ORDER BY T1.von ASC")
    #    events_sql_df = conn.query(events_sql, ttl=600, params={"event_date": event_date})
    return events_sql_df


@st.cache_data
def get_athletes(_conn):
    athletes_sql = "SELECT T1.name FROM sp T1 WHERE T1.del =\'N\'"
    athletes_sql_df = conn.query(athletes_sql, ttl=600)
    return athletes_sql_df


@st.cache_data
def get_sports(_conn):
    sports_sql = "SELECT T1.id, T1.bez FROM sportart T1 WHERE T1.del =\'N\' ORDER BY T1.bez"
    sports_sql_df = conn.query(sports_sql, ttl=600)
    return sports_sql_df


@st.cache_data
def get_disciplines_by_sportsid(_conn, sportsid):
    logging.error(sportsid)
    disciplines_sql = "SELECT T1.disziplin FROM disz T1 WHERE T1.del =\'N\' AND T1.sportartid = :sportsid"
    logging.error(f"SQL String: {disciplines_sql}")
    disciplines_sql_df = _conn.query(disciplines_sql, ttl=600, params={"sportsid": sportsid})
    return disciplines_sql_df


def get_teams(_conn):
    athletes_sql = "SELECT name FROM sp T1 WHERE T1.del =\'N\'"
    athletes_sql_df = conn.query(athletes_sql, ttl=600)
    return athletes_sql_df


@st.cache_data
def get_countries(_conn):
    countries_sql = "SELECT bez FROM land T1 WHERE T1.del =\'N\'"
    countries_sql_df = conn.query(countries_sql, ttl=600)
    return countries_sql_df


@st.cache_data
def get_athlete(_conn, athlete):
    athlete_sql = (
        "SELECT T1.* FROM ("
        "(SELECT YEAR(event.von) AS jahr, sp.name, spwk.spid, NULL AS teamspid,"
        "IF(spwk.platz<4, 'Medaille - Einzel', IF(spwk.platz<9, 'Finale - Einzel', 'Teilnahme - Einzel')) AS platz, "
        "NULLIF(event.akl, '') AS akl, thesaur.bez AS wkart, TIMESTAMPDIFF(YEAR, sp.geb, event.von) AS wkalter "
        "FROM spwk "
        "LEFT JOIN wk ON (spwk.wkid = wk.id) "
        "LEFT JOIN sp ON (spwk.spid = sp.id) "
        "LEFT JOIN event ON (wk.eventid = event.id) "
        "LEFT JOIN land ON (spwk.landid = land.id) "
        "INNER JOIN thesaur ON (event.art = thesaur.nr AND thesaur.kategorie = \'wkart\') "
        "WHERE spwk.del = \'N\' AND NOT ISNULL(spwk.spid) AND sp.name = :athlete "
        ") UNION ("
        "SELECT YEAR(event.von) AS jahr, sp.name, spwk.spid, team.spid AS teamspid, "
        "IF(spwk.platz<4, 'Medaille - Team', IF(spwk.platz<9, 'Finale - Team', 'Teilnahme - Team')) AS platz, "
        "NULLIF(event.akl, '') AS akl, thesaur.bez AS wkart, TIMESTAMPDIFF(YEAR, sp.geb, event.von) AS wkalter "
        "FROM spwk "
        "LEFT JOIN wk ON (spwk.wkid = wk.id) "
        "LEFT JOIN event ON (wk.eventid = event.id) "
        "LEFT JOIN team ON (team.spwkid = spwk.id AND team.del = \'N\') "
        "LEFT JOIN sp ON (team.spid = sp.id) "
        "LEFT JOIN land ON (spwk.landid = land.id) "
        "INNER JOIN thesaur ON (event.art = thesaur.nr AND thesaur.kategorie = \'wkart\') "
        "WHERE spwk.del = \'N\' AND ISNULL(spwk.spid) AND sp.name = :athlete)) AS T1 "
        "ORDER BY T1.jahr"
    )
    logging.info(f"SQL String: {athlete_sql}")
    athlete_sql_df = conn.query(athlete_sql, ttl=600, params={"athlete": athlete})
    return athlete_sql_df


# -- Get all events
conn = get_sql_connection()
events = get_events(conn)
# -- Get all athletes
athletes = get_athletes(conn)
# -- Get all teams
teams = get_teams(conn)

# -- Logo in sidebar
st.sidebar.image('https://bikila.de/img/Logo_BIKILA-RGB-negativ.png')
st.sidebar.markdown(f"""
 Willkommen bei Bikila Data Dive (BiDD). 
 Es sind aktuell {len(events)} Events, {len(athletes)} Athleten, {len(teams)} Teams
 um Erkenntnisse zu gewinnen. 
""")

main_options = ['individual', 'team']
main_options_selected = st.sidebar.selectbox("Wählen Sie eine der Optionen", main_options)

match main_options_selected:
    case 'individual':
        # https://github.com/m-wrzr/streamlit-searchbox/blob/main/example.py
        # -- Set an Athlete :
        selected_athlete = st.sidebar.multiselect(
            'Name',
            athletes['name'],
            placeholder='Bikila, Abebe',
            max_selections=5
        )

        if selected_athlete:
            # athlete_df = get_athlete('Roest, Patrick')
            # athlete_df = get_athlete("Wellbrock, Florian")
            athlete_df = get_athlete(conn, selected_athlete)

            # -- Suppose missing age group is 'Senior'
            athlete_df['akl'] = athlete_df['akl'].fillna('Senioren')
            # -- Concat event type wih age groups
            athlete_df['wkart'] = athlete_df['wkart'].astype(str) + ' - ' + athlete_df['akl']
            # -- check if athlete age is known
            if not athlete_df['wkalter'].isna().all():
                athlete_df_wkalter_min = athlete_df['wkalter'].unique().min()
                athlete_df_wkalter_max = athlete_df['wkalter'].unique().max()
                athlete_df_wkalter = st.sidebar.slider("Alter", athlete_df_wkalter_min, athlete_df_wkalter_max,
                                                       (athlete_df_wkalter_min, athlete_df_wkalter_max))
                selected_min, selected_max = athlete_df_wkalter
                athlete_df = athlete_df.loc[
                    (athlete_df['wkalter'] >= selected_min) & (athlete_df['wkalter'] <= selected_max)]
            else:
                st.sidebar.divider()
                st.sidebar.markdown(f":orange[Für {''.join(selected_athlete)} ist kein Geburtstag hinterlegt.]")

            # -- Boxplot mit Plotly Express erstellen
            fig = px.box(athlete_df, x="jahr", y='wkart', color='platz', points='all',
                         labels={"platz": "Platzierungen"})
            fig.update_xaxes(title='Jahr')
            fig.update_yaxes(title='Platzierungen')

            st.subheader("Wettkampferfolge")
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

            with st.expander("Rohadaten"):
                st.markdown('Die Rohdaten für die Abbildung oben.')
                st.dataframe(athlete_df)

        else:
            st.info('Please select an athlete from the sidebar menu')

    case 'team':
        sports_df = get_sports(conn)
        selected_sports = st.sidebar.selectbox(
            "Wähle eine Sportart",
            sports_df['bez'].dropna().unique()
        )
        selected_sportsid = sports_df.loc[sports_df['bez'] == selected_sports]['id'].iloc[0]

        disciplines_df = get_disciplines_by_sportsid(conn, selected_sportsid)
        selected_discipline = st.sidebar.selectbox(
            "Wähle eine Disziplin",
            disciplines_df['disziplin'].dropna().unique()
        )
        st.dataframe(disciplines_df)

        events_df = get_events(conn, selected_sportsid)
        st.dataframe(events_df)

        #events_year = pd.to_datetime(events['von'].dropna(), errors='coerce').dt.strftime('%Y')
        # -- Set a Year :
        #selected_year = st.sidebar.selectbox(
        #    'Wähle ein Jahr',
        #    events_year.unique()
        #)

        #if selected_year:
        #    selected_events = get_events(conn, selected_year)
        #    st.write(selected_events)
        #    st.sidebar.selectbox(
        #        'Wähle ein Event',
        #        selected_events['bem']
        #    )
        #else:
        #    st.info('Please select a year from the sidebar menu')
