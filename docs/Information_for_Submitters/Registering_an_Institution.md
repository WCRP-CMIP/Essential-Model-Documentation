# Registering an Institution

If your institution is not yet available in the EMD dropdown, you need to register it in the CMIP7 CVs before you can complete your model submission.

---

## How institutions are structured

Institutions in CMIP7 are registered as **institution members** — each record specifies which member organisations belong to an institution and the DRS name (institution ID) that will appear in file paths and global attributes.

This structure supports both:

- **Single-member institutes** — one organisation, one institution ID.
- **Consortia** — multiple member organisations listed under a shared institution ID (e.g. EC-Earth). If a consortium also has its own ROR, it can list itself as a member too.

ROR identifiers are attached to the individual member records, not the top-level institution.

!!! note
    In the CMIP7 CVs the top-level collection is called `institutions`, but internally this links to the WCRP universe `organisations` directory. The member records that carry ROR identifiers end up in the universe `institutions` directory. This is a known inconsistency that will be tidied up in CMIP8 — for now, you do not need to worry about it.

---

## How to register

Submit the institution member form on the CMIP7-CVs repository:

**[Register institution member →](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=register-institution-member.yml)**

The form asks you to specify your member organisation(s) and the DRS institution ID you want to use.

---

## How long it takes

Registration involves several steps across different systems. Here is a realistic timeline:

| Step | Who | Typical wait |
|------|-----|-------------|
| Submit the form | You | ~5 minutes |
| PR reviewed and merged into `esgvoc_dev` | Laurent or Daniel | ~1 day |
| CMIP7 CVs and universe synced in esgvoc | [@ltroussellier](https://github.com/ltroussellier) | ~every 2 days |
| Web CVs API updated to serve the new data | [@ltroussellier](https://github.com/ltroussellier) | TBC |
| EMD forms updated to include the new institution | [@wolfiex](https://github.com/wolfiex) | ~daily (scheduled) |

**The maximum end-to-end wait is currently around 3–5 days.**

If you are working to a deadline, submit the institution form as early as possible — ideally before starting your EMD grid submissions.

---

## Once registered

Once your institution ID appears in the EMD dropdown, you can proceed with your model submission as normal. See the [Submission Guide](Submission-Guide/) for the full four-stage process.
