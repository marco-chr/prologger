from fpdf import FPDF
import datetime
import json


class Report(FPDF):

    # HEADER

    def header(self):
        self.line(10, 10, 285, 10)
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, 'PROLOGGER PUNCHLIST REPORT ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1, 'C')

        # TODO add parametric name
        # TODO add project name

        headers = ['Number', 'System', 'Author', 'Description', 'Responsible', 'Supplier', 'Status']

        col_width = self.w / 16
        row_height = self.font_size + 2
        headers_width = [col_width*1,col_width*2,col_width*2,col_width*6,col_width*2,col_width*1,col_width*1]

        for item in range(0,7):
            self.cell(headers_width[item],row_height, txt=headers[item], border=0)
        self.ln(row_height)

    # FOOTER
    def footer(self):
        self.line(10, 200, 285, 200)
        # Add a page number
        page = 'Page ' + str(self.page_no()) + '/{nb}'
        self.cell(0, 10, page, 0, 0, 'R')

    # CREATE PDF BODY
    def create_pdf(pdf_path, json_dump_file):
        pdf = Report(orientation='L', unit='mm', format='A4', )
        pdf.alias_nb_pages()
        pdf.add_page()

        col_width = pdf.w / 16
        headers_width = [col_width*1,col_width*2,col_width*2,col_width*6,col_width*2,col_width*1,col_width*1]
        row_height = pdf.font_size + 2

        with open(json_dump_file) as json_file:
            data = json.load(json_file)

        #print(len(data['data']))
        maxrows = len(data['data'])

        keys = ['id', 'system', 'author', 'description', 'closure', 'supplier', 'status']

        pdf.add_font('Arial', '', r"/Users/mchrappan/PyCharmProjects/prologger/app/Arial.ttf", uni=True)
        pdf.set_font('Arial', size=8)

        firstx = pdf.get_x()
        maxlen = 0

        for i in range(0,maxrows): # i cycle through the punchlist rows
            for item in keys:
                if len(str(data['data'][i][item])) > maxlen:
                    maxlen = len(str(data['data'][i][item]))

            space_left = pdf.h - pdf.get_y() - round(maxlen/60+1)*5.52 - 20

            if space_left < 10:
                pdf.add_page()

            j = 0
            lasty2 = 0

            for item in keys:
                if len(str(data['data'][i][item])) > 60:
                    lastx = pdf.get_x()
                    lasty = pdf.get_y()
                    pdf.multi_cell(headers_width[j],row_height, txt=str(data['data'][i][item]), border=0)

                    if pdf.get_y() > lasty2:
                        lasty2 = pdf.get_y()

                    pdf.set_y(lasty)
                    pdf.set_x(lastx+headers_width[j])

                elif item == 'system':
                    pdf.cell(headers_width[j],row_height, txt=str(data['data'][i][item])[0:19], border=0)
                    if pdf.get_y() > lasty2:
                        lasty2 = pdf.get_y()

                elif item == 'supplier':
                    pdf.cell(headers_width[j],row_height, txt=str(data['data'][i][item])[0:9], border=0)
                    if pdf.get_y() > lasty2:
                        lasty2 = pdf.get_y()

                else:
                    pdf.cell(headers_width[j],row_height, txt=str(data['data'][i][item]), border=0)
                    if pdf.get_y() > lasty2:
                        lasty2 = pdf.get_y()

                #print("row " + str(i) + " item " + str(item) + " lasty2 " + str(lasty2))
                j = j + 1


            pdf.set_x(firstx)
            pdf.set_y(lasty2 + row_height)

        pdf.output(pdf_path)


def create_report(report_folder, json_dump):

    # TODO Change name / Change path
    # BUG: Regenerate after switching a project the json file!

    full_filename = report_folder + "prologger_export_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".pdf"
    saved_filename = "prologger_export_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".pdf"
    Report.create_pdf(full_filename, json_dump)

    return saved_filename


if __name__ == "__main__":
    filename = "prologger_export_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".pdf"
    Report.create_pdf(filename)
