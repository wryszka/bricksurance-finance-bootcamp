# Legacy spreadsheet: the Accruals Tracker

`AccrualsTracker.bas` is the macro from a **synthetic** end-user computing (EUC) spreadsheet,
*"Accruals Tracker v7 FINAL (2).xlsm"*. It was written for this bootcamp; it is not any real
company's file. It is used in exercise **C2**.

## How the spreadsheet is used today

1. On working day 1 someone exports purchase orders and supplier invoices from two systems and
   pastes them into the `PO_Extract` and `INV_Extract` sheets.
2. They edit the period end date in the macro, then press **Run Month End**.
3. The macro fills the `Accruals` sheet, refreshes a pivot on `Summary`, and highlights big lines.
4. The `Summary` sheet is emailed to the Financial Controller, who replies "approved".
5. Someone keys the journal by hand.

The governed versions of the two extracts are your tables `1_purchase_orders` and
`1_supplier_invoices`.

There are at least three things in the macro that should worry you. Exercise C2 asks you to
find them.
