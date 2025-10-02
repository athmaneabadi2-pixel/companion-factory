# Cursor — Bonnes pratiques (D3-A)

## Règles (8)
1. Une intention par message (≤3 phrases).
2. Ancre au code : fichier, fonction, lignes (utilise la sélection).
3. Petites itérations : “ne modifie que X”, “propose un diff”.
4. Demande un plan (5 points) avant d’appliquer.
5. Contrôle : “explique tes changements”, “liste risques/TODO”.
6. Refactor guidé : PEP8, types, fonctions pures (I/O séparées).
7. Tests rapides : un test minimal + script de run local.
8. Contexte ciblé : extraits utiles, zéro bruit.

## Prompts types (FR)
- "Lis %FILE% ligne %N%-%M%. Dis ce que fait la fonction."
- "Diff minimal pour corriger %BUG% sans changer l'API."
- "Refactor en fonction pure (I/O dehors) + types."
- "Écris un test pytest minimal pour %FUNC%."
- "Plan en 5 étapes pour %FEATURE%. Attends validation."
- "Liste 3 risques et ajoute 3 TODO en commentaires."
