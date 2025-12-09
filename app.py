"""
Streamlit-Anwendung zur Analyse und Filterung von Magnetgetriebe-Daten.
Die Anwendung ermöglicht die Suche nach Übersetzungen, Rotor- und Modulator-Drehmomenten
sowie deren Kombinationen. Die Qualität der Kombinationen wird farblich dargestellt.
"""

import streamlit as st
import pandas as pd
import os
from PIL import Image  # Wird verwendet, um das Logo zu laden und anzuzeigen
import math

# Streamlit-Seitenlayout auf "wide" setzen, um mehr Platz für die Inhalte zu schaffen
st.set_page_config(layout="wide")

# 2. CSS-Stile für zentrierte Tabellen injizieren (HIER EINFÜGEN!)
# CSS-Stile für Tabellen (Schriftgröße und Ausrichtung)
st.markdown(
    """
    <style>
    table {
        font-size: 20px !important;
    }
    table th {
        font-size: 20px !important;
        text-align: center !important;
    }
    table td {
        font-size: 40px !important;
        text-align: center !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Logo anzeigen (linksbündig)
col1, col2, col3 = st.columns([2, 1, 2])  # Drei Spalten: links, mitte, rechts
with col2:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=350)  # Breite des Logos anpassen
    except FileNotFoundError:
        st.warning("Logo-Datei nicht gefunden. Bitte überprüfe den Pfad.")


# --- Farbige Legende für die Qualität des Drehmomentrippels ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        '<div style="background-color: rgba(0, 255, 0, 0.7); padding: 10px; border-radius: 5px; text-align: center;">'
        '<strong>Qualität = 1</strong><br>Guter Drehmomentrippel</div>',
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        '<div style="background-color: rgba(255, 255, 0, 0.7); padding: 10px; border-radius: 5px; text-align: center;">'
        '<strong>Qualität = 2</strong><br>Mittlerer Drehmomentrippel</div>',
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        '<div style="background-color: rgba(255, 0, 0, 0.7); padding: 10px; border-radius: 5px; text-align: center;">'
        '<strong>Qualität > 2</strong><br>Schlechter Drehmomentrippel</div>',
        unsafe_allow_html=True
    )

# Titel der Anwendung zentriert anzeigen
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("<h1 class='centered-title'>Magnetgetriebe mit 80mm Aussendurchmesser und festem Stator</h1>", unsafe_allow_html=True)

# --- Excel-Datei laden ---
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "magnet.xlsx")
if not os.path.exists(EXCEL_PATH):
    st.error(f"Excel-Datei nicht gefunden unter:\n{EXCEL_PATH}")
    st.stop()
df = pd.read_excel(EXCEL_PATH, header=None)

def berechne_qualitaet(row):
    """
    Berechnet den Qualitätsfaktor für den Drehmomentrippel.

    Args:
        row (pd.Series): Eine Zeile des DataFrames mit den Spalten "Modulatorzahl" und "Polzahl Rotor".

    Returns:
        float: Qualitätsfaktor (1 = bester Wert, größer = schlechterer Rippel).
    """
    mod = int(round(row["Modulatorzahl"]))  # Modulatorzahl als Integer
    rotor = int(round(row["Polzahl Rotor"]))  # Rotor-Polzahl als Integer
    kgv = (mod * rotor) // math.gcd(mod, rotor)  # Kleinstes gemeinsames Vielfaches berechnen
    return (mod * rotor) / kgv  # Qualitätsfaktor zurückgeben

def farbige_und_zentrierte_formatierung(df):
    """
    Wendet eine farbige Hintergrundformatierung und zentrierte Textausrichtung
    auf den DataFrame an, basierend auf dem Qualitätsfaktor.
    Zentriert sowohl die Daten als auch die Spaltenüberschriften.

    Args:
        df (pd.DataFrame): DataFrame mit den Daten, inkl. einer Spalte "Qualität".

    Returns:
        pd.io.formats.style.Styler: Formatierter DataFrame mit farbiger Hintergrundformatierung und zentriertem Text.
    """
    def farbe_und_zentrierung(qualitaet):
        """
        Gibt die CSS-Formatierung für eine Zelle basierend auf dem Qualitätsfaktor zurück.

        Args:
            qualitaet (float): Qualitätsfaktor der Zeile.

        Returns:
            str: CSS-String für die Hintergrundfarbe und Textausrichtung.
        """
        if qualitaet == 1:
            return 'background-color: rgba(0, 255, 0, 0.7); text-align: center'
        elif qualitaet == 2:
            return 'background-color: rgba(255, 255, 0, 0.7); text-align: center'
        else:
            return 'background-color: rgba(255, 0, 0, 0.7); text-align: center'

    # Qualitätsfaktor für jede Zeile berechnen
    df["Qualität"] = df.apply(lambda row: berechne_qualitaet(row), axis=1)
    # DataFrame ohne Qualitäts-Spalte für die Anzeige erstellen
    df_ohne_qualitaet = df.drop(columns=["Qualität"])

    # Styler erstellen und Formatierung anwenden
    styled_df = df_ohne_qualitaet.style.apply(
        lambda x: [
            farbe_und_zentrierung(df.loc[i, "Qualität"])
            for i in df.index
        ],
        axis=0
    ).set_table_styles([
        # Zentriert alle Spaltenüberschriften
        {'selector': 'th', 'props': [('text-align', 'center'), ('font-size', '20px')]},
        # Zentriert alle Zelleninhalte
        {'selector': 'td', 'props': [('text-align', 'center'), ('font-size', '20px')]}
    ])

    return styled_df




# --- Tabs für die verschiedenen Suchfunktionen erstellen ---
tab_uebersetzung, tab_rotor, tab_mod, tab_combo1, tab_combo2, tab_combo3 = st.tabs([
    "Übersetzung",
    "Rotor-Drehmoment",
    "Modulator-Drehmoment",
    "Übersetzung + Rotor",
    "Übersetzung + Modulator",
    "Rotor + Modulator"
])

# --- Daten aus der Excel-Datei extrahieren ---
# Zeile 1 enthält die Polzahl des Stators für alle Varianten
p_stator = df.iloc[0, :].tolist()
results = []

# Spaltenweise durch die Daten iterieren und die relevanten Werte extrahieren
for col in df.columns:
    stator = df.iloc[0, col]  # Polzahl Stator
    start_row = 1  # Startzeile für die Blöcke
    while start_row + 4 < len(df):
        # Rotor-Polzahl, Modulatorzahl, Übersetzung, Modulator- und Rotor-Drehmoment extrahieren
        rotor = df.iloc[start_row, col]
        mod = df.iloc[start_row+1, col]
        ratio = df.iloc[start_row+2, col]
        torque_mod = df.iloc[start_row+3, col]
        torque_rot = df.iloc[start_row+4, col]
        results.append({
            "Spalte": col,
            "Polzahl Stator": stator,
            "Polzahl Rotor": rotor,
            "Modulatorzahl": mod,
            "Übersetzung": ratio,
            "Drehmoment Modulator": torque_mod,
            "Drehmoment Rotor": torque_rot
        })
        start_row += 5  # Zum nächsten Block springen

# DataFrame mit den extrahierten Daten erstellen
df_all = pd.DataFrame(results)

# --- Tab: Suche nach Übersetzung ---
with tab_uebersetzung:
    st.subheader("Suche nach Übersetzung")
    # Auswahl aller möglichen Übersetzungen
    ratio_list = sorted(df_all["Übersetzung"].unique())
    selected_ratio = st.selectbox(
        "Übersetzung auswählen",
        ratio_list,
        help="Wähle die Zielübersetzung, die du ungefähr erreichen willst."
    )
    tolerance_Uebersetzung = st.number_input(
        "Toleranz: ",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="tolerance_gear_ratio",
        help="Die Toleranz legt fest, wie weit die Ergebnisse vom Zielwert abweichen dürfen."
    )
    # Bereich für die Filterung berechnen
    min_gear_ratio = selected_ratio - tolerance_Uebersetzung
    max_gear_ratio = selected_ratio + tolerance_Uebersetzung
    st.markdown(f"**Gefiltert wird die Übersetzung zwischen {min_gear_ratio:.2f} und {max_gear_ratio:.2f}**")
    # DataFrame nach Übersetzung filtern
    gear_ratio_filtered = df_all[
        (df_all["Übersetzung"] >= min_gear_ratio) &
        (df_all["Übersetzung"] <= max_gear_ratio)
    ]
    # Relevante Spalten für die Anzeige auswählen
    result_display = gear_ratio_filtered[[
        "Polzahl Stator",
        "Polzahl Rotor",
        "Modulatorzahl",
        "Übersetzung",
        "Drehmoment Modulator",
        "Drehmoment Rotor"
    ]]
    # Formatierten DataFrame anzeigen
    styled_combo_display = farbige_und_zentrierte_formatierung(result_display.copy())
    st.subheader("Alle Kombinationen für diese Übersetzung")
    st.dataframe(styled_combo_display)


# --- Tab: Suche nach Rotor-Drehmoment ---
with tab_rotor:
    st.subheader("Nach Rotor-Drehmoment filtern")
    # Eingabefelder für Ziel-Drehmoment und Toleranz
    target_torque_Rotor = st.number_input(
        "Ziel Rotor Drehmoment (Nm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
        key="target_torque_Rotor",
        help="Wähle das Zieldrehmoment des Rotors aus."
    )
    tolerance_Rotor = st.number_input(
        "Toleranz (Nm)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="tolerance_torque_Rotor",
        help="Die Toleranz definiert, wie weit weg man vom gewünschten Rotordrehmoment sein darf."
    )
    # Bereich für die Filterung berechnen
    min_torque_Rotor = target_torque_Rotor - tolerance_Rotor
    max_torque_Rotor = target_torque_Rotor + tolerance_Rotor
    st.markdown(f"**Gefiltert wird zwischen {min_torque_Rotor:.2f} Nm und {max_torque_Rotor:.2f} Nm**")
    # DataFrame nach Rotor-Drehmoment filtern
    torque_filtered = df_all[
        (df_all["Drehmoment Rotor"] >= min_torque_Rotor) &
        (df_all["Drehmoment Rotor"] <= max_torque_Rotor)
    ]
    # Relevante Spalten für die Anzeige auswählen
    torque__Rotor_filtered_display = torque_filtered[[
        "Polzahl Stator",
        "Polzahl Rotor",
        "Modulatorzahl",
        "Übersetzung",
        "Drehmoment Modulator",
        "Drehmoment Rotor"
    ]]
    # Formatierten DataFrame anzeigen
    styled_combo_display_TRot = farbige_und_zentrierte_formatierung(torque__Rotor_filtered_display.copy())
    st.subheader("Kombinationen im Drehmomentbereich")
    st.dataframe(styled_combo_display_TRot)

# --- Tab: Suche nach Modulator-Drehmoment ---
with tab_mod:
    st.subheader("Nach Modulator-Drehmoment filtern")
    # Eingabefelder für Ziel-Drehmoment und Toleranz
    target_torque_MOD = st.number_input(
        "Ziel Modulator Drehmoment (Nm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
        key="target_torque_MOD",
        help="Wähle das Zieldrehmoment des Modulators aus."
    )
    tolerance_MOD = st.number_input(
        "Toleranz (Nm)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="tolerance_torque_MOD",
        help="Die Toleranz definiert, wie weit weg man vom gewünschten Modulatordrehmoment sein darf."
    )
    # Bereich für die Filterung berechnen
    min_torque_MOD = target_torque_MOD - tolerance_MOD
    max_torque_MOD = target_torque_MOD + tolerance_MOD
    st.markdown(f"**Gefiltert wird zwischen {min_torque_MOD:.2f} Nm und {max_torque_MOD:.2f} Nm**")
    # DataFrame nach Modulator-Drehmoment filtern
    torque_filtered_MOD = df_all[
        (df_all["Drehmoment Modulator"] >= min_torque_MOD) &
        (df_all["Drehmoment Modulator"] <= max_torque_MOD)
    ]
    # Relevante Spalten für die Anzeige auswählen
    torque_MOD_filtered_display = torque_filtered_MOD[[
        "Polzahl Stator",
        "Polzahl Rotor",
        "Modulatorzahl",
        "Übersetzung",
        "Drehmoment Modulator",
        "Drehmoment Rotor"
    ]]
    # Formatierten DataFrame anzeigen
    styled_combo_display_TMOD = farbige_und_zentrierte_formatierung(torque_MOD_filtered_display.copy())
    st.subheader("Kombinationen im Drehmomentbereich")
    st.dataframe(styled_combo_display_TMOD)

# --- Tab: Kombi-Suche Übersetzung und Rotor-Drehmoment ---
with tab_combo1:
    st.subheader("Kombi-Suche: Übersetzung UND Rotor-Drehmoment")
    # Auswahl der Übersetzung und Toleranz
    combo_ratio_TRot = st.selectbox(
        "Übersetzung auswählen",
        sorted(df_all["Übersetzung"].unique()),
        key="combo_ratio_TRotor_i",
        help="Wähle die gewünschte Übersetzung aus."
    )
    combo_tolerance_i = st.number_input(
        "Toleranz (-)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="combo_ratio_TRotor_i_tol",
        help="Toleranz für die Übersetzung."
    )
    min_t_i_TRotor = combo_ratio_TRot - combo_tolerance_i
    max_t_i_TRotor = combo_ratio_TRot + combo_tolerance_i
    # Auswahl des Ziel-Drehmoments und Toleranz für den Rotor
    combo_target_torque = st.number_input(
        "Ziel Rotor Drehmoment (Nm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
        key="combo_ratio_TRotor_TRotor",
        help="Wähle das gewünschte Rotor-Drehmoment aus."
    )
    combo_tolerance_T = st.number_input(
        "Toleranz (Nm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
        key="combo_ratio_TRotor_tol",
        help="Toleranz für das Rotor-Drehmoment."
    )
    min_t_T = combo_target_torque - combo_tolerance_T
    max_t_T = combo_target_torque + combo_tolerance_T
    st.markdown(
        f"Gefiltert wird nach Übersetzung **{combo_ratio_TRot}** "
        f"UND Rotor-Drehmoment **zwischen {min_t_T:.2f} Nm und {max_t_T:.2f} Nm**."
    )
    # DataFrame nach Übersetzung und Rotor-Drehmoment filtern
    combo_filtered = df_all[
        (df_all["Übersetzung"] >= min_t_i_TRotor) &
        (df_all["Übersetzung"] <= max_t_i_TRotor) &
        (df_all["Drehmoment Rotor"] >= min_t_T) &
        (df_all["Drehmoment Rotor"] <= max_t_T)
    ]
    # Relevante Spalten für die Anzeige auswählen
    combo_display_TRot_i = combo_filtered[[
        "Polzahl Stator",
        "Polzahl Rotor",
        "Modulatorzahl",
        "Übersetzung",
        "Drehmoment Modulator",
        "Drehmoment Rotor"
    ]]
    # Formatierten DataFrame anzeigen
    styled_combo_display_i_TRot = farbige_und_zentrierte_formatierung(combo_display_TRot_i.copy())
    st.subheader("Ergebnisse der Kombi-Suche")
    st.dataframe(styled_combo_display_i_TRot)

# --- Tab: Kombi-Suche Übersetzung und Modulator-Drehmoment ---
with tab_combo2:
    st.subheader("Kombi-Suche: Übersetzung UND Modulator-Drehmoment")
    # Auswahl der Übersetzung und Toleranz
    combo_ratio_TMOD = st.selectbox(
        "Übersetzung auswählen",
        sorted(df_all["Übersetzung"].unique()),
        key="combo_ratio_TMOD_i",
        help="Wähle die gewünschte Übersetzung aus."
    )
    combo_tolerance_i = st.number_input(
        "Toleranz (-)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="combo_ratio_TMOD_i_tol",
        help="Toleranz für die Übersetzung."
    )
    min_t_i_TMOD = combo_ratio_TMOD - combo_tolerance_i
    max_t_i_TMOD = combo_ratio_TMOD + combo_tolerance_i
    # Auswahl des Ziel-Drehmoments und Toleranz für den Modulator
    combo_target_torque = st.number_input(
        "Ziel Modulator Drehmoment (Nm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
        key="combo_ratio_TMOD_TMOD",
        help="Wähle das gewünschte Modulator-Drehmoment aus."
    )
    combo_tolerance = st.number_input(
        "Toleranz (Nm)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="combo_ratio_TMOD_tol",
        help="Toleranz für das Modulator-Drehmoment."
    )
    min_t_T = combo_target_torque - combo_tolerance
    max_t_T = combo_target_torque + combo_tolerance
    st.markdown(
        f"Gefiltert wird nach Übersetzung **{combo_ratio_TMOD}** "
        f"UND Modulator-Drehmoment **zwischen {min_t_T:.2f} Nm und {max_t_T:.2f} Nm**."
    )
    # DataFrame nach Übersetzung und Modulator-Drehmoment filtern
    combo_filtered = df_all[
        (df_all["Übersetzung"] >= min_t_i_TMOD) &
        (df_all["Übersetzung"] <= max_t_i_TMOD) &
        (df_all["Drehmoment Modulator"] >= min_t_T) &
        (df_all["Drehmoment Modulator"] <= max_t_T)
    ]
    # Relevante Spalten für die Anzeige auswählen
    combo_display_TMOD_i = combo_filtered[[
        "Polzahl Stator",
        "Polzahl Rotor",
        "Modulatorzahl",
        "Übersetzung",
        "Drehmoment Modulator",
        "Drehmoment Rotor"
    ]]
    # Formatierten DataFrame anzeigen
    styled_combo_display_i_TMOD = farbige_und_zentrierte_formatierung(combo_display_TMOD_i.copy())
    st.subheader("Ergebnisse der Kombi-Suche")
    st.dataframe(styled_combo_display_i_TMOD)

# --- Tab: Kombi-Suche Rotor- und Modulator-Drehmoment ---
with tab_combo3:
    st.subheader("Kombi-Suche: Rotor-Drehmoment + Modulator-Drehmoment")
    # Auswahl des Ziel-Drehmoments und Toleranz für den Modulator
    combo_target_torque_MOD = st.number_input(
        "Ziel Modulator Drehmoment (Nm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
        key="combo_TRotor_TMOD",
        help="Wähle das gewünschte Modulator-Drehmoment aus."
    )
    combo_tolerance_MOD = st.number_input(
        "Toleranz (Nm)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="combo_TRotor_TMOD_tol",
        help="Toleranz für das Modulator-Drehmoment."
    )
    min_t_MOD = combo_target_torque_MOD - combo_tolerance_MOD
    max_t_MOD = combo_target_torque_MOD + combo_tolerance_MOD
    # Auswahl des Ziel-Drehmoments und Toleranz für den Rotor
    combo_target_torque_Rotor = st.number_input(
        "Ziel Rotor Drehmoment (Nm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
        key="combo_target_Rotor",
        help="Wähle das gewünschte Rotor-Drehmoment aus."
    )
    combo_tolerance_Rotor = st.number_input(
        "Toleranz (Nm)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="combo_tol_Rotor",
        help="Toleranz für das Rotor-Drehmoment."
    )
    min_t_Rotor = combo_target_torque_Rotor - combo_tolerance_Rotor
    max_t_Rotor = combo_target_torque_Rotor + combo_tolerance_Rotor
    st.markdown(
        f"Gefiltert wird nach Modulator-Drehmoment **zwischen {min_t_MOD:.2f} Nm und {max_t_MOD:.2f} Nm** "
        f"UND Rotor-Drehmoment **zwischen {min_t_Rotor:.2f} Nm und {max_t_Rotor:.2f} Nm**."
    )
    # DataFrame nach Rotor- und Modulator-Drehmoment filtern
    combo_filtered = df_all[
        (df_all["Drehmoment Modulator"] >= min_t_MOD) &
        (df_all["Drehmoment Modulator"] <= max_t_MOD) &
        (df_all["Drehmoment Rotor"] >= min_t_Rotor) &
        (df_all["Drehmoment Rotor"] <= max_t_Rotor)
    ]
    # Relevante Spalten für die Anzeige auswählen
    combo_display_TRot_TMOD = combo_filtered[[
        "Polzahl Stator",
        "Polzahl Rotor",
        "Modulatorzahl",
        "Übersetzung",
        "Drehmoment Modulator",
        "Drehmoment Rotor"
    ]]
    # Formatierten DataFrame anzeigen
    styled_combo_display_Trot_TMOD = farbige_und_zentrierte_formatierung(combo_display_TRot_TMOD.copy())
    st.subheader("Ergebnisse der Kombi-Suche")
    st.dataframe(styled_combo_display_Trot_TMOD)
