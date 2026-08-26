# Build — extraction

`PDD.md` §5.6 says only one of the three documents is a form. That one is read into fields; the other two are prose and stay documents.

**Two routes, and taking the second is not a penalty.** Extraction feeds everything after it, so a half-trained model is worse than a borrowed one — and both produce the same field groups, so everything downstream is identical either way.

**Adopt the shared project.** `CONFIG.md` names it. Point your design's extraction step at it and move on. Ten minutes.

**Or train your own.** Use the **`uipath-ixp`** skill. Import `3a-extraction/taxonomy.json` — never retype it and never accept the tool's own suggestion, because a suggested taxonomy is plausible-but-slightly-different and the difference surfaces three blocks later as a field nobody can find. Get samples by running the claim generator ten to fifteen times unaimed, for the natural spread of countries, currencies and damage-row counts. Then label, train, publish, and deploy it to your folder — **publishing is not deploying**, and a model that is published but not deployed cannot be called at run time.

**Done when** a claim form you have never labelled comes back with every field group populated and the damage rows repeating correctly — one row per item, not one blob.

Take the shared project the moment yours stops being the interesting part of your day.
