#!/usr/bin/python
# -*- coding: utf-8 -*-
from io import BytesIO
import xlsxwriter
from django.utils.translation import ugettext
from django.db.models import Avg, Sum, Max, Min


def WriteToExcel(transactions, town, townslug, daterange,fop_rating, uric_rating):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet("СПИСОК_ТРАНЗАКЦІЙ")
    #============Рейтинг ФОП==========#
    worksheet = workbook.add_worksheet("ФОП_ТОП_ОТРИМУВАЧІ_ПЛАТЕЖІВ")
    bold = workbook.add_format({'bold': 1})

    fop_name = []
    fop_amount = []

    for fop in fop_rating:
        fop_name.append(fop['recipt_name'])
        fop_amount.append(fop['total'])

    worksheet.write_column('F7', fop_name)
    worksheet.write_column('G7', fop_amount)

    chart_fop = workbook.add_chart({'type': 'bar'})
    len_list = len(fop_amount) + 7

    # Configure the first series.
    chart_fop.add_series({
        'categories': '=ФОП_ТОП_ОТРИМУВАЧІ_ПЛАТЕЖІВ!$F$7:$F$'+str(len_list),
        'values': '=ФОП_ТОП_ОТРИМУВАЧІ_ПЛАТЕЖІВ!$G$7:$G$'+str(len_list),
    })
    chart_fop.set_legend({'none': True})

    # Add a chart title and some axis labels.
    chart_fop.set_title({'name': 'ТОП отримувачів платежів по ФО-СПД (гривень) '+ daterange})
    chart_fop.set_x_axis({'name': 'Скільки гривень оплачено отримувачу за вибраний період по '+town})

    # Set an Excel chart style.
    chart_fop.set_style(11)

    # Insert the chart into the worksheet (with an offset).
    worksheet.insert_chart('A1', chart_fop, {'x_offset': 25, 'y_offset': 10})
    chart_fop.set_size({'width': 1220, 'height': 776})

    # ============Рейтинг Юриков==========#

    worksheet = workbook.add_worksheet("ЮО_ТОП_ОТРИМУВАЧІ_ПЛАТЕЖІВ")
    bold = workbook.add_format({'bold': 1})

    uric_name = []
    uric_amount = []

    for uric in uric_rating:
        uric_name.append(uric['recipt_name'])
        uric_amount.append(uric['total'])

    worksheet.write_column('F7', uric_name)
    worksheet.write_column('G7', uric_amount)

    chart_uric = workbook.add_chart({'type': 'bar'})
    len_list = len(uric_amount) + 7

    # Configure the first series.
    chart_uric.add_series({
        'categories': '=ЮО_ТОП_ОТРИМУВАЧІ_ПЛАТЕЖІВ!$F$7:$F$'+str(len_list),
        'values': '=ЮО_ТОП_ОТРИМУВАЧІ_ПЛАТЕЖІВ!$G$7:$G$'+str(len_list),
    })
    chart_uric.set_legend({'none': True})

    # Add a chart title and some axis labels.
    chart_uric.set_title({'name': 'ТОП отримувачів платежів по юридичним особам (гривень) '+ daterange})
    chart_uric.set_x_axis({'name': 'Скільки гривень оплачено отримувачу за вибраний період по '+town})

    # Set an Excel chart style.
    chart_uric.set_style(11)

    # Insert the chart into the worksheet (with an offset).
    worksheet.insert_chart('A1', chart_uric, {'x_offset': 25, 'y_offset': 10})
    chart_uric.set_size({'width': 1220, 'height': 776})



#=============================================================================================================#



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
    worksheet_s.merge_range('B2:I2', "Виписка по публічним фінансам ("+town+")", title)
    if(daterange):
        worksheet_s.merge_range('B3:I3', "Період виписки: "+daterange+". Перейти до 'Розумного міста' на генератор виписок - www.rozumnemisto.org/"+townslug+"/edata/", sub_title)
    else:
        worksheet_s.merge_range('B3:I3',"Перейти до 'Розумного міста' на генератор виписок - www.rozumnemisto.org/" + townslug + "/edata/", sub_title)


    # write header
    worksheet_s.write(4, 0, ugettext("ID транзакції"), header)
    worksheet_s.write(4, 1, ugettext("Сума(грн.)"), header)
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


    # column widths
    town_col_width = 10
    description_col_width = 10
    observations_col_width = 25
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

