# Data Schema Overview

This document provides a comprehensive overview of all tables loaded into the DuckDB database, including their schemas, sample data, and row counts.

---

## Table: clienti

**Total Rows:** 11,200

### Schema

| Column Name | Data Type | Nullable |
|------------|-----------|----------|
| Nome | VARCHAR | YES |
| Cognome | VARCHAR | YES |
| Età | BIGINT | YES |
| Luogo di Nascita | VARCHAR | YES |
| Luogo di Residenza | VARCHAR | YES |
| Professione | VARCHAR | YES |
| Reddito | BIGINT | YES |
| Reddito Familiare | BIGINT | YES |
| Numero Figli | BIGINT | YES |
| Anzianità con la Compagnia | BIGINT | YES |
| Stato Civile | VARCHAR | YES |
| Numero Familiari a Carico | BIGINT | YES |
| Reddito Stimato | DOUBLE | YES |
| Patrimonio Finanziario Stimato | DOUBLE | YES |
| Patrimonio Reale Stimato | DOUBLE | YES |
| Consumi Stimati | DOUBLE | YES |
| Propensione Acquisto Prodotti Vita | DOUBLE | YES |
| Propensione Acquisto Prodotti Danni | DOUBLE | YES |
| Valore Immobiliare Medio | DOUBLE | YES |
| Probabilità Furti Stimata | DOUBLE | YES |
| Probabilità Rapine Stimata | DOUBLE | YES |
| Zona di Residenza | VARCHAR | YES |
| codice_cliente | BIGINT | YES |
| Agenzia | VARCHAR | YES |
| Latitudine | DOUBLE | YES |
| Longitudine | DOUBLE | YES |
| Num_Polizze | BIGINT | YES |
| Engagement_Score | DOUBLE | YES |
| Churn_Probability | DOUBLE | YES |
| CLV_Stimato | BIGINT | YES |
| Potenziale_Crescita | DOUBLE | YES |
| Reclami_Totali | BIGINT | YES |
| Satisfaction_Score | DOUBLE | YES |
| Data_Ultima_Visita | DATE | YES |
| Visite_Ultimo_Anno | BIGINT | YES |
| Cluster_Risposta | VARCHAR | YES |

### Sample Data

| Nome | Cognome | Età | Professione | Reddito | Stato Civile | codice_cliente | Agenzia | Num_Polizze | Engagement_Score | Cluster_Risposta |
|------|---------|-----|-------------|---------|--------------|----------------|---------|-------------|------------------|------------------|
| Rosina | Biagi | 60 | Pensionato | 19,243 | Sposato | 9500 | Agenzia_Napoli_2 | 1 | 60.0 | Moderate_Responder |
| Mattia | Foà | 43 | Avvocato | 113,648 | Divorziato | 9501 | Agenzia_Sevignano | 4 | 78.4 | High_Responder |
| Paride | Taccola | 63 | Medico | 104,863 | Divorziato | 9502 | Agenzia_Qualso | 4 | 100.0 | High_Responder |

---

## Table: polizze

**Total Rows:** 18,039

### Schema

| Column Name | Data Type | Nullable |
|------------|-----------|----------|
| Unnamed: 0 | DOUBLE | YES |
| codice_cliente | BIGINT | YES |
| Prodotto | VARCHAR | YES |
| Area di Bisogno | VARCHAR | YES |
| Data di Emissione | DATE | YES |
| Premio_Ricorrente | DOUBLE | YES |
| Premio_Unico | DOUBLE | YES |
| Capitale_Rivalutato | DOUBLE | YES |
| Massimale | DOUBLE | YES |
| Stato_Polizza | VARCHAR | YES |
| Data_Scadenza | DATE | YES |
| Canale_Acquisizione | VARCHAR | YES |
| Commissione_Perc | DOUBLE | YES |
| Premio_Totale_Annuo | DOUBLE | YES |
| Commissione_Euro | BIGINT | YES |
| Costi_Operativi | DOUBLE | YES |
| Margine_Lordo | BIGINT | YES |
| Importo_Liquidato | DOUBLE | YES |
| Sinistri_Totali | BIGINT | YES |
| Loss_Ratio | DOUBLE | YES |

### Sample Data

| codice_cliente | Prodotto | Area di Bisogno | Data di Emissione | Premio_Ricorrente | Premio_Unico | Stato_Polizza | Canale_Acquisizione |
|----------------|----------|-----------------|-------------------|-------------------|--------------|---------------|---------------------|
| 9500 | Assicurazione Casa e Famiglia: Casa Serena | Protezione | 2011-05-06 | 387.0 | - | Scaduta | Rete Diretta Agenziale |
| 9501 | Assicurazione Casa e Famiglia: Casa Serena | Protezione | 2021-09-25 | 683.0 | - | Attiva | Rete Diretta Agenziale |
| 9501 | Polizza Vita a Premio Unico: Futuro Sicuro | Risparmio e Investimento | 2017-11-16 | - | 47,300.0 | Attiva | Rete Diretta Agenziale |

---

## Table: sinistri

**Total Rows:** 16,839

### Schema

| Column Name | Data Type | Nullable |
|------------|-----------|----------|
| codice_cliente | BIGINT | YES |
| Prodotto | VARCHAR | YES |
| Area di Bisogno | VARCHAR | YES |
| Sinistro | VARCHAR | YES |
| Data_Sinistro | DATE | YES |
| Importo_Liquidato | BIGINT | YES |
| Stato_Liquidazione | VARCHAR | YES |

### Sample Data

| codice_cliente | Prodotto | Area di Bisogno | Sinistro | Data_Sinistro | Importo_Liquidato | Stato_Liquidazione |
|----------------|----------|-----------------|----------|---------------|-------------------|--------------------|
| 9500 | Assicurazione Casa e Famiglia: Casa Serena | Protezione | None | - | - | None |
| 9501 | Assicurazione Casa e Famiglia: Casa Serena | Protezione | None | - | - | None |
| 9501 | Polizza Vita a Premio Unico: Futuro Sicuro | Risparmio e Investimento | None | - | - | None |

**Note:** Many records appear to have NULL values for claim details.

---

## Table: reclami

**Total Rows:** 16,839

### Schema

| Column Name | Data Type | Nullable |
|------------|-----------|----------|
| codice_cliente | BIGINT | YES |
| Prodotto | VARCHAR | YES |
| Area di Bisogno | VARCHAR | YES |
| Reclami_e_info | VARCHAR | YES |

### Sample Data

| codice_cliente | Prodotto | Area di Bisogno | Reclami_e_info |
|----------------|----------|-----------------|----------------|
| 9500 | Assicurazione Casa e Famiglia: Casa Serena | Protezione | None |
| 9501 | Assicurazione Casa e Famiglia: Casa Serena | Protezione | None |
| 9501 | Polizza Vita a Premio Unico: Futuro Sicuro | Risparmio e Investimento | None |

**Note:** Many records appear to have NULL values for complaint information.

---

## Table: abitazioni

**Total Rows:** 5,190

### Schema

| Column Name | Data Type | Nullable |
|------------|-----------|----------|
| codice_cliente | BIGINT | YES |
| Luogo di Residenza | VARCHAR | YES |
| Indirizzo | VARCHAR | YES |
| Metratura | BIGINT | YES |
| Sistema_Allarme | BOOLEAN | YES |

### Sample Data

| codice_cliente | Luogo di Residenza | Indirizzo | Metratura | Sistema_Allarme |
|----------------|-------------------|-----------|-----------|-----------------|
| 9500 | Napoli | Piazza Garibaldi, 91 | 90 | True |
| 9501 | Sevignano | Corso Italia, 7 | 177 | True |
| 9502 | Qualso | Via Vittorio Emanuele, 63 | 227 | False |

---

## Table: interazioni_clienti

**Total Rows:** 41,195

### Schema

| Column Name | Data Type | Nullable |
|------------|-----------|----------|
| codice_cliente | BIGINT | YES |
| Data_Interazione | DATE | YES |
| Tipo_Interazione | VARCHAR | YES |
| Motivo | VARCHAR | YES |
| Durata_Minuti | DOUBLE | YES |
| Esito | VARCHAR | YES |
| Note | VARCHAR | YES |
| Conversione | BOOLEAN | YES |

### Sample Data

| codice_cliente | Data_Interazione | Tipo_Interazione | Motivo | Durata_Minuti | Esito | Conversione |
|----------------|------------------|------------------|--------|---------------|-------|-------------|
| 9500 | 2024-04-05 | Visita Agente | Reclamo | 15.0 | Positivo | False |
| 9500 | 2024-08-29 | Chat Online | Pagamento Premio | 2.0 | Negativo | False |
| 9500 | 2025-04-18 | App Mobile | Consulenza | 5.0 | Neutrale | False |

---

## Table: competitor_prodotti

**Total Rows:** Sample data only (exact count not specified)

### Schema

| Column Name | Data Type | Nullable |
|------------|-----------|----------|
| Competitor | VARCHAR | YES |
| Tipo_Prodotto | VARCHAR | YES |
| Premio_Medio | BIGINT | YES |
| Massimale_Medio | BIGINT | YES |
| Rating_Clienti | DOUBLE | YES |
| Quota_Mercato_Perc | DOUBLE | YES |
| Coperture_Extra | VARCHAR | YES |

### Sample Data

| Competitor | Tipo_Prodotto | Premio_Medio | Massimale_Medio | Rating_Clienti | Quota_Mercato_Perc | Coperture_Extra |
|------------|---------------|--------------|-----------------|----------------|-------------------|-----------------|
| Protezione Italia | Casa | 333 | 100,000 | 4.5 | 14.4% | Base |
| Sicurezza Unita | Casa | 409 | 100,000 | 3.9 | 5.2% | Intermedia |
| Futuro Sereno | Casa | 419 | 200,000 | 3.9 | 12.0% | Intermedia |

---

## Key Observations

### Data Relationships
- **codice_cliente** is the primary key linking customers across tables
- **Prodotto** and **Area di Bisogno** appear in multiple tables (polizze, sinistri, reclami)

### Data Quality Notes
- `sinistri` and `reclami` tables have many NULL values in key fields
- `polizze` table has an `Unnamed: 0` column (likely an index from CSV)
- Customer engagement metrics already calculated (Engagement_Score, Churn_Probability, CLV_Stimato)
- Geographic data available (Latitudine, Longitudine, Zona di Residenza)

### Table Sizes
- Largest: **interazioni_clienti** (41,195 rows)
- Medium: **polizze** (18,039 rows), **sinistri** (16,839 rows), **reclami** (16,839 rows)
- Smaller: **clienti** (11,200 rows), **abitazioni** (5,190 rows)
