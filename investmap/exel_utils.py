import xlsxwriter
from io import BytesIO

from .models import InvestMapObject, PROJECT_TYPES


def generate_investmap_objects_xlsx():
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    for t in PROJECT_TYPES:
        worksheet = workbook.add_worksheet(t[1])
        values = InvestMapObject.objects.filter(project_type=t[0]).all()

        worksheet.write_string(1, 2, 'Назва')
        worksheet.write_string(1, 3, 'Ціна')
        worksheet.write_string(1, 4, 'Адреса')
        worksheet.write_string(1, 5, 'Площа')
        worksheet.write_string(1, 6, 'Контакти')

        for id_, value in enumerate(values):
            row = 2 + id_
            worksheet.write_string(row, 2, value.name)
            worksheet.write_string(row, 3, value.price)
            worksheet.write_string(row, 4, value.address)
            worksheet.write_string(row, 5, value.metrics)
            worksheet.write_string(row, 6, value.contacts)
    workbook.close()
    xlsx_data = output.getvalue()
    return xlsx_data
