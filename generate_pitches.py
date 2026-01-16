import csv
import random


def generate_pitch(row):
    """Generate a personalized sales pitch based on customer data."""
    nome = row["nome"]
    eta = int(row["eta"])
    raccomandazione = row["raccomandazione_nba"]
    satisfaction_score = float(row["satisfaction_score"])
    num_prodotti_distinti = int(row["num_prodotti_distinti"])

    # Determine which products to recommend
    products = raccomandazione.split("+")

    # Base greetings
    greetings = [
        f"Buongiorno {nome}, la chiamo da Vita Sicura.",
        f"Salve {nome}, sono un consulente di Vita Sicura.",
        f"Gentile {nome}, le scrivo da Vita Sicura.",
        f"Buonasera {nome}, la contatto per conto di Vita Sicura.",
    ]

    # Product-specific pitches
    pitch_templates = {
        "Casa": [
            "Gli eventi meteorologici estremi nella sua zona sono in aumento. Una polizza casa la proteggerebbe da danni imprevisti.",
            "La sua abitazione merita la migliore protezione. Le proponiamo una copertura completa per la casa.",
            "Incendi, allagamenti, furti: la polizza Casa Serena la protegge da ogni imprevisto domestico.",
            "Proteggere la propria casa è fondamentale. Abbiamo soluzioni su misura per lei.",
        ],
        "Salute": [
            "Come professionista nel settore sanitario, sa quanto è importante una copertura salute completa. Le presentiamo Salute Protetta.",
            "La polizza Salute Protetta offre accesso a strutture private e rimborsi rapidi. Perfetta per la sua professione.",
            "Una copertura sanitaria integrativa le garantirebbe accesso immediato alle migliori cure mediche.",
            "La sua salute merita attenzione. Le proponiamo una polizza con copertura completa e assistenza h24.",
        ],
        "Pip": [
            "A {eta} anni è il momento ideale per pensare al futuro. Il nostro PIP Pensione Serenità le garantisce tranquillità.",
            "Integrare la pensione pubblica è essenziale. Il nostro piano pensionistico le offre vantaggi fiscali immediati.",
            "Pensione Serenità: investa oggi per un futuro sereno. Vantaggi fiscali e rendimenti competitivi.",
            "Il suo futuro merita sicurezza. Il nostro PIP le permette di costruire una pensione integrativa solida.",
        ],
        "Investimento": [
            "La polizza Vita Risparmio Costante combina protezione e investimento con rendimenti garantiti.",
            "Proteggere i suoi risparmi con una polizza vita le offre sicurezza e vantaggi fiscali.",
            "Investire in modo sicuro: la nostra soluzione combina assicurazione e risparmio.",
        ],
    }

    # Build the pitch
    greeting = random.choice(greetings)

    # Determine main focus
    if "Casa" in products and "Salute" in products and "Pip" in products:
        product_pitch = "Le nostre analisi indicano un'opportunità perfetta per lei: un pacchetto completo con assicurazione casa, salute e piano pensionistico. Sono soluzioni che si integrano perfettamente con il suo profilo."
    elif "Casa" in products and "Salute" in products:
        product_pitch = f"Abbiamo identificato due prodotti ideali per lei: assicurazione casa e salute. {random.choice(pitch_templates['Casa'])} Inoltre, la copertura sanitaria è essenziale per la sua tranquillità."
    elif "Casa" in products and "Pip" in products:
        product_pitch = f"Le proponiamo due soluzioni: protezione casa e piano pensionistico. {random.choice(pitch_templates['Casa'])}"
    elif "Salute" in products and "Pip" in products:
        product_pitch = f"Dalla nostra analisi emerge un'opportunità per assicurazione salute e piano pensionistico. {random.choice(pitch_templates['Salute'])}"
    elif "Casa" in products:
        product_pitch = random.choice(pitch_templates["Casa"])
    elif "Salute" in products:
        product_pitch = random.choice(pitch_templates["Salute"])
    elif "Pip" in products:
        product_pitch = random.choice(pitch_templates["Pip"]).replace("{eta}", str(eta))
    else:
        product_pitch = "Le proponiamo soluzioni su misura per le sue esigenze."

    # Closing based on customer profile
    if num_prodotti_distinti > 0:
        closing = "Lei è già nostra cliente e potremmo proporle condizioni vantaggiose."
    elif satisfaction_score > 85:
        closing = "Clienti con il suo profilo apprezzano molto le nostre soluzioni."
    else:
        closing = "Sarei lieto di illustrarle i dettagli in una breve chiamata."

    return f"{greeting} {product_pitch} {closing}"


# Read the CSV file
input_file = r"c:\Users\gabri\workspace\aida_projects\aida-challenge\data\analytics\client_nba_pitches_proposal.csv"
output_file = r"c:\Users\gabri\workspace\aida_projects\aida-challenge\data\analytics\client_nba_pitches_proposal.csv"

rows = []
with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames + ["pitch_suggestion"]

    for row in reader:
        pitch = generate_pitch(row)
        row["pitch_suggestion"] = pitch
        rows.append(row)

# Write back to CSV
with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Aggiunta colonna 'pitch_suggestion' a {len(rows)} clienti")
print(f"✓ File aggiornato: {output_file}")
