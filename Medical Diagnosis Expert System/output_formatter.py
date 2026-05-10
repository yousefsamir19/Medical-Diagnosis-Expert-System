def format_and_display_results(results, patterns):
   
    if not results:
        print("\nSorry, I could not determine a diagnosis based on your symptoms.")
        print("Please consult a doctor or try describing your symptoms in more detail.")
        return

   
    precautions_lookup = {
        entry["name"]: entry["precautions"]
        for entry in patterns
    }

   
    sorted_results = sorted(results, key=lambda x: x["cf"], reverse=True)

    
    print("\n" + "=" * 45)
    print("            Diagnosis Results")
    print("=" * 45)

    for disease in sorted_results:
        name       = disease["name"].replace("_", " ").title()
        percentage = round(disease["cf"] * 100, 1)
        print(f"  · {name}: {percentage}%")

   
    top_disease    = sorted_results[0]
    top_name_raw   = top_disease["name"]
    top_name_clean = top_name_raw.replace("_", " ").title()

   
    print("\n" + "=" * 45)
    print(f"   Precautions for {top_name_clean}")
    print("=" * 45)

    precautions = precautions_lookup.get(top_name_raw, [])

    if precautions:
        for i, precaution in enumerate(precautions, start=1):
            print(f"  {i}. {precaution.capitalize()}")
    else:
        print("  No precautions found for this disease.")

    print("=" * 45 + "\n")