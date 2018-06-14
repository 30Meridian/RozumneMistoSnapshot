#!/usr/bin/python
# -*- coding: utf-8 -*-
from io import BytesIO
import xlsxwriter
from django.utils.translation import ugettext


def WriteToExcel(transactions, town, townslug, daterange, receiver_name):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet("СПИСОК_ТРАНЗАКЦІЙ")


    # excel styles
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    sub_title = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter'
    })

    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1
    })


    # merge cells
    worksheet_s.merge_range('B2:I2', "Виписка по публічним фінансам ("+town+"), отримувач платежів - "+receiver_name+"", title)
    if(daterange):
        worksheet_s.merge_range('B3:I3', "Період виписки: "+daterange+". Перейти до 'Розумного міста' на генератор виписок - www.rozumnemisto.org/"+townslug+"/edata/", sub_title)
    else:
        worksheet_s.merge_range('B3:I3',"Перейти до 'Розумного міста' на генератор виписок - www.rozumnemisto.org/" + townslug + "/edata/", sub_title)


    # write header
    worksheet_s.write(4, 0, ugettext("ID транзакції"), header)
    worksheet_s.write(4, 1, ugettext("Сума"), header)
    worksheet_s.write(4, 2, ugettext("Дата транзакції"), header)
    worksheet_s.write(4, 3, ugettext("Назва платника"), header)
    worksheet_s.write(4, 4, ugettext("Отримувач"), header)
    worksheet_s.write(4, 5, ugettext("Призначення"), header)
    worksheet_s.write(4, 6, ugettext("Банк платника"), header)
    worksheet_s.write(4, 7, ugettext("ЄДРПОУ платника"), header)
    worksheet_s.write(4, 8, ugettext("МФО банку платника"), header)
    worksheet_s.write(4, 9, ugettext("Банк отримувача"), header)
    worksheet_s.write(4, 10, ugettext("ЄДРПОУ отримувача"), header)
    worksheet_s.write(4, 11, ugettext("МФО банку отримувача"), header)


    row = 5
    for idx, transaction in enumerate(transactions):
        row = 5 + idx
        worksheet_s.write_number(row, 0, transaction.trans_id, cell_center)
        worksheet_s.write_number(row, 1, transaction.amount, cell_center)
        worksheet_s.write_string(row, 2, str(transaction.trans_date), cell_center)
        worksheet_s.write_string(row, 3, transaction.payer_name, cell)
        worksheet_s.write_string(row, 4, transaction.recipt_name, cell)
        worksheet_s.write_string(row, 5, transaction.payment_details, cell)
        worksheet_s.write_string(row, 6, transaction.payer_bank, cell)
        worksheet_s.write_string(row, 7, transaction.payer_edrpou, cell_center)
        worksheet_s.write_string(row, 8, transaction.payer_mfo, cell_center)
        worksheet_s.write_string(row, 9, transaction.recipt_bank, cell)
        worksheet_s.write_string(row, 10, transaction.recipt_edrpou, cell_center)
        worksheet_s.write_string(row, 11, transaction.recipt_mfo, cell_center)

    worksheet_s.write_formula(row+1, 1, '=SUM(B6:B'+str(row+1)+')', cell_center)


        # the rest of the data
    worksheet_s.set_column('A:A', 15)
    worksheet_s.set_column('B:B', 15)
    worksheet_s.set_column('C:C', 25)
    worksheet_s.set_column('D:D', 40)
    worksheet_s.set_column('E:E', 40)
    worksheet_s.set_column('F:F', 50)
    worksheet_s.set_column('G:G', 25)
    worksheet_s.set_column('H:H', 12)
    worksheet_s.set_column('I:I', 12)
    worksheet_s.set_column('J:J', 25)
    worksheet_s.set_column('K:K', 10)
    worksheet_s.set_column('K:K', 10)

    # close workbook
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data
