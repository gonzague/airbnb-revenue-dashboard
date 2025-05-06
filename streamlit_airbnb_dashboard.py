import streamlit as st
import pandas as pd
import os

# Ensure page config is first Streamlit call
st.set_page_config(page_title="Airbnb Revenue Dashboard", layout="wide")

# --- Configuration & Localization ---
LOCALIZATION = {
    'en': {
        'title': "Airbnb Revenue Dashboard",
        'uploader': "Choose Airbnb export CSV",
        'duplicates': "Potential Duplicates",
        'no_duplicates': "No duplicates.",
        'new_bookings': "New Bookings Added",
        'added_count': "Added {count} new bookings.",
        'no_new': "No new bookings to add.",
        'kpi_header': "Key Metrics & Visualizations",
        'total_rev': "Total Gross Revenue",
        'monthly_rev': "Monthly Gross Revenue",
        'monthly_nights': "Monthly Occupancy Nights",
        'avg_nights': "Average Nights per Booking (Monthly)",
        'lead_dist': "Lead Time Distribution (%)",
        'recent_bookings': "Recent Bookings Preview",
        'missing_cols': "Missing expected columns: {cols}. Please check your export headers.",
        'reservation_date': "Reservation Date",
        'arrival': 'Arrival Date',
        'departure': 'Departure Date',
        'confirmation_code': 'Confirmation Code'
    },
    'fr': {
        'title': "Tableau de Bord Revenu Airbnb",
        'uploader': "Choisissez le fichier CSV d'export Airbnb",
        'duplicates': "Doublons potentiels",
        'no_duplicates': "Aucun doublon.",
        'new_bookings': "Nouvelles Réservations Ajoutées",
        'added_count': "{count} nouvelles réservations ajoutées.",
        'no_new': "Aucune nouvelle réservation à ajouter.",
        'kpi_header': "Principaux indicateurs & visualisations",
        'total_rev': "Revenu Brut Total",
        'monthly_rev': "Revenu Brut Mensuel",
        'monthly_nights': "Nuits Occupées Mensuelles",
        'avg_nights': "Nuits Moyennes par Réservation (Mensuel)",
        'lead_dist': "Distribution du Délai de Réservation (%)",
        'cleaning_sched': "Arrivées & Départs à Venir",
        'recent_bookings': "Aperçu des Réservations Récentes",
        'missing_cols': "Colonnes manquantes: {cols}. Veuillez vérifier vos en-têtes.",
        'reservation_date': "Date de réservation",
        'arrival': 'Date de début',
        'departure': 'Date de fin',
        'confirmation_code': 'Code de confirmation'
    }
}

# Sidebar language selector
lang = st.sidebar.selectbox(
    "Language / Langue",
    ['en', 'fr'],
    format_func=lambda x: 'English' if x == 'en' else 'Français'
)
L = LOCALIZATION[lang]

# App title
st.title(L['title'])

# Path to master dataset
MASTER_PATH = "airbnb_master.csv"

# Column header variants for normalization
COLUMN_VARIANTS = {
    'Date de réservation': ['Date de réservation', 'Booking date', 'Reservation Date', 'Date Réservation'],
    'Date de début': ['Date de début', 'Start date', 'Arrival Date', 'Check-in Date', 'Date début'],
    'Date de fin': ['Date de fin', 'End date', 'Departure Date', 'Check-out Date', 'Date fin'],
    'Revenus bruts': ['Revenus bruts', 'Gross earnings', 'Gross Revenue', 'Revenue', 'Revenus'],
    'Code de confirmation': ['Code de confirmation', 'Confirmation Code', 'Booking ID', 'Reservation Code', 'Reference code']
}

# Normalize headers (case-insensitive)
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    lower_map = {col.lower(): col for col in df.columns}
    rename_map = {}
    for canonical, variants in COLUMN_VARIANTS.items():
        for variant in variants:
            if variant.lower() in lower_map:
                rename_map[lower_map[variant.lower()]] = canonical
                break
    return df.rename(columns=rename_map)

# Load existing master dataset if present
if os.path.exists(MASTER_PATH):
    master_df = pd.read_csv(MASTER_PATH)
    master_df = normalize_columns(master_df)
else:
    master_df = pd.DataFrame()

# File uploader UI
uploaded = st.file_uploader(L['uploader'], type=["csv"])

if uploaded:
    raw = pd.read_csv(uploaded)
    df_new = normalize_columns(raw)

    # Verify required columns
    required = list(COLUMN_VARIANTS.keys())
    missing = [col for col in required if col not in df_new.columns]
    if missing:
        st.error(L['missing_cols'].format(cols=", ".join(missing)))
    else:
        # Parse dates and numeric
        df_new['Date de réservation'] = pd.to_datetime(df_new['Date de réservation'], dayfirst=False)
        df_new['Date de début'] = pd.to_datetime(df_new['Date de début'], dayfirst=False)
        df_new['Date de fin'] = pd.to_datetime(df_new['Date de fin'], dayfirst=False)
        df_new['Revenus bruts'] = pd.to_numeric(df_new['Revenus bruts'], errors='coerce')

        # Detect duplicates
        dups = df_new[df_new['Code de confirmation'].isin(master_df.get('Code de confirmation', []))]
        st.header(L['duplicates'])
        if not dups.empty:
            st.dataframe(dups)
        else:
            st.success(L['no_duplicates'])

        # Append unique bookings
        unique = df_new[~df_new['Code de confirmation'].isin(master_df.get('Code de confirmation', []))]
        if not unique.empty:
            st.header(L['new_bookings'])
            disp = unique.rename(columns={
                'Date de réservation': L['reservation_date'],
                'Date de début': L['arrival'],
                'Date de fin': L['departure'],
                'Revenus bruts': L['total_rev'],
                'Code de confirmation': L['confirmation_code']
            })
            st.dataframe(disp)
            master_df = pd.concat([master_df, unique], ignore_index=True)
            master_df.to_csv(MASTER_PATH, index=False)
            st.success(L['added_count'].format(count=len(unique)))
        else:
            st.info(L['no_new'])

# KPI section (only once)
if not master_df.empty:
    st.header(L['kpi_header'])
    # Normalize types
    master_df['Date de réservation'] = pd.to_datetime(master_df['Date de réservation'], errors='coerce')
    master_df['Date de début'] = pd.to_datetime(master_df['Date de début'], errors='coerce')
    master_df['Date de fin'] = pd.to_datetime(master_df['Date de fin'], errors='coerce')
    master_df['Revenus bruts'] = pd.to_numeric(master_df['Revenus bruts'], errors='coerce')

    df = master_df.copy()
    df['Nights'] = (df['Date de fin'] - df['Date de début']).dt.days
    df['Lead Time'] = (df['Date de début'] - df['Date de réservation']).dt.days

    # Total revenue metric
    total = df['Revenus bruts'].sum()
    st.metric(L['total_rev'], f"€{total:,.2f}")

    # Time series aggregations
    ts = df.set_index('Date de début')
    monthly_rev = ts['Revenus bruts'].resample('ME').sum()
    monthly_nights = ts['Nights'].resample('ME').sum()
    avg_nights = ts['Nights'].resample('ME').mean()
    month_labels = monthly_rev.index.to_period('M').astype(str)
    monthly_rev.index = month_labels
    monthly_nights.index = month_labels
    avg_nights.index = month_labels

    st.subheader(L['monthly_rev'])
    st.bar_chart(monthly_rev)
    st.subheader(L['monthly_nights'])
    st.bar_chart(monthly_nights)
    st.subheader(L['avg_nights'])
    st.line_chart(avg_nights)

    # Lead time distribution
    bins = [0, 7, 30, 90, df['Lead Time'].max()]
    labels = ['0-7 days', '8-30 days', '31-90 days', '>90 days']
    df['Lead Bin'] = pd.cut(df['Lead Time'], bins=bins, labels=labels, include_lowest=True)
    lead_pct = df['Lead Bin'].value_counts(normalize=True).reindex(labels) * 100
    st.subheader(L['lead_dist'])
    st.bar_chart(lead_pct)

    # Recent bookings preview
    st.subheader(L['recent_bookings'])
    recent = df.sort_values('Date de début', ascending=False).head(20)
    recent = recent.rename(columns={
        'Date de réservation': L['reservation_date'],
        'Date de début': L['arrival'],
        'Date de fin': L['departure'],
        'Revenus bruts': L['total_rev'],
        'Code de confirmation': L['confirmation_code']
    })
    st.dataframe(recent)
else:
    st.info(L['no_new'])
