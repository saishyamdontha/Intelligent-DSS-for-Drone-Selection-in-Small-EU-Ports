"""
EU Country Regulations
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology

EASA regulations apply across all EU member states but each country
has additional national rules on top of EU 2019/947 and EU 2019/945.
"""

# All EU member states with EASA drone regulations
EU_COUNTRY_REGULATIONS = {
    "SE": {
        "name": "Sweden",
        "flag": "🇸🇪",
        "authority": "Transportstyrelsen (Swedish Transport Agency)",
        "authority_url": "https://www.transportstyrelsen.se",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "No specific coastal restrictions beyond EASA Open category rules",
        "port_specific_rules": "Port authority approval required for operations within 500m of port infrastructure",
        "national_additions": [
            "Registration mandatory for drones above 250g",
            "A1/A3 subcategory competency certificate required",
            "Operations near military areas require special permits",
            "Drone insurance recommended for commercial operations"
        ],
        "eliminated_categories": [],
        "notes": "Sweden follows standard EASA regulations with no major additional restrictions"
    },
    "DE": {
        "name": "Germany",
        "flag": "🇩🇪",
        "authority": "Luftfahrt-Bundesamt (LBA) / Bundesministerium für Digitales und Verkehr",
        "authority_url": "https://www.lba.de",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "North Sea and Baltic Sea coastlines have restricted zones near shipping lanes",
        "port_specific_rules": "Hamburg, Bremen ports require specific operational authorisation from port authority",
        "national_additions": [
            "Kennzeichnungspflicht: All drones above 250g must display operator registration number",
            "No-fly zones: 1.5km around airports, military areas, crowds",
            "Nature reserves require special permits",
            "Commercial operations require liability insurance minimum €1M",
            "LuftVO §21h applies to all commercial port operations"
        ],
        "eliminated_categories": [],
        "notes": "Germany has strict no-fly zone enforcement and insurance requirements"
    },
    "FR": {
        "name": "France",
        "flag": "🇫🇷",
        "authority": "Direction Générale de l'Aviation Civile (DGAC)",
        "authority_url": "https://www.ecologie.gouv.fr/direction-generale-laviation-civile-dgac",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 800,
        "remote_id_required": True,
        "night_flying_allowed": False,
        "bvlos_allowed": False,
        "coastal_restrictions": "Coastal zones within 300m of shore require prefecture authorisation",
        "port_specific_rules": "Major ports (Marseille, Le Havre) require DGAC operational authorisation",
        "national_additions": [
            "Night flying prohibited without special DGAC waiver",
            "Arrêté du 24 décembre 2015 applies to professional drone operations",
            "Mandatory training for commercial operators (CATT certificate)",
            "Registration required above 800g (stricter than EASA threshold)",
            "Drone flights over coastal areas may require maritime authority approval"
        ],
        "eliminated_categories": [],
        "notes": "France prohibits night flying by default — drones requiring night operations need DGAC waiver"
    },
    "NL": {
        "name": "Netherlands",
        "flag": "🇳🇱",
        "authority": "Inspectie Leefomgeving en Transport (ILT)",
        "authority_url": "https://www.ilent.nl",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "North Sea coastal operations require coordination with MARIN and port authorities",
        "port_specific_rules": "Rotterdam Port Authority requires pre-flight notification and approval for all drone operations",
        "national_additions": [
            "Rotterdam is world's busiest port — strict operational protocols apply",
            "Mandatory liability insurance for commercial operations",
            "ILT registration required for all operators",
            "Drone operations in Schiphol TMA require special permits"
        ],
        "eliminated_categories": [],
        "notes": "Rotterdam port has among the strictest drone regulations in Europe"
    },
    "ES": {
        "name": "Spain",
        "flag": "🇪🇸",
        "authority": "Agencia Estatal de Seguridad Aérea (AESA)",
        "authority_url": "https://www.seguridadaerea.gob.es",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Mediterranean and Atlantic coastal zones have seasonal restrictions (tourist season)",
        "port_specific_rules": "Barcelona, Valencia, Bilbao ports require AESA operational authorisation",
        "national_additions": [
            "RD 1036/2017 applies to professional drone operations",
            "Mandatory insurance for commercial operations",
            "Seasonal coastal restrictions during summer tourist season",
            "Port operations require coordination with Puertos del Estado"
        ],
        "eliminated_categories": [],
        "notes": "Spain has seasonal coastal restrictions that may affect port operations"
    },
    "IT": {
        "name": "Italy",
        "flag": "🇮🇹",
        "authority": "Ente Nazionale per l'Aviazione Civile (ENAC)",
        "authority_url": "https://www.enac.gov.it",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Adriatic and Tyrrhenian coastal zones require ENAC authorisation for commercial ops",
        "port_specific_rules": "Genova, Venice, Taranto ports require ENAC and port authority approval",
        "national_additions": [
            "ENAC Regolamento Mezzi Aerei a Pilotaggio Remoto applies",
            "Mandatory liability insurance minimum €2M for commercial ops",
            "Cultural heritage sites have strict no-fly zones",
            "Venice lagoon area has special drone restrictions"
        ],
        "eliminated_categories": [],
        "notes": "Italy has strict insurance requirements and cultural heritage no-fly zones"
    },
    "PL": {
        "name": "Poland",
        "flag": "🇵🇱",
        "authority": "Urząd Lotnictwa Cywilnego (ULC)",
        "authority_url": "https://www.ulc.gov.pl",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Baltic Sea coastal operations require coordination with maritime authorities",
        "port_specific_rules": "Gdansk, Gdynia, Szczecin ports require ULC and port authority approval",
        "national_additions": [
            "PL UAS regulations align with EASA but have additional military zone restrictions",
            "Baltic Sea port operations require Maritime Office coordination",
            "Registration mandatory for drones above 250g",
            "Commercial operators must hold ULC certificate"
        ],
        "eliminated_categories": [],
        "notes": "Poland has additional military zone restrictions near Baltic coast"
    },
    "DK": {
        "name": "Denmark",
        "flag": "🇩🇰",
        "authority": "Trafikstyrelsen (Danish Transport Authority)",
        "authority_url": "https://www.trafikstyrelsen.dk",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "North Sea and Baltic Sea operations require maritime coordination",
        "port_specific_rules": "Copenhagen and Esbjerg ports require port authority notification",
        "national_additions": [
            "Danish Drone Act BL 9-900 applies",
            "Operations near offshore wind farms require special permits",
            "Greenland and Faroe Islands have separate regulations",
            "Mandatory registration for drones above 250g"
        ],
        "eliminated_categories": [],
        "notes": "Denmark has restrictions near offshore wind farms common in Danish waters"
    },
    "FI": {
        "name": "Finland",
        "flag": "🇫🇮",
        "authority": "Traficom (Finnish Transport and Communications Agency)",
        "authority_url": "https://www.traficom.fi",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Baltic Sea and Gulf of Finland operations require maritime coordination",
        "port_specific_rules": "Helsinki, Turku ports require Traficom and port authority coordination",
        "national_additions": [
            "Finnish Air Navigation Regulations (FANR) apply",
            "Operations near Russian border require special permits",
            "Winter operations: ice and snow conditions must be assessed",
            "Mandatory registration for drones above 250g"
        ],
        "eliminated_categories": [],
        "notes": "Finland has border zone restrictions near Russian border"
    },
    "NO": {
        "name": "Norway",
        "flag": "🇳🇴",
        "authority": "Luftfartstilsynet (Civil Aviation Authority Norway)",
        "authority_url": "https://luftfartstilsynet.no",
        "easa_category": "EEA Member (follows EASA)",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Norwegian fjords and coastal areas have strict nature protection zones",
        "port_specific_rules": "Bergen, Oslo, Stavanger ports require CAA Norway and port authority approval",
        "national_additions": [
            "Norway is EEA member — follows EASA regulations",
            "Strict nature protection in fjord areas",
            "Oil platform exclusion zones (500m radius)",
            "Svalbard has separate aviation regulations"
        ],
        "eliminated_categories": [],
        "notes": "Norway has strict nature protection zones and oil platform exclusions"
    },
    "BE": {
        "name": "Belgium",
        "flag": "🇧🇪",
        "authority": "Directorate-General Air Transport (DGTM)",
        "authority_url": "https://mobilit.belgium.be",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "North Sea coastal operations require DGTM and maritime authority approval",
        "port_specific_rules": "Antwerp (world's 2nd largest port) has strict drone protocols — pre-approval mandatory",
        "national_additions": [
            "Antwerp Port Authority has own drone regulations",
            "Mandatory registration for drones above 250g",
            "Operations near NATO headquarters require special permits",
            "Brussels exclusion zone: 3km radius"
        ],
        "eliminated_categories": [],
        "notes": "Antwerp is Europe's 2nd largest port with strict drone protocols"
    },
    "PT": {
        "name": "Portugal",
        "flag": "🇵🇹",
        "authority": "Autoridade Nacional de Aviação Civil (ANAC)",
        "authority_url": "https://www.anac.pt",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Atlantic coastal operations require ANAC and maritime authority approval",
        "port_specific_rules": "Lisbon, Sines, Leixões ports require ANAC operational authorisation",
        "national_additions": [
            "Decreto-Lei n.º 58/2019 applies to drone operations",
            "Mandatory insurance for commercial operations",
            "Azores and Madeira have separate regional regulations",
            "Strong Atlantic winds: weather assessment mandatory"
        ],
        "eliminated_categories": [],
        "notes": "Portugal has Atlantic weather considerations and island territories with separate rules"
    },
    "GR": {
        "name": "Greece",
        "flag": "🇬🇷",
        "authority": "Hellenic Civil Aviation Authority (HCAA)",
        "authority_url": "https://www.hcaa.gr",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Aegean Sea islands have strict airspace regulations due to proximity to Turkey",
        "port_specific_rules": "Piraeus (Mediterranean's largest port) requires HCAA and port authority approval",
        "national_additions": [
            "Military airspace restrictions near Greek-Turkish border",
            "Island drone operations require HCAA approval",
            "Archaeological site no-fly zones",
            "Piraeus port has specific drone protocols"
        ],
        "eliminated_categories": [],
        "notes": "Greece has military airspace restrictions near Turkish border and archaeological no-fly zones"
    },
    "HR": {
        "name": "Croatia",
        "flag": "🇭🇷",
        "authority": "Croatia Control (CCAA)",
        "authority_url": "https://www.ccaa.hr",
        "easa_category": "EU Member State",
        "allowed_categories": ["Open-A1", "Open-A2", "Open-A3", "Specific"],
        "max_altitude_m": 120,
        "registration_required_above_g": 250,
        "remote_id_required": True,
        "night_flying_allowed": True,
        "bvlos_allowed": False,
        "coastal_restrictions": "Adriatic Sea coastal operations require CCAA approval — tourist season restrictions",
        "port_specific_rules": "Rijeka, Split ports require CCAA and port authority approval",
        "national_additions": [
            "Tourist season restrictions June-September",
            "National park no-fly zones (Plitvice, Krka)",
            "Adriatic coastal airspace shared with Bosnia",
            "Registration mandatory for drones above 250g"
        ],
        "eliminated_categories": [],
        "notes": "Croatia has tourist season restrictions on Adriatic coast"
    },
}

def get_country_regulations(country_code: str) -> dict:
    """Get regulations for a specific EU country."""
    return EU_COUNTRY_REGULATIONS.get(country_code.upper(), None)

def get_all_countries() -> list:
    """Get list of all supported countries."""
    return [
        {"code": code, "name": data["name"], "flag": data["flag"]}
        for code, data in EU_COUNTRY_REGULATIONS.items()
    ]

def apply_country_filter(drones: list, country_code: str) -> dict:
    """
    Apply country-specific regulations to filter drones.
    Returns eligible drones and eliminated drones with reasons.
    """
    regs = get_country_regulations(country_code)
    if not regs:
        return {"eligible": drones, "eliminated": [], "country": None}

    eligible = []
    eliminated = []
    warnings = []

    for drone in drones:
        reasons = []
        drone_warnings = []

        # Check regulatory category allowed
        if drone["regulatory_compliance"] not in regs["allowed_categories"]:
            reasons.append(
                f"{regs['name']} does not allow '{drone['regulatory_compliance']}' category drones. "
                f"Allowed: {', '.join(regs['allowed_categories'])}"
            )

        # Check night flying
        if not regs["night_flying_allowed"] and drone["night_vision"] != "none":
            drone_warnings.append(
                f"Night flying requires special waiver from {regs['authority']} in {regs['name']}"
            )

        # Check BVLOS
        if not regs["bvlos_allowed"] and drone["flight_range_km"] > 1.5:
            drone_warnings.append(
                f"BVLOS operations (range > 1.5km) require Specific authorisation in {regs['name']}"
            )

        # Add country-specific warnings
        for addition in regs["national_additions"][:2]:
            drone_warnings.append(f"{regs['name']}: {addition}")

        if reasons:
            eliminated.append({
                "id": drone["id"],
                "name": drone["name"],
                "elimination_reasons": reasons,
                "country": regs["name"]
            })
        else:
            drone_copy = drone.copy()
            drone_copy["country_warnings"] = drone_warnings
            eligible.append(drone_copy)

    return {
        "eligible": eligible,
        "eliminated": eliminated,
        "country": regs,
        "summary": {
            "country_name":   regs["name"],
            "authority":      regs["authority"],
            "max_altitude_m": regs["max_altitude_m"],
            "night_flying":   regs["night_flying_allowed"],
            "bvlos_allowed":  regs["bvlos_allowed"],
            "port_rules":     regs["port_specific_rules"],
            "notes":          regs["notes"],
        }
    }

if __name__ == "__main__":
    print("Supported EU countries:")
    for c in get_all_countries():
        print(f"  {c['flag']} {c['code']}: {c['name']}")
