But : Application pédagogique Django (SQLite, TZ = Africa/Ouagadougou) pour gérer assurance (produits santé/auto, assurés, contrats, sinistres, plaintes, imports Excel, paiements, dashboard DG).

Apps : accounts, catalog, crm, underwriting, claims, complaints, finance, imports, dashboard, audit.

Front : templates HTML + CSS + JS (DataTables pour listes, Chart.js pour dashboard).

Rôles : dg, commercial, redacteur, gestionnaire, actuaire, rh.

Identifiants : ASS00001 (assuré), POL{YYYY}{seq} (contrat), SINS-ASS00001-YYYYMMDDhhmmss (sinistre).

Statuts clés :

Contrat: DRAFT→ACTIVE→EXPIRED→CANCELLED (+renouvellement)

Sinistre: SUBMITTED→APPROVED→PAID / REJECTED

Plainte: OPEN→ANSWERED→CLOSED

Règles (exemples) : carence (waiting_days), contrat ACTIVE à la date d’incident, montant remboursable = min(invoice * coverage_rate, remaining_limit), idempotence imports, CNIB/immatriculation uniques, PJ max 5 Mo.