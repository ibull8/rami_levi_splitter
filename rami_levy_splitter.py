import streamlit as st

# הגדרות כלליות
# המשתנה הזה מאפשר לשנות את שם המטבע בקלות
CURRENCY = "₪"

def calculate_debt(total_receipt_cost, discount_rate, payer_name, specific_costs):
    """
    מבצע את חישוב החובות לפי הנחת השובר וחלוקה משותפת (50/50 לאילן ומירה).

    :param total_receipt_cost: העלות הכוללת של הקנייה בקבלה (לפני הנחה).
    :param discount_rate: שיעור הנחת השובר (למשל, 0.055 עבור 5.5%).
    :param payer_name: שם האדם ששילם בפועל (מחזיק השוברים).
    :param specific_costs: מילון של עלויות ספציפיות לכל משתתף (לפני הנחה).
    :return: מילון המכיל את חוב ההחזר הסופי של כל משתתף לקרדיטור (המשלם).
    """

    # 1. חישוב מכפיל העלות האמיתי (לאחר הנחה)
    cost_multiplier = 1 - discount_rate
    
    # 2. החוב האמיתי הכולל שיש להחזיר לקרדיטור (יעקב בדוגמה הקודמת)
    total_actual_debt = total_receipt_cost * cost_multiplier

    # 3. חישוב עלות הפריטים הספציפיים לאחר הנחה וקיזוזם
    specific_debt_total = 0
    discounted_specific_debts = {}
    
    for name, cost in specific_costs.items():
        # מחשב את החוב הספציפי בפועל לאחר הנחה
        actual_specific_cost = cost * cost_multiplier
        discounted_specific_debts[name] = actual_specific_cost
        specific_debt_total += actual_specific_cost
        
    # 4. חישוב החוב המשותף (מה שנשאר לחלוקה בין אילן ומירה)
    net_shared_debt = total_actual_debt - specific_debt_total
    
    # אם החישוב תקין, החוב המשותף לא אמור להיות שלילי, אבל נטפל במקרה גבולי
    if net_shared_debt < 0:
        st.error("שגיאה בחישוב: סכום הפריטים הספציפיים גבוה מהעלות הכוללת של הקבלה!")
        return {}

    # 5. חלוקה שווה של החוב המשותף בין אילן ומירה (50/50)
    shared_debt_per_person = net_shared_debt / 2
    
    # 6. סיכום החובות הסופיים להחזר לקרדיטור (המשלם)
    final_debts_to_payer = {}
    
    # חוב אילן = עלות ספציפית (מוזלת) + חצי מהחוב המשותף
    ilan_debt = discounted_specific_debts.get("אילן", 0) + shared_debt_per_person
    
    # חוב מירה = עלות ספציפית (מוזלת) + חצי מהחוב המשותף
    mira_debt = discounted_specific_debts.get("מירה", 0) + shared_debt_per_person
    
    # החוב של שאר המשתתפים הוא רק העלות הספציפית שלהם
    yaakov_debt = discounted_specific_debts.get("יעקב", 0)
    parents_debt = discounted_specific_debts.get("הורים", 0)

    final_debts_to_payer = {
        "אילן": ilan_debt,
        "מירה": mira_debt,
        "יעקב": yaakov_debt,
        "הורים": parents_debt
    }

    # 7. חישוב מיוחד עבור הזינוק ל-Splitwise (מירה לאילן)
    # זהו למעשה סך החוב של מירה לקרדיטור (יעקב), כפי שחושב קודם.
    mira_debt_to_ilan_for_splitwise = mira_debt


    # סיכום נתונים לבדיקת תקינות (Display)
    summary = {
        "total_actual_debt": total_actual_debt,
        "specific_debt_total": specific_debt_total,
        "net_shared_debt": net_shared_debt,
        "shared_debt_per_person": shared_debt_per_person,
        "mira_debt_to_ilan_for_splitwise": mira_debt_to_ilan_for_splitwise,
    }

    return final_debts_to_payer, summary


# --- ממשק Streamlit ---
st.set_page_config(page_title="מחשבון חלוקת קניות רמי לוי", layout="wide")

st.markdown("# 🛒 מחשבון חלוקת קניות רמי לוי (שובר הנחה)")
st.markdown("כלי אוטומטי לחישוב מדויק של חובות ההחזר, כולל הנחת שוברים יחסית.")

# --- קלט נתונים ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. נתוני בסיס")
    total_receipt_cost = st.number_input(
        f"עלות כוללת בקבלה (לפני הנחה) ({CURRENCY})",
        min_value=0.0,
        value=767.34,
        step=1.0,
        key="receipt_cost"
    )
    
    payer_name = st.text_input("שם המשלם (הקרדיטור)", value="יעקב", key="payer_name_input")
    
    # דינמיות: שיעור ההנחה ניתן לשינוי
    discount_rate_percent = st.number_input(
        "שיעור הנחת השובר (%)",
        min_value=0.0,
        max_value=100.0,
        value=5.5,
        step=0.1,
        key="discount_rate_input"
    )
    
    # המרה לאחוז עשרוני
    discount_rate = discount_rate_percent / 100.0

with col2:
    st.subheader("2. פריטים ספציפיים (עלות *לפני הנחה* )")
    st.markdown("הכנס עלות פריטים שנרכשו **רק** על ידי אדם מסוים. השאר 0 אם אין.")

    specific_costs = {}
    
    # אילן ומירה מתחלקים בשאר, אבל יכולים לרכוש גם פריטים ספציפיים
    specific_costs["אילן"] = st.number_input(f"עלות ספציפית לאילן ({CURRENCY})", min_value=0.0, value=0.0, step=0.1)
    specific_costs["מירה"] = st.number_input(f"עלות ספציפית למירה ({CURRENCY})", min_value=0.0, value=13.80, step=0.1)
    
    # יעקב וההורים משלמים רק על מה שספציפי עבורם
    specific_costs["יעקב"] = st.number_input(f"עלות ספציפית ליעקב ({CURRENCY})", min_value=0.0, value=0.0, step=0.1)
    specific_costs["הורים"] = st.number_input(f"עלות ספציפית להורים ({CURRENCY})", min_value=0.0, value=0.0, step=0.1)

# --- חישוב והצגת תוצאות ---
if st.button("חשב חובות", type="primary"):
    if total_receipt_cost > 0:
        final_debts_to_payer, summary = calculate_debt(
            total_receipt_cost,
            discount_rate,
            payer_name,
            specific_costs
        )

        st.markdown("---")
        st.subheader("✅ סיכום וחלוקת חובות")
        
        # הטבלה הראשית מציגה את החוב לקרדיטור
        st.markdown(f"**חובות להחזר ל-** **{payer_name}** (הסכומים להחזר אם הייתם מחזירים לו ישירות):")
        
        debt_data_to_payer = []
        for name, debt in final_debts_to_payer.items():
            if debt > 0:
                debt_data_to_payer.append({"משתתף": name, f"חוב החזר ל-{payer_name} ({CURRENCY})": f"{debt:.2f}"})

        st.dataframe(
            debt_data_to_payer,
            use_container_width=True,
            hide_index=True
        )

        # התוצאה הספציפית ל-Splitwise
        st.markdown("---")
        st.subheader("📝 נתונים להזנה ל-Splitwise (בשיטת שרשור חובות)")
        st.info(
            f"**1. חוב אילן ליעקב:** {summary['total_actual_debt']:.2f} {CURRENCY} (אתה לוקח על עצמך את כל החוב ליעקב)."
        )
        st.success(
            f"**2. חוב מירה לאילן:** {summary['mira_debt_to_ilan_for_splitwise']:.2f} {CURRENCY} (זה הסכום שאתה מחייב את מירה - חלקה + הקפה שלה)."
        )
        st.caption("שים לב: חוב מירה לאילן (368.73₪) מורכב מחלקה המשותף (356.41₪) + עלות הקפסולות שלה לאחר הנחה (12.32₪).")
        
        # --- פירוט חישוב לבדיקת QA ---
        st.markdown("### 🔬 פירוט תהליך החישוב (לאימות)")
        st.markdown(f"**מכפיל הנחה:** $1 - {discount_rate_percent:.1f}\\% = {(1-discount_rate):.3f}$")
        st.info(f"**1. חוב אמיתי כולל:** {summary['total_actual_debt']:.2f} {CURRENCY}")
        st.info(f"**2. חוב ספציפי (מוזל):** {summary['specific_debt_total']:.2f} {CURRENCY}")
        
        st.success(f"**3. סכום משותף לחלוקה:** {summary['net_shared_debt']:.2f} {CURRENCY}")
        st.success(f"**4. החלק של כל אחד (אילן ומירה):** {summary['shared_debt_per_person']:.2f} {CURRENCY}")
        
        st.markdown("---")
        
        # סיכום החזר כדי לוודא תקינות
        total_repaid = sum(final_debts_to_payer.values())
        if abs(total_repaid - summary['total_actual_debt']) < 0.01:
             st.success(f"**בדיקת תקינות עברה:** סך ההחזר ({total_repaid:.2f} {CURRENCY}) שווה לחוב האמיתי הכולל.")
        else:
             st.error(f"**בדיקת תקינות נכשלה:** סך ההחזר ({total_repaid:.2f} {CURRENCY}) אינו שווה לחוב האמיתי ({summary['total_actual_debt']:.2f} {CURRENCY}).")


    else:
        st.warning("נא להזין עלות קבלה כוללת חיובית.")

st.markdown("---")
st.markdown("עכשיו אתה יכול להשתמש בסכום המדויק לחיוב מירה ב-Splitwise!")
