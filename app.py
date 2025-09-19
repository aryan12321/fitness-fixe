from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta


app = Flask(__name__)

# -------------------------
# Calculator Metadata (for index.html menu/cards)
# -------------------------
CALCULATORS = [
    # Nutrition
    {"name": "Protein Requirement", "route": "protein", "desc": "Track daily protein intake vs. target", "icon": "🥩", "category": "Nutrition"},
    {"name": "Daily Calorie (TDEE)", "route": "tdee", "desc": "Calculate BMR & daily calorie needs", "icon": "🔥", "category": "Nutrition"},
    {"name": "Macro Split", "route": "macro", "desc": "Balance protein, carbs & fats", "icon": "🥗", "category": "Nutrition"},
    {"name": "Water Intake", "route": "water", "desc": "Check daily hydration needs", "icon": "💧", "category": "Nutrition"},
    {"name": "Sugar Intake", "route": "sugar", "desc": "Check safe vs risky sugar intake", "icon": "🍬", "category": "Nutrition"},

    # Fitness & Body
    {"name": "BMI Calculator", "route": "bmi", "desc": "Check BMI & body fat %", "icon": "⚖️", "category": "Fitness"},
    {"name": "Body Fat % Estimator", "route": "bodyfat", "desc": "Estimate body fat %", "icon": "📉", "category": "Fitness"},
    {"name": "Ideal Weight (India)", "route": "ideal_weight", "desc": "Find healthy weight range", "icon": "📏", "category": "Fitness"},
    {"name": "Calories Burned", "route": "calories_burned", "desc": "By workout type", "icon": "🏃", "category": "Fitness"},

    # Sleep & Lifestyle
   {"name": "Sleep Calculator", "route": "sleep", "desc": "Best sleep/wake times", "icon": "🛌", "category": "Sleep & Lifestyle"},
    {"name": "Sleep Debt Calculator", "route": "sleep_debt", "desc": "Track lost sleep", "icon": "⏰", "category": "Sleep & Lifestyle"},
    {"name": "Stress / Relaxation Score", "route": "stress", "desc": "Check stress balance", "icon": "🧘", "category": "Sleep & Lifestyle"},

    # Health Trackers
    {"name": "Blood Pressure Risk", "route": "bp", "desc": "Check BP risk level", "icon": "💓", "category": "Health"},
    {"name": "Diabetes Risk", "route": "diabetes", "desc": "Sugar + lifestyle risk", "icon": "🩸", "category": "Health"},
    {"name": "Alcohol Impact", "route": "alcohol", "desc": "See alcohol effect", "icon": "🍺", "category": "Health"},
]


# -------------------------
# Master Indian Protein Database
# -------------------------
PROTEIN_DB = {
    "Paneer": {"protein": 18, "unit": "per 100g"},
    "Milk": {"protein": 3.4, "unit": "per 100g"},
    "Curd": {"protein": 3.5, "unit": "per 100g"},
    "Buttermilk": {"protein": 2, "unit": "per 100g"},
    "Cheese": {"protein": 25, "unit": "per 100g"},
    "Whey Protein": {"protein": 24, "unit": "per scoop (30g)"},
    "Toor Dal": {"protein": 22, "unit": "per 100g"},
    "Moong Dal": {"protein": 24, "unit": "per 100g"},
    "Chana Dal": {"protein": 21, "unit": "per 100g"},
    "Masoor Dal": {"protein": 19, "unit": "per 100g"},
    "Urad Dal": {"protein": 25, "unit": "per 100g"},
    "Rajma": {"protein": 24, "unit": "per 100g"},
    "Chole": {"protein": 19, "unit": "per 100g"},
    "Soybeans": {"protein": 36, "unit": "per 100g"},
    "Moth Beans": {"protein": 23, "unit": "per 100g"},
    "Horse Gram": {"protein": 22, "unit": "per 100g"},
    "Rice, White": {"protein": 7, "unit": "per 100g"},
    "Brown Rice": {"protein": 8, "unit": "per 100g"},
    "Wheat Flour": {"protein": 12, "unit": "per 100g"},
    "Ragi": {"protein": 7, "unit": "per 100g"},
    "Jowar": {"protein": 10, "unit": "per 100g"},
    "Bajra": {"protein": 11, "unit": "per 100g"},
    "Oats": {"protein": 16, "unit": "per 100g"},
    "Quinoa": {"protein": 14, "unit": "per 100g"},
    "Peanuts": {"protein": 25, "unit": "per 100g"},
    "Almonds": {"protein": 21, "unit": "per 100g"},
    "Cashews": {"protein": 18, "unit": "per 100g"},
    "Walnuts": {"protein": 15, "unit": "per 100g"},
    "Pistachios": {"protein": 20, "unit": "per 100g"},
    "Sunflower Seeds": {"protein": 21, "unit": "per 100g"},
    "Pumpkin Seeds": {"protein": 30, "unit": "per 100g"},
    "Flax Seeds": {"protein": 18, "unit": "per 100g"},
    "Chia Seeds": {"protein": 17, "unit": "per 100g"},
    "Sesame Seeds": {"protein": 18, "unit": "per 100g"},
    "Egg": {"protein": 6, "unit": "per 1 piece"},
    "Chicken Breast": {"protein": 31, "unit": "per 100g"},
    "Chicken Thigh": {"protein": 24, "unit": "per 100g"},
    "Mutton": {"protein": 26, "unit": "per 100g"},
    "Beef": {"protein": 26, "unit": "per 100g"},
    "Fish, Rohu": {"protein": 19, "unit": "per 100g"},
    "Fish, Hilsa": {"protein": 21, "unit": "per 100g"},
    "Fish, Pomfret": {"protein": 20, "unit": "per 100g"},
    "Prawns": {"protein": 24, "unit": "per 100g"}
}

# -------------------------
# Master Sugar Database (per 100g or per unit)
# -------------------------
SUGAR_DB = {
    "Table Sugar": {"sugar": 100, "unit": "per 100g"},
    "Tea Spoon Sugar": {"sugar": 4, "unit": "per tsp (4g)"},
    "Soft Drink (Cola)": {"sugar": 10.6, "unit": "per 100ml"},
    "Fruit Juice (Packaged)": {"sugar": 11, "unit": "per 100ml"},
    "Indian Sweet (Gulab Jamun)": {"sugar": 35, "unit": "per piece (~50g)"},
    "Indian Sweet (Rasgulla)": {"sugar": 30, "unit": "per piece (~40g)"},
    "Chocolate (Milk)": {"sugar": 52, "unit": "per 100g"},
    "Candy": {"sugar": 70, "unit": "per 100g"},
    "Ice Cream": {"sugar": 20, "unit": "per 100g"},
    "Ketchup": {"sugar": 22, "unit": "per 100g"},
    "White Bread": {"sugar": 5, "unit": "per 100g"},
    "Banana": {"sugar": 12, "unit": "per 100g"},
    "Mango": {"sugar": 14, "unit": "per 100g"},
    "Apple": {"sugar": 10, "unit": "per 100g"},
    "Orange": {"sugar": 9, "unit": "per 100g"},
    "Grapes": {"sugar": 16, "unit": "per 100g"},
    "Dates (Khajoor)": {"sugar": 66, "unit": "per 100g"},
    "Honey": {"sugar": 82, "unit": "per 100g"},
}



@app.route('/')
def index():
    categories = sorted(list(set(calc['category'] for calc in CALCULATORS)))
    print("DEBUG categories:", categories)
    print("DEBUG calculators:", len(CALCULATORS))
    return render_template('index.html', calculators=CALCULATORS, categories=categories)


# -------------------------
# Existing routes unchanged
# -------------------------

@app.route("/protein", methods=["GET", "POST"])
def protein_calculator():
    result = None
    if request.method == "POST":
        weight = float(request.form.get("weight", 0))
        goal = request.form.get("goal")
        items = request.form.getlist("item")
        quantities = request.form.getlist("quantity")

        total_protein = 0
        breakdown = []

        for i, item in enumerate(items):
            qty = float(quantities[i]) if quantities[i] else 0
            if item in PROTEIN_DB:
                per_unit = PROTEIN_DB[item]["protein"]
                unit = PROTEIN_DB[item]["unit"]
                protein_amount = (per_unit * qty) / 100 if "100g" in unit or "100ml" in unit else per_unit * qty
                total_protein += protein_amount
                breakdown.append({"item": item, "qty": qty, "protein": round(protein_amount, 2), "unit": unit})

        factor = {"fat-loss": 1.6, "maintenance": 1.8, "muscle-gain": 2.0}
        target = round(weight * factor.get(goal, 1.8), 1)

        result = {
            "total_protein": round(total_protein, 2),
            "target": target,
            "status": "Good" if total_protein >= target else "Low",
            "breakdown": breakdown,
        }

    return render_template("protein.html", foods=PROTEIN_DB, result=result)


@app.route("/api/protein", methods=["POST"])
def protein_api():
    data = request.json
    weight = float(data.get("weight", 0))
    goal = data.get("goal")
    items = data.get("items", [])

    total_protein = 0
    breakdown = []

    for entry in items:
        item = entry["item"]
        qty = float(entry["quantity"])
        if item in PROTEIN_DB:
            per_unit = PROTEIN_DB[item]["protein"]
            unit = PROTEIN_DB[item]["unit"]
            protein_amount = (per_unit * qty) / 100 if "100g" in unit or "100ml" in unit else per_unit * qty
            total_protein += protein_amount
            breakdown.append({"item": item, "qty": qty, "protein": round(protein_amount, 2), "unit": unit})

    factor = {"fat-loss": 1.6, "maintenance": 1.8, "muscle-gain": 2.0}
    target = round(weight * factor.get(goal, 1.8), 1)

    return jsonify({
        "total_protein": round(total_protein, 2),
        "target": target,
        "status": "Good" if total_protein >= target else "Low",
        "breakdown": breakdown,
    })


# (BMI, Sleep, Sugar routes remain same as you pasted…)

# --- TDEE / Daily Calorie Calculator ---
@app.route("/tdee", methods=["GET", "POST"])
def tdee():
    result = None
    if request.method == "POST":
        try:
            weight = float(request.form.get("weight", 0))
            height = float(request.form.get("height", 0))
            age = int(request.form.get("age", 0))
            gender = request.form.get("gender")
            activity = request.form.get("activity")

            # Mifflin-St Jeor Equation (BMR)
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            # Activity multipliers
            factors = {
                "sedentary": 1.2,
                "light": 1.375,
                "moderate": 1.55,
                "active": 1.725,
                "very_active": 1.9
            }
            tdee_val = round(bmr * factors.get(activity, 1.2), 0)

            result = {
                "bmr": round(bmr, 1),
                "tdee": tdee_val,
                "activity": activity.replace("_", " ").title()
            }
        except Exception as e:
            result = {"error": str(e)}

    return render_template("tdee.html", result=result, calc={"name": "TDEE Calculator", "icon": "🔥"})


# --- Macro Split Calculator ---
@app.route("/macro", methods=["GET", "POST"])
def macro():
    result = None
    if request.method == "POST":
        try:
            # Inputs
            age = int(request.form.get("age", 0))
            gender = request.form.get("gender")
            height = float(request.form.get("height", 0))
            weight = float(request.form.get("weight", 0))
            activity = request.form.get("activity")
            goal = request.form.get("goal")

            # --- Step 1: BMR (Mifflin-St Jeor) ---
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            # --- Step 2: Activity multipliers ---
            activity_factors = {
                "sedentary": 1.2,
                "light": 1.375,
                "moderate": 1.55,
                "active": 1.725,
                "very_active": 1.9,
            }
            tdee = bmr * activity_factors.get(activity, 1.2)

            # --- Step 3: Goal adjustment ---
            if goal == "cut":
                calories = tdee - 500
            elif goal == "bulk":
                calories = tdee + 300
            else:  # maintain
                calories = tdee

            # --- Step 4: Macro split (25/50/25) ---
            split = {"protein": 0.25, "carbs": 0.50, "fat": 0.25}

            protein_g = round((calories * split["protein"]) / 4, 1)
            carbs_g = round((calories * split["carbs"]) / 4, 1)
            fat_g = round((calories * split["fat"]) / 9, 1)

            result = {
                "calories": round(calories),
                "protein": protein_g,
                "carbs": carbs_g,
                "fat": fat_g,
                "protein_pct": int(split["protein"] * 100),
                "carbs_pct": int(split["carbs"] * 100),
                "fat_pct": int(split["fat"] * 100),
            }
        except Exception as e:
            result = {"error": str(e)}

    return render_template("macro.html", result=result, calc={"name": "Macro Split", "icon": "🥗"})


# --- Water Intake Calculator ---
@app.route("/water", methods=["GET", "POST"])
def water():
    result = None
    if request.method == "POST":
        try:
            weight = float(request.form.get("weight", 0))
            activity = request.form.get("activity")
            climate = request.form.get("climate")
            coffee = int(request.form.get("coffee", 0))
            alcohol = int(request.form.get("alcohol", 0))

            # --- Base requirement (ml per kg) ---
            activity_factor = {"low": 30, "moderate": 35, "high": 40}
            water_ml = weight * activity_factor.get(activity, 35)

            # --- Climate adjustment ---
            if climate == "hot":
                water_ml += 500
            elif climate == "cool":
                water_ml -= 250

            # --- Coffee & alcohol adjustment ---
            water_ml += coffee * 100   # +100 ml per cup coffee
            water_ml += alcohol * 150  # +150 ml per drink

            # Final liters
            liters = round(water_ml / 1000, 2)

            # --- Advice ---
            if liters < 2:
                advice = "Hydration is on the lower side. Ensure at least 2 L daily."
            elif 2 <= liters <= 3.5:
                advice = "Good hydration target. Spread intake evenly throughout the day."
            else:
                advice = "High hydration need — make sure to drink frequently, especially around workouts."

            # Suggested distribution
            distribution = [
                ("Morning", round(liters * 0.25, 2)),
                ("Midday", round(liters * 0.35, 2)),
                ("Evening", round(liters * 0.25, 2)),
                ("Workout", round(liters * 0.15, 2)),
            ]

            result = {
                "liters": liters,
                "recommendation": f"{liters} L per day",
                "advice": advice,
                "distribution": distribution,
                "activity": activity,
                "climate": climate,
                "coffee": coffee,
                "alcohol": alcohol,
            }
        except Exception as e:
            result = {"error": str(e)}

    return render_template("water.html", result=result, calc={"name": "Water Intake", "icon": "💧"})

# --- Sugar Calculator ---
@app.route("/sugar", methods=["GET", "POST"])
def sugar():
    result = None
    if request.method == "POST":
        try:
            age = int(request.form.get("age", 0))
            gender = request.form.get("gender")
            weight = float(request.form.get("weight", 0))

            items = request.form.getlist("item")
            quantities = request.form.getlist("quantity")

            total_sugar = 0
            breakdown = []

            for i, item in enumerate(items):
                qty_str = quantities[i] if i < len(quantities) else "0"
                try:
                    qty = float(qty_str) if qty_str else 0
                except ValueError:
                    qty = 0

                if item in SUGAR_DB and qty > 0:
                    per_unit = SUGAR_DB[item]["sugar"]
                    unit = SUGAR_DB[item]["unit"]
                    if "100g" in unit or "100ml" in unit:
                        sugar_amount = (per_unit * qty) / 100
                    else:
                        sugar_amount = per_unit * qty

                    total_sugar += sugar_amount
                    breakdown.append({
                        "item": item,
                        "qty": qty,
                        "sugar": round(sugar_amount, 2),
                        "unit": unit
                    })

            # --- WHO guideline ---
            daily_calories = max(weight * 30, 1500)  # avoid division by zero
            max_safe = round((0.05 * daily_calories) / 4, 1)
            max_limit = round((0.10 * daily_calories) / 4, 1)

            if total_sugar <= max_safe:
                status = "✅ Safe"
                advice = "Excellent — within WHO ideal limit (<5% of daily calories)."
            elif total_sugar <= max_limit:
                status = "⚠️ Moderate"
                advice = "Within 10% safe upper limit. Try cutting down a little."
            else:
                status = "❌ High Risk"
                advice = "Too much sugar — linked with obesity, diabetes, and heart risk."

            sugar_pct = round((total_sugar * 4 / daily_calories) * 100, 1)

            result = {
                "total_sugar": round(total_sugar, 1),
                "max_safe": max_safe,
                "max_limit": max_limit,
                "sugar_pct": sugar_pct,
                "status": status,
                "advice": advice,
                "breakdown": breakdown,
            }
        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("sugar.html", foods=SUGAR_DB, result=result, calc={"name": "Sugar Intake", "icon": "🍬"})


# --- BMI Calculator with dynamic scale ---
@app.route("/bmi", methods=["GET", "POST"])
def bmi():
    result = None
    if request.method == "POST":
        try:
            weight = float(request.form.get("weight", 0))
            unit = request.form.get("unit", "cm")
            gender = request.form.get("gender")

            # Height
            if unit == "imperial":
                ft = float(request.form.get("height_ft", 0) or 0)
                inch = float(request.form.get("height_in", 0) or 0)
                height_cm = round((ft * 12 + inch) * 2.54, 2)
            else:
                height_cm = float(request.form.get("height_cm", 0) or 0)

            height_m = height_cm / 100.0

            # --- BMI calc ---
            bmi_val = round(weight / (height_m ** 2), 1) if height_m > 0 else 0

            # --- Category (WHO) ---
            if bmi_val < 18.5:
                category = "Underweight"
                advice = "You may need to gain some weight for health."
            elif bmi_val < 25:
                category = "Normal"
                advice = "Good job! Maintain your lifestyle."
            elif bmi_val < 30:
                category = "Overweight"
                advice = "Consider balanced diet & exercise."
            else:
                category = "Obese"
                advice = "High risk — take action with structured plan."

            # --- Dynamic scale thresholds ---
            min_bmi, max_bmi = 15, 40
            thresholds = [18.5, 24.9, 29.9, max_bmi]

            denom = max_bmi - min_bmi
            segs = []
            last = min_bmi
            for t in thresholds:
                width = max(0, ((t - last) / denom) * 100)
                segs.append(round(width, 2))
                last = t

            # pointer position
            pointer_pct = ((bmi_val - min_bmi) / denom) * 100
            pointer_pct = max(0, min(100, round(pointer_pct, 2)))

            result = {
                "bmi": bmi_val,
                "category": category,
                "advice": advice,
                "scale": {
                    "segments": segs,  # [under, normal, overweight, obese]
                    "pointer_pct": pointer_pct,
                    "min_bmi": min_bmi,
                    "thresholds": thresholds,
                }
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("bmi.html", result=result, calc={"name": "BMI Calculator", "icon": "⚖️"})

# --- Body Fat % Estimator (with dynamic scale) ---
@app.route("/bodyfat", methods=["GET", "POST"])
def bodyfat():
    result = None
    if request.method == "POST":
        try:
            # Inputs
            age = int(request.form.get("age", 0))
            gender = request.form.get("gender")
            weight = float(request.form.get("weight", 0))
            unit = request.form.get("unit", "cm")

            # --- Height ---
            if unit == "imperial":
                ft = float(request.form.get("height_ft", 0) or 0)
                inch = float(request.form.get("height_in", 0) or 0)
                height_cm = round((ft * 12 + inch) * 2.54, 2)
            else:
                height_cm = float(request.form.get("height_cm", 0) or 0)

            height_m = height_cm / 100.0 if height_cm > 0 else 0

            # --- Circumferences ---
            if unit == "imperial":
                waist = float(request.form.get("waist_in", 0) or 0) * 2.54 if request.form.get("waist_in") else None
                neck = float(request.form.get("neck_in", 0) or 0) * 2.54 if request.form.get("neck_in") else None
                hip = float(request.form.get("hip_in", 0) or 0) * 2.54 if request.form.get("hip_in") else None
            else:
                waist = float(request.form.get("waist_cm", 0) or 0) if request.form.get("waist_cm") else None
                neck = float(request.form.get("neck_cm", 0) or 0) if request.form.get("neck_cm") else None
                hip = float(request.form.get("hip_cm", 0) or 0) if request.form.get("hip_cm") else None

            # --- Method 1: BMI-based (Deurenberg) ---
            if height_m > 0:
                bmi = weight / (height_m ** 2)
            else:
                bmi = 0
            sex = 1 if gender == "male" else 0
            bf_bmi = round((1.20 * bmi) + (0.23 * age) - (10.8 * sex) - 5.4, 1)

            # --- Method 2: US Navy (if circumferences available) ---
            bf_navy = None
            if waist and neck and (gender == "male" or (gender == "female" and hip)):
                import math
                if gender == "male":
                    bf_navy = 495 / (
                        1.0324 - 0.19077 * math.log10(waist - neck) +
                        0.15456 * math.log10(height_cm)
                    ) - 450
                else:
                    bf_navy = 495 / (
                        1.29579 - 0.35004 * math.log10(waist + hip - neck) +
                        0.22100 * math.log10(height_cm)
                    ) - 450
                bf_navy = round(bf_navy, 1)

            # --- Final value ---
            bf_final = bf_navy if bf_navy else bf_bmi

            # --- Category (ACE Guidelines) ---
            if gender == "male":
                if bf_final < 6:
                    category, advice = "Essential Fat", "Too low, may affect hormones."
                elif bf_final <= 13:
                    category, advice = "Athlete", "Excellent shape, maintain performance diet."
                elif bf_final <= 17:
                    category, advice = "Fitness", "Very good range for health and looks."
                elif bf_final <= 24:
                    category, advice = "Average", "Healthy, but can be improved."
                else:
                    category, advice = "Obese", "High risk, reduce fat with diet & exercise."
            else:  # female
                if bf_final < 14:
                    category, advice = "Essential Fat", "Too low, may affect hormones."
                elif bf_final <= 20:
                    category, advice = "Athlete", "Excellent shape, maintain performance diet."
                elif bf_final <= 24:
                    category, advice = "Fitness", "Very good range for health and looks."
                elif bf_final <= 31:
                    category, advice = "Average", "Healthy, but can be improved."
                else:
                    category, advice = "Obese", "High risk, reduce fat with diet & exercise."

            # --- Lean & Fat Mass ---
            fat_mass = round(weight * bf_final / 100, 1)
            lean_mass = round(weight - fat_mass, 1)

            # --- Dynamic Scale Setup ---
            min_bf, max_bf = 5, 50
            if gender == "male":
                thresholds = [6, 13, 17, 24, max_bf]
            else:
                thresholds = [14, 20, 24, 31, max_bf]

            denom = max_bf - min_bf
            segs, last = [], min_bf
            for t in thresholds:
                segs.append(round(((t - last) / denom) * 100, 2))
                last = t

            pointer_pct = ((bf_final - min_bf) / denom) * 100
            pointer_pct = max(0, min(100, round(pointer_pct, 2)))

            result = {
                "bf_bmi": bf_bmi,
                "bf_navy": bf_navy,
                "bf_final": bf_final,
                "category": category,
                "advice": advice,
                "fat_mass": fat_mass,
                "lean_mass": lean_mass,
                "scale": {
                    "segments": segs,
                    "pointer_pct": pointer_pct,
                    "min_bf": min_bf,
                    "thresholds": thresholds
                }
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("bodyfat.html", result=result, calc={"name": "Body Fat % Estimator", "icon": "📉"})


# --- Advanced Ideal Weight Calculator (fixed dynamic scale) ---
@app.route("/ideal_weight", methods=["GET", "POST"])
def ideal_weight():
    result = None
    if request.method == "POST":
        try:
            gender = request.form.get("gender")
            unit = request.form.get("unit", "cm")

            # --- Height handling ---
            if unit == "imperial":
                ft = float(request.form.get("height_ft", 0) or 0)
                inch = float(request.form.get("height_in", 0) or 0)
                height_cm = round((ft * 12 + inch) * 2.54, 2)
            else:
                height_cm = float(request.form.get("height_cm", 0) or 0)

            height_m = height_cm / 100.0
            height_in = height_cm / 2.54

            # Optional current weight (for pointer & advice)
            weight = float(request.form.get("weight", 0)) if request.form.get("weight") else None

            # --- WHO BMI-based healthy range (18.5 - 24.9) ---
            min_weight = round(18.5 * (height_m ** 2), 1)
            max_weight = round(24.9 * (height_m ** 2), 1)

            # --- Classic formulas ---
            if gender == "male":
                devine = 50 + 2.3 * (height_in - 60)
                hamwi = 48.0 + 2.7 * (height_in - 60)
                miller = 56.2 + 1.41 * (height_in - 60)
                robinson = 52 + 1.9 * (height_in - 60)
            else:
                devine = 45.5 + 2.3 * (height_in - 60)
                hamwi = 45.5 + 2.2 * (height_in - 60)
                miller = 53.1 + 1.36 * (height_in - 60)
                robinson = 49 + 1.7 * (height_in - 60)

            formulas = {
                "Devine": round(devine, 1),
                "Hamwi": round(hamwi, 1),
                "Miller": round(miller, 1),
                "Robinson": round(robinson, 1),
            }

            # --- Dynamic display range for the scale ---
            # Use a display BMI range e.g. 15 -> 40 so the scale shows reasonable spread
            min_display_bmi = 15.0
            max_display_bmi = 40.0

            min_display_weight = min_display_bmi * (height_m ** 2)
            max_display_weight = max_display_bmi * (height_m ** 2)

            # Threshold weights at key BMI breakpoints
            w_under_end = 18.5 * (height_m ** 2)    # end of underweight
            w_normal_end = 24.9 * (height_m ** 2)   # end of normal
            w_over_end = 29.9 * (height_m ** 2)     # end of overweight
            w_max_display = max_display_weight

            denom = max_display_weight - min_display_weight
            if denom <= 0:
                denom = 1e-6

            # Segment widths (%) for bar
            seg_under = max(0.0, ((w_under_end - min_display_weight) / denom) * 100)
            seg_normal = max(0.0, ((w_normal_end - w_under_end) / denom) * 100)
            seg_over = max(0.0, ((w_over_end - w_normal_end) / denom) * 100)
            seg_obese = max(0.0, ((w_max_display - w_over_end) / denom) * 100)

            # ensure they sum to ~100 (minor float correction)
            total = seg_under + seg_normal + seg_over + seg_obese
            if total > 0:
                factor = 100.0 / total
                seg_under *= factor
                seg_normal *= factor
                seg_over *= factor
                seg_obese *= factor

            # Pointer (percentage position of current weight across display range)
            pointer_pct = None
            if weight is not None:
                pointer_pct = ((weight - min_display_weight) / denom) * 100
                # clamp to 0..100
                if pointer_pct < 0:
                    pointer_pct = 0.0
                if pointer_pct > 100:
                    pointer_pct = 100.0
                pointer_pct = round(pointer_pct, 2)

            # Advice if current weight is given
            advice = None
            if weight:
                if weight < min_weight:
                    advice = f"Your weight {weight} kg is below the WHO healthy range ({min_weight}–{max_weight} kg). Consider gaining weight safely."
                elif weight > max_weight:
                    advice = f"Your weight {weight} kg is above the WHO healthy range ({min_weight}–{max_weight} kg). Consider a structured plan to reduce."
                else:
                    advice = f"Your weight {weight} kg is within the WHO healthy range ({min_weight}–{max_weight} kg). Maintain with balanced diet and exercise."

            result = {
                "height_cm": height_cm,
                "min_weight": round(min_weight, 1),
                "max_weight": round(max_weight, 1),
                "formulas": formulas,
                "advice": advice,
                "current_weight": weight,
                "scale": {
                    "min_display_weight": round(min_display_weight, 1),
                    "w_under_end": round(w_under_end, 1),
                    "w_normal_end": round(w_normal_end, 1),
                    "w_over_end": round(w_over_end, 1),
                    "max_display_weight": round(max_display_weight, 1),
                    "seg_under": round(seg_under, 2),
                    "seg_normal": round(seg_normal, 2),
                    "seg_over": round(seg_over, 2),
                    "seg_obese": round(seg_obese, 2),
                    "pointer_pct": pointer_pct,
                }
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("ideal_weight.html", result=result, calc={"name": "Ideal Weight", "icon": "📏"})


# --- Calories Burned Calculator (Pro) ---
@app.route("/calories_burned", methods=["GET", "POST"])
def calories_burned():
    result = None
    METS = {
        "Running (6 mph / 10 km/h)": 9.8,
        "Running (8 mph / 12.8 km/h)": 11.8,
        "Cycling (moderate)": 7.5,
        "Cycling (vigorous)": 10,
        "Swimming (moderate)": 6,
        "Swimming (vigorous)": 9.5,
        "Walking (4 km/h)": 3.5,
        "Walking (6 km/h)": 4.8,
        "Yoga": 2.5,
        "HIIT / CrossFit": 8,
        "Weight Training": 6,
        "Dancing": 5.5,
    }

    if request.method == "POST":
        try:
            weight = float(request.form.get("weight", 0))
            duration = float(request.form.get("duration", 0))
            exercise = request.form.get("exercise")

            met = METS.get(exercise, 6)  # default fallback
            calories = round((met * 3.5 * weight / 200) * duration, 1)
            cal_per_min = round(calories / duration, 1) if duration > 0 else 0

            # Fun equivalents
            food_eq = []
            if calories > 0:
                food_eq.append(f"{round(calories/285,1)} 🍕 slices (285 kcal each)")
                food_eq.append(f"{round(calories/250,1)} 🍫 bars (250 kcal each)")
                food_eq.append(f"{round(calories/150,1)} 🍺 beers (150 kcal each)")

            # Dynamic scale
            min_cal, max_cal = 0, 1000
            milestones = [200, 500, 1000]
            pointer_pct = (calories - min_cal) / (max_cal - min_cal) * 100
            pointer_pct = max(0, min(100, round(pointer_pct, 2)))

            result = {
                "exercise": exercise,
                "calories": calories,
                "cal_per_min": cal_per_min,
                "food_eq": food_eq,
                "scale": {
                    "pointer_pct": pointer_pct,
                    "milestones": milestones,
                    "max_cal": max_cal
                }
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("calories_burned.html", result=result, calc={"name": "Calories Burned", "icon": "🔥"}, mets=METS)


# --- Stress / Relaxation Score Calculator ---
@app.route("/stress", methods=["GET", "POST"])
def stress():
    result = None
    if request.method == "POST":
        try:
            # Stress inputs
            work = int(request.form.get("work", 0))
            sleep = int(request.form.get("sleep", 0))
            screen = int(request.form.get("screen", 0))

            # Relaxation inputs
            exercise = int(request.form.get("exercise", 0))
            meditation = int(request.form.get("meditation", 0))
            social = int(request.form.get("social", 0))

            # Calculate stress load and relaxation recovery
            stress_total = work + screen + (10 - sleep)   # higher sleep = less stress
            relax_total = exercise + meditation + social

            # Normalize (scale 0–100)
            score = max(0, min(100, 100 - (stress_total * 5) + (relax_total * 3)))

            if score >= 80:
                advice = "Great balance 🟢 — keep up your routine!"
            elif score >= 60:
                advice = "Manageable 🟡 — focus on better relaxation."
            else:
                advice = "High Stress 🔴 — consider lifestyle adjustments."

            result = {
                "score": score,
                "stress_total": stress_total,
                "relax_total": relax_total,
                "advice": advice
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("stress.html", result=result, calc={"name": "Stress Balance", "icon": "🧘"})


# --- Blood Pressure Risk Calculator (Dual Gauges) ---
@app.route("/bp", methods=["GET", "POST"])
def bp():
    result = None
    if request.method == "POST":
        try:
            systolic = int(request.form.get("systolic", 0))
            diastolic = int(request.form.get("diastolic", 0))
            age = int(request.form.get("age", 0)) if request.form.get("age") else None
            history = request.form.get("history", "no")

            # Helper classification functions
            def classify_systolic(s):
                if s >= 180: return "Hypertensive Crisis"
                if s >= 140: return "High BP Stage 2"
                if s >= 130: return "High BP Stage 1"
                if s >= 120: return "Elevated"
                if s < 90:    return "Hypotension"
                return "Normal"

            def classify_diastolic(d):
                if d >= 120: return "Hypertensive Crisis"
                if d >= 90:  return "High BP Stage 2"
                if d >= 80:  return "High BP Stage 1"
                if d < 60:   return "Hypotension"
                return "Normal"

            sys_cat = classify_systolic(systolic)
            dia_cat = classify_diastolic(diastolic)

            # Final category = worst of systolic/diastolic
            order = ["Hypertensive Crisis", "High BP Stage 2", "High BP Stage 1", "Elevated", "Normal", "Hypotension"]
            worst = min(order.index(sys_cat), order.index(dia_cat))
            final_cat = order[worst]

            # Advice
            if final_cat == "Hypertensive Crisis":
                advice = "Hypertensive crisis — seek immediate medical attention!"
            elif final_cat == "High BP Stage 2":
                advice = "High BP Stage 2 — consult a doctor; risk of complications."
            elif final_cat == "High BP Stage 1":
                advice = "High BP Stage 1 — monitor regularly & adopt a low-salt, active lifestyle."
            elif final_cat == "Elevated":
                advice = "Elevated BP — lifestyle improvements (diet, exercise) recommended."
            elif final_cat == "Hypotension":
                advice = "Low BP detected — if symptomatic (dizziness, fainting), consult a doctor."
            else:
                advice = "Normal — maintain healthy habits."

            if age and age > 50:
                advice += " (Over 50 — regular checkups recommended.)"
            if history == "yes":
                advice += " Family history increases risk — stay proactive."

            result = {
                "systolic": systolic,
                "diastolic": diastolic,
                "sys_cat": sys_cat,
                "dia_cat": dia_cat,
                "category": final_cat,
                "advice": advice
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("bp.html", result=result, calc={"name": "Blood Pressure Risk", "icon": "💓"})


# --- Diabetes Risk Calculator (with Lifestyle Tips) ---
@app.route("/diabetes", methods=["GET", "POST"])
def diabetes():
    result = None
    if request.method == "POST":
        try:
            fasting = float(request.form.get("fasting", 0))
            postmeal = float(request.form.get("postmeal", 0))
            age = int(request.form.get("age", 0)) if request.form.get("age") else None
            bmi = float(request.form.get("bmi", 0)) if request.form.get("bmi") else None
            family = request.form.get("family", "no")
            activity = request.form.get("activity", "sedentary")
            diet = request.form.get("diet", "balanced")

            # --- Risk Scoring ---
            score = 0
            category = "Normal"

            if fasting >= 126: score += 40
            elif fasting >= 100: score += 20

            if postmeal >= 200: score += 40
            elif postmeal >= 140: score += 20

            if age and age >= 45: score += 10
            if bmi and bmi >= 25: score += 10
            if family == "yes": score += 10
            if activity == "sedentary": score += 10
            if diet == "high_sugar": score += 10

            # --- Category & Advice ---
            if score >= 70:
                category = "High Risk (Possible Diabetes)"
                advice = "High diabetes risk — consult a doctor for blood tests and adopt strict lifestyle changes."
                tips = [
                    "Adopt a low-carb, high-fiber diet (vegetables, legumes, whole grains).",
                    "Avoid sugary drinks and processed foods.",
                    "Exercise at least 30 minutes daily (walking, jogging, yoga).",
                    "Get regular HbA1c and blood sugar tests.",
                    "Maintain a healthy sleep schedule (7–8 hrs)."
                ]
            elif score >= 40:
                category = "Prediabetes Risk"
                advice = "Prediabetes risk — improve diet, increase activity, and monitor regularly."
                tips = [
                    "Reduce portion sizes and refined carbs.",
                    "Include 20–30 min of brisk walking most days.",
                    "Cut down on late-night snacking.",
                    "Track weight and waist circumference.",
                    "Increase water intake and avoid excess alcohol."
                ]
            else:
                category = "Normal"
                advice = "Normal range — maintain healthy habits."
                tips = [
                    "Continue balanced meals with fruits & veggies.",
                    "Exercise at least 3–4 times a week.",
                    "Limit fried/junk food to occasional treats.",
                    "Get annual blood sugar screening.",
                    "Stay hydrated and stress-free."
                ]

            if age and age > 50:
                advice += " (Age above 50: regular annual screening recommended.)"

            result = {
                "fasting": fasting,
                "postmeal": postmeal,
                "age": age,
                "bmi": bmi,
                "score": score,
                "category": category,
                "advice": advice,
                "tips": tips
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("diabetes.html", result=result, calc={"name": "Diabetes Risk", "icon": "🩸"})



# --- Sleep Calculator ---
from datetime import datetime, timedelta

@app.route("/sleep", methods=["GET", "POST"])
def sleep():
    result = None
    if request.method == "POST":
        try:
            bedtime = request.form.get("bedtime")
            wakeup = request.form.get("wakeup")

            sleep_cycles = 90  # minutes
            fall_asleep_buffer = 15
            suggestions = []
            advice = ""

            if bedtime and not wakeup:
                bt = datetime.strptime(bedtime, "%H:%M")
                for cycles in range(3, 7):  # 4.5–9 hrs
                    wake = bt + timedelta(minutes=fall_asleep_buffer + cycles * sleep_cycles)
                    suggestions.append(wake.strftime("%I:%M %p"))
                advice = "Aim for 5–6 cycles (~7.5–9 hrs). Pick a wake time that fits your lifestyle."
                result = {"mode": "bedtime", "bedtime": bedtime, "suggestions": suggestions, "advice": advice}

            elif wakeup and not bedtime:
                wu = datetime.strptime(wakeup, "%H:%M")
                for cycles in range(6, 2, -1):
                    bed = wu - timedelta(minutes=fall_asleep_buffer + cycles * sleep_cycles)
                    suggestions.append(bed.strftime("%I:%M %p"))
                advice = "Going to bed at these times ensures you complete healthy sleep cycles."
                result = {"mode": "wakeup", "wakeup": wakeup, "suggestions": suggestions, "advice": advice}

            elif bedtime and wakeup:
                bt = datetime.strptime(bedtime, "%H:%M")
                wu = datetime.strptime(wakeup, "%H:%M")
                if wu < bt:
                    wu += timedelta(days=1)  # handle overnight
                duration = (wu - bt).total_seconds() / 3600
                cycles = round(duration * 60 / sleep_cycles, 1)

                # Advice based on duration
                if duration < 6:
                    advice = "❌ Too short — linked with fatigue, poor focus, and health risk."
                elif 6 <= duration < 7.5:
                    advice = "⚠️ Slightly short — try extending to 7.5 hrs for full recovery."
                elif 7.5 <= duration <= 9:
                    advice = "✅ Optimal — excellent range for health and performance."
                else:
                    advice = "⚠️ Oversleeping — too much sleep may signal fatigue or imbalance."

                # For gauge scale (target = 8 hrs)
                min_hr, max_hr, target_hr = 4, 12, 8
                pointer_pct = (duration - min_hr) / (max_hr - min_hr) * 100
                pointer_pct = max(0, min(100, round(pointer_pct, 2)))

                result = {
                    "mode": "both",
                    "bedtime": bedtime,
                    "wakeup": wakeup,
                    "duration": round(duration, 2),
                    "cycles": cycles,
                    "advice": advice,
                    "scale": {
                        "min_hr": min_hr,
                        "max_hr": max_hr,
                        "target_hr": target_hr,
                        "pointer_pct": pointer_pct,
                    }
                }
            else:
                result = {"error": "Please provide at least bedtime or wake-up time."}

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("sleep.html", result=result, calc={"name": "Sleep Calculator", "icon": "🛌"})


# --- Sleep Debt Calculator ---
@app.route("/sleep_debt", methods=["GET", "POST"])
def sleep_debt():
    result = None
    if request.method == "POST":
        try:
            avg = float(request.form.get("avg", 0))
            age = int(request.form.get("age", 0))
            days = int(request.form.get("days", 7))

            # Ideal sleep based on NSF guidelines
            if age < 14:
                ideal = 9
            elif age <= 17:
                ideal = 8.5
            elif age <= 64:
                ideal = 8
            else:
                ideal = 7.5

            debt_per_day = ideal - avg
            total_debt = round(debt_per_day * days, 1)

            if total_debt <= 0:
                advice = "✅ No sleep debt — you’re meeting or exceeding your ideal sleep."
            elif total_debt <= 5:
                advice = "⚠️ Mild sleep debt — try going to bed earlier or adding naps."
            elif total_debt <= 14:
                advice = "❌ Moderate debt — recovery sleep needed. Aim for a few nights of 8–9 hrs."
            else:
                advice = "🚨 Severe debt — linked to major fatigue, mood issues, and health risks."

            # Scale for UI
            thresholds = [5, 14, 21]
            max_debt = 28
            pointer_pct = (total_debt / max_debt) * 100
            pointer_pct = max(0, min(100, round(pointer_pct, 1)))

            result = {
                "avg": avg,
                "ideal": ideal,
                "days": days,
                "total_debt": total_debt,
                "advice": advice,
                "scale": {
                    "pointer_pct": pointer_pct,
                    "thresholds": thresholds,
                    "max_debt": max_debt,
                }
            }

        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("sleep_debt.html", result=result, calc={"name": "Sleep Debt", "icon": "⏰"})





# --- Alcohol Impact Calculator ---
@app.route("/alcohol", methods=["GET", "POST"])
def alcohol():
    result = None
    if request.method == "POST":
        try:
            drinks = int(request.form.get("drinks", 0))  # drinks per week
            gender = request.form.get("gender", "male")
            weight = float(request.form.get("weight", 0)) if request.form.get("weight") else None
            pattern = request.form.get("pattern", "spread")

            # --- Safe Limits (WHO/CDC) ---
            safe_limit = 14 if gender == "male" else 7  # drinks/week
            ethanol_per_drink = 14  # grams pure alcohol
            total_ethanol = drinks * ethanol_per_drink
            safe_ethanol = safe_limit * ethanol_per_drink

            # Risk score for gauge
            if drinks == 0:
                score = 0
            else:
                score = min(100, round((drinks / (safe_limit * 2)) * 100))

            # Comparison %
            compare_pct = min(200, round((total_ethanol / safe_ethanol) * 100)) if safe_ethanol > 0 else 0

            # Category + Advice
            if drinks <= safe_limit:
                category = "Low Risk"
                advice = "Within safe limits — maintain moderation."
                tips = [
                    "Keep alcohol-free days during the week.",
                    "Stay hydrated and avoid drinking on an empty stomach.",
                    "Continue moderate, social drinking only."
                ]
            elif drinks <= safe_limit * 2:
                category = "Moderate Risk"
                advice = "Above recommended weekly limit — cut back gradually."
                tips = [
                    "Replace alcohol with non-alcoholic alternatives sometimes.",
                    "Avoid binge drinking — spread consumption over the week.",
                    "Include liver-friendly foods (leafy greens, fruits, nuts)."
                ]
            else:
                category = "High Risk"
                advice = "High alcohol intake — risk of liver, heart & sleep issues. Strongly advised to reduce."
                tips = [
                    "Seek medical advice if finding it difficult to cut down.",
                    "Join support groups or track consumption with an app.",
                    "Avoid alcohol before sleep — improves rest & recovery.",
                    "Focus on exercise, hydration, and balanced diet."
                ]

            result = {
                "drinks": drinks,
                "gender": gender.title(),
                "weight": weight,
                "pattern": pattern,
                "category": category,
                "advice": advice,
                "tips": tips,
                "score": score,
                "safe_limit": safe_limit,
                "ethanol": total_ethanol,
                "safe_ethanol": safe_ethanol,
                "compare_pct": compare_pct
            }
            if result["pattern"] == "binge" and result["category"] == "Low Risk":
             result["advice"] = "Your weekly intake is within safe limits, but binge drinking is harmful. Spread drinks across the week."
             result["tips"].insert(0, "Avoid binge sessions — spread your drinks across multiple days.")


        except Exception as e:
            result = {"error": f"Calculation failed: {e}"}

    return render_template("alcohol.html", result=result, calc={"name": "Alcohol Impact", "icon": "🍺"})


@app.route("/<tool>")
def placeholder(tool):
    # Find calculator by route
    calc = next((c for c in CALCULATORS if c["route"] == tool), None)
    if not calc:
        return "Calculator not found", 404

    return render_template("placeholder.html", calc=calc)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
