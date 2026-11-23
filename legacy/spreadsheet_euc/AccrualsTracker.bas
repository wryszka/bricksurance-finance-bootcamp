Attribute VB_Name = "AccrualsTracker"
' ============================================================================
'  Accruals Tracker v7 FINAL (2).xlsm  -  module AccrualsTracker
'  SYNTHETIC EXAMPLE written for this bootcamp. Not a real company's macro.
'
'  Sheets:  PO_Extract   (pasted in by hand from the purchasing system each month)
'           INV_Extract  (pasted in by hand from the payables system each month)
'           Accruals     (output - one row per purchase order)
'           Summary      (output - by company and cost centre, used for the journal)
'
'  Run:     press the "Run Month End" button on the Summary sheet.
' ============================================================================
Option Explicit

Const PERIOD_END As Date = #10/31/2026#     ' change me every month!!
Const LAST_ROW As Long = 1000               ' "we never have more than 1000 POs"
Const REVIEW_LIMIT As Double = 250000       ' lines above this go to the Financial Controller

Sub RunMonthEnd()
    Dim wsPO As Worksheet, wsInv As Worksheet, wsAcc As Worksheet, wsSum As Worksheet
    Dim i As Long, j As Long, outRow As Long
    Dim poId As String, invoiced As Double, accrual As Double

    Set wsPO = Sheets("PO_Extract")      ' A po_id, B supplier_name, C company_code, D cost_centre,
                                         ' E po_date, F goods_received_date, G po_amount_gbp, H po_status
    Set wsInv = Sheets("INV_Extract")    ' A supplier_invoice_id, B po_id, C invoice_date, D invoice_amount_gbp
    Set wsAcc = Sheets("Accruals")
    Set wsSum = Sheets("Summary")

    wsAcc.Range("A2:F5000").ClearContents
    outRow = 2

    On Error Resume Next                 ' added by J.P. 2023 - stops the macro crashing on bad dates

    For i = 2 To LAST_ROW
        poId = wsPO.Cells(i, 1).Value
        If poId <> "" Then
            ' Rule 1: ignore cancelled purchase orders
            If wsPO.Cells(i, 8).Value <> "Cancelled" Then
                ' Rule 2: goods must have been received on or before the period end
                If wsPO.Cells(i, 6).Value <> "" And CDate(wsPO.Cells(i, 6).Value) <= PERIOD_END Then
                    ' Rule 3: add up invoices for this PO dated on or before the period end
                    invoiced = 0
                    For j = 2 To LAST_ROW
                        If wsInv.Cells(j, 2).Value = poId Then
                            If CDate(wsInv.Cells(j, 3).Value) <= PERIOD_END Then
                                invoiced = invoiced + wsInv.Cells(j, 4).Value
                            End If
                        End If
                    Next j
                    ' Rule 4: accrual = ordered minus invoiced, only if something is left
                    accrual = wsPO.Cells(i, 7).Value - invoiced
                    If accrual > 0 Then
                        wsAcc.Cells(outRow, 1).Value = poId
                        wsAcc.Cells(outRow, 2).Value = wsPO.Cells(i, 3).Value   ' company_code
                        wsAcc.Cells(outRow, 3).Value = wsPO.Cells(i, 4).Value   ' cost_centre
                        wsAcc.Cells(outRow, 4).Value = wsPO.Cells(i, 7).Value   ' po_amount_gbp
                        wsAcc.Cells(outRow, 5).Value = invoiced
                        wsAcc.Cells(outRow, 6).Value = accrual
                        outRow = outRow + 1
                    End If
                End If
            End If
        End If
    Next i

    ' Summary by company and cost centre is a pivot table on the Summary sheet
    wsSum.PivotTables("pvtAccruals").RefreshTable

    ' Flag big lines for review
    For i = 5 To 40
        If wsSum.Cells(i, 4).Value >= REVIEW_LIMIT Then
            wsSum.Cells(i, 5).Value = "REVIEW"
            wsSum.Cells(i, 5).Interior.Color = vbYellow
        Else
            wsSum.Cells(i, 5).Value = ""
        End If
    Next i

    MsgBox "Month end accruals done. Email Summary sheet to Financial Controller.", vbInformation
End Sub
