def calculate_carbon_footprint(
    km_per_week,
    electricity_kwh_per_month,
    diet,
    flights_per_year,
    recycles,
    water_liters_per_day,
    shopping_habit,
    digital_hours_per_day
):
    # Emission factors (approximate & weekly)
    emissions = {
        "Transport": km_per_week * 0.21,
        "Electricity": (electricity_kwh_per_month / 4) * 0.9,
        "Food": {"Vegetarian": 35, "Mixed": 50, "Non-Vegetarian": 65}[diet],
        "Flights": (flights_per_year * 250) / 52,
        "Waste": 5 if recycles == "Yes" else 15,
        "Water": (water_liters_per_day * 7) * 0.0015,
        "Shopping": {"Minimal": 5, "Average": 15, "Frequent": 30}[shopping_habit],
        "Digital": digital_hours_per_day * 7 * 1.2,
    }

    total = sum(emissions.values())
    return total, emissions