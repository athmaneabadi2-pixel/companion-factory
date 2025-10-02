# Cursor - Bonnes pratiques (D3-A)

## RŠgles (8)
1. Une intention par message. Prompts courts (=3 phrases).
2. Ancre au code: cite fichier, fonction, ligne. Utilise la s‚lection (chat sur surlignage).
3. ItŠre petit: "ne modifie que la fonction X", "propose un diff".
4. Demande un plan (5 points) puis applique ‚tape par ‚tape.
5. Garde le contr“le: "explique tes changements", "liste risques / TODO".
6. Refactor guid‚: PEP8, types, fonctions pures, s‚paration I/O vs logique.
7. Tests rapides: demande un test minimal et un script de run local.
8. Contexte cibl‚: colle extraits docs/projets utiles, ‚vite le bruit.

## Prompts types (FR)
- "Lis %%FILE%% ligne %%N%%-%%M%%. Dis-moi ce que fait la fonction."
- "Propose un diff minimal pour corriger %%BUG%% sans changer l'API."
- "Refactor en fonction pure (I/O hors de la fonction). Ajoute types."
- "cris un test pytest minimal pour %%FUNC%%. N'ajoute rien d'autre."
- "Pr‚pare un plan en 5 ‚tapes pour impl‚menter %%FEATURE%%. Attends validation."
- "Explique les risques et ajoute 3 TODO en commentaires."

> Astuce: si d‚rive, ouvre un nouveau chat avec un r‚sum‚ de contexte.
