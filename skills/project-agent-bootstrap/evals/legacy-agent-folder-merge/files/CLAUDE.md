# Ledger service

## Notes from the team
- Money is stored as int64 cents, never float.
- Every write goes through `ledger.Post`, which enforces debit == credit.
- Run `make test` before pushing.
