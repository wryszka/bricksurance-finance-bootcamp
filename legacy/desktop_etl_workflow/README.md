# Legacy workflow: PO accruals at month-end

`po_accruals_month_end.yxmd` is a **synthetic** workflow file in the XML format that a common
desktop data-prep tool saves. It was written for this bootcamp; it is not any real company's
process. It is used in exercise **A5**.

## What the workflow does, in plain words

At month-end Finance accrues for goods and services that have been **received but not yet
invoiced**. The workflow:

1. Reads the purchase order extract and the supplier invoice extract (two CSV files on a shared drive).
2. Keeps purchase orders that are not cancelled and whose goods were received on or before the period end.
3. Keeps invoices dated on or before the period end, and totals them per purchase order.
4. Matches invoices to purchase orders, keeping purchase orders that have no invoice at all.
5. Calculates the accrual: purchase order amount minus what has been invoiced.
6. Keeps only purchase orders with something left to accrue.
7. Totals the accrual by company and cost centre and saves a spreadsheet for the journal.

## What is wrong with it today

- The period end date is typed by hand into two different tools every month.
- It reads files from a shared drive, so nobody can say which version of the extract was used.
- It runs on one person's laptop. When they are on leave, it doesn't run.
- The output is a spreadsheet; there is no record of what it produced last month.
