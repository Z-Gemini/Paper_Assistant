import fitz
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate,Paragraph,Image
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from classUI import *

class InOut:
    def __init__(self, pdf):
        self.PdfFile = pdf
        # Create folder and file name
        self.dir_temp = os.path.dirname(self.PdfFile) + "_temp"
        self.filename = os.path.split(self.PdfFile)[1].split('.')[0]
        self.dir_images = os.path.join(self.dir_temp, self.filename + "_images").replace(r'\\', '/')
        self.dir_text = os.path.join(self.dir_temp, self.filename + ".txt").replace(r'\\', '/')
        self.dir_pdf = os.path.join(self.dir_temp, self.filename + "_simple" + ".pdf").replace(r'\\', '/')

class Processor:
    # init extract result path
    def __init__(self, inout):
        self.InOut = inout
        self.Result = True

        pdfmetrics.registerFont(TTFont('SimSun', 'data/SimSun.ttf'))
        pdfmetrics.registerFont(TTFont('SimHei', 'data/SimHei.ttf'))

        self.styleSheet = getSampleStyleSheet()
        self.styleSheet.add(ParagraphStyle(name='Customer_Normal',
                                           fontName='SimSun',
                                           fontSize=10,
                                           leading=12,
                                           allowOrphans=0,
                                           spaceBefore=6,
                                           spaceAfter=6,
                                           wordWrap=1))

        self.styleSheet.add(ParagraphStyle(name='Customer_Bold',
                                           parent=self.styleSheet['Customer_Normal'],
                                           fontName='SimHei',
                                           fontSize=12,
                                           leading=12,
                                           spaceAfter=6))

        self.styleSheet.add(ParagraphStyle(name='Customer_Title',
                                           parent=self.styleSheet['Customer_Normal'],
                                           fontName='SimHei',
                                           fontSize=18,
                                           leading=22,
                                           spaceAfter=6))

        self.styleSheet.add(ParagraphStyle(name='Customer_Body',
                                           parent=self.styleSheet['Customer_Normal'],
                                           spaceBefore=6))

    # Process and save texts to .txt file
    def process(self):
        Keywords = ""
        Abstract = ""
        with fitz.open(self.InOut.PdfFile) as pdfOpen:
            if not os.path.exists(self.InOut.dir_temp):
                os.mkdir(self.InOut.dir_temp)
            if not os.path.exists(self.InOut.dir_images):
                os.mkdir(self.InOut.dir_images)

            # process text
            Title = pdfOpen.metadata['title']
            Subject = pdfOpen.metadata['subject']
            Blocks = [x[4] for x in pdfOpen[0].get_text("blocks")]
            search_abstract = "abstract"
            search_keywords = "keywords"
            for i in range(len(Blocks) - 1):
                if search_abstract in str(Blocks[i]).lower().replace(' ', ''):
                    Abstract = Blocks[i] + Blocks[i + 1]
                if search_keywords in str(Blocks[i]).lower().replace(' ', ''):
                    Keywords = Blocks[i]
                with open(self.InOut.dir_text, 'w+', encoding='utf8') as f:
                    f.write("Current file is: " + self.InOut.filename + '\n')
                    f.write('\n')
                    # Title
                    f.write("Title Start" + '\n')
                    if not Title == "":
                        f.write(Title + '\n')
                    else:
                        f.write("No Result" + '\n')
                    f.write("Title End" + '\n')
                    f.write('\n')

                    # Subject
                    f.write("Subject Start" + '\n')
                    if not Subject == "":
                        f.write(Subject + '\n')
                    else:
                        f.write("No Result" + '\n')
                    f.write("Subject End" + '\n')
                    f.write('\n')

                    # Abstract
                    f.write("Abstract Start" + '\n')
                    if not Abstract == "":
                        f.write(Abstract.replace('\n','') + '\n')
                    else:
                        f.write("No Result" + '\n')
                    f.write("Abstract End" + '\n')
                    f.write('\n')

                    # Keywords
                    f.write("Keywords Start" + '\n')
                    if not Keywords == "":
                        f.write(Keywords.replace('\n',',') + '\n')
                    else:
                        f.write("No Result" + '\n')
                    f.write("Keywords End" + '\n')
                    f.write('\n')

            for page in pdfOpen:
                for img in page.get_images():
                    xref = img[0]
                    img_dict = img[1]
                    try:
                        pix = fitz.Pixmap(pdfOpen, xref)
                        if pix.n < 5:  # 只处理RGBA或者灰度图像
                            if pix.colorspace != 'rgb':  # 如果颜色空间不是RGB，则转换为RGB
                                pix = fitz.Pixmap(fitz.csRGB, pix)
                            img_id = f"{page.number}.{xref}"
                            imagePath = os.path.join(self.InOut.dir_images, f"{img_id}.png")
                            pix.save(imagePath)
                        pix = None
                    except ValueError as e:
                        continue
        return self.Result

    def showOnWindow(self, parserWindow):
        pass

    def updateFromView(self, parserWindow):
        pass

    def drawToPdf(self, paragraphs):
        pass

class AbstractProcessor(Processor):
    def __init__(self, inout):
        super(AbstractProcessor, self).__init__(inout)
        self.Result = True
        self.Abstract = ""

    def process(self):
        if not os.path.exists(self.InOut.dir_text):
            Processor.process(self)
        search_start = b"Abstract Start"
        search_end = b"Abstract End"
        with open(self.InOut.dir_text, 'rb') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if search_start in lines[i]:
                    start = i + 1
                    break
            for j in range(start, len(lines)):
                if search_end in lines[j]:
                    end = j
                    break
            for k in range(start, end):
                self.Abstract = self.Abstract + lines[k].decode('utf-8')
        return self.Result

    def resultObject(self):
        return self.Abstract

    # UI show abstract
    def showOnWindow(self, parserWindow):
        parserWindow.set_abstract(self.Abstract)

    def updateFromView(self, parserWindow):
        self.Abstract = parserWindow.get_abstract()

    def drawToPdf(self, paragraphs):
        P0 = Paragraph("Abstract", self.styleSheet['Customer_Bold'])
        paragraphs.append(P0)
        for i in range(len(self.Abstract.split('\n'))):
            Pi = Paragraph(self.Abstract.split('\n')[i], self.styleSheet['Customer_Normal'])
            paragraphs.append(Pi)

class TitleProcessor(Processor):
    def __init__(self, inout):
        super(TitleProcessor, self).__init__(inout)
        self.Result = True
        self.Title = ""

    def process(self):
        if not os.path.exists(self.InOut.dir_text):
            Processor.process(self)
        search_start = b"Title Start"
        search_end = b"Title End"
        with open(self.InOut.dir_text, 'rb') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if search_start in lines[i]:
                    start = i + 1
                    break
            for j in range(start, len(lines)):
                if search_end in lines[j]:
                    end = j
                    break
            for k in range(start, end):
                self.Title = self.Title + lines[k].decode('utf-8')
        return self.Result

    def resultObject(self):
        return self.Title

    # UI show title
    def showOnWindow(self, parserWindow):
        parserWindow.set_title(self.Title)

    def updateFromView(self, parserWindow):
        self.Title = parserWindow.get_title()

    def drawToPdf(self, paragraphs):
        P0 = Paragraph('\n', self.styleSheet['Customer_Title'])
        P1 = Paragraph(self.Title, self.styleSheet['Customer_Title'])
        paragraphs.append(P1)
        paragraphs.append(P0)

class KeywordsProcessor(Processor):
    def __init__(self, inout):
        super(KeywordsProcessor, self).__init__(inout)
        self.Result = True
        self.Keywords = ""

    def process(self):
        if not os.path.exists(self.InOut.dir_text):
            Processor.process(self)
        search_start = b"Keywords Start"
        search_end = b"Keywords End"
        with open(self.InOut.dir_text, 'rb') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if search_start in lines[i]:
                    start = i + 1
                    break
            for j in range(start, len(lines)):
                if search_end in lines[j]:
                    end = j
                    break
            for k in range(start, end):
                self.Keywords = self.Keywords + lines[k].decode('utf-8')
        return self.Result

    def resultObject(self):
        return self.Keywords

    # ui show keywords
    def showOnWindow(self, parserWindow):
        parserWindow.set_keywords(self.Keywords)

    def updateFromView(self, parserWindow):
        self.Keywords = parserWindow.get_keywords()

    def drawToPdf(self, paragraphs):
        P0 = Paragraph("Keywords", self.styleSheet['Customer_Bold'])
        paragraphs.append(P0)
        for i in range(len(self.Keywords.split('\n'))):
            Pi = Paragraph(self.Keywords.split('\n')[i], self.styleSheet['Customer_Normal'])
            paragraphs.append(Pi)

class CommentsProcessor(Processor):
    def __init__(self, inout):
        super(CommentsProcessor, self).__init__(inout)
        self.Result = True
        self.Comments = ""

    def process(self):
        if not os.path.exists(self.InOut.dir_text):
            Processor.process(self)
        search_start = b"Subject Start"
        search_end = b"Subject End"
        with open(self.InOut.dir_text, 'rb') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if search_start in lines[i]:
                    start = i + 1
                    break
            for j in range(start, len(lines)):
                if search_end in lines[j]:
                    end = j
                    break
            for k in range(start, end):
                self.Comments = self.Comments + lines[k].decode('utf-8')
        return self.Result

    def resultObject(self):
        return self.Comments

    # UI show abstract
    def showOnWindow(self, parserWindow):
        parserWindow.set_comments(self.Comments)

    def updateFromView(self, parserWindow):
        self.Comments = parserWindow.get_comments()

    def drawToPdf(self, paragraphs):
        P0 = Paragraph("Comments", self.styleSheet['Customer_Bold'])
        paragraphs.append(P0)
        for i in range(len(self.Comments.split('\n'))):
            Pi = Paragraph(self.Comments.split('\n')[i], self.styleSheet['Customer_Normal'])
            paragraphs.append(Pi)

class ImageProcessor(Processor):
    def __init__(self, inout):
        super(ImageProcessor, self).__init__(inout)
        self.Result = True
        self.Images = []

    # process images
    def process(self):
        if not os.path.exists(self.InOut.dir_images):
            Processor.process(self)
        if len(os.listdir(self.InOut.dir_images)) == 0:
            Processor.process(self)
        self.Images = []
        img_list = os.listdir(self.InOut.dir_images)
        try:
            img_list.sort(key=lambda x: float(x[:-4]))
        except ValueError:
            img_list.sort()
        for file in img_list:
            file_path = os.path.join(self.InOut.dir_images, file)
            self.Images.append(file_path)
        return self.Images

    def resultObject(self):
        return self.Images

    # ui show Image
    def showOnWindow(self, parserWindow):
        parserWindow.set_images(self.Images)

    def updateFromView(self, parserWindow):
        self.Images = parserWindow.get_images()

    def drawToPdf(self, paragraphs):
        P0 = Paragraph("Images", self.styleSheet['Customer_Bold'])
        P1 = Paragraph('\n', self.styleSheet['Customer_Normal'])
        paragraphs.append(P0)
        for img in self.Images:
            i = Image(img,6 * inch, 3 * inch,kind='proportional')
            paragraphs.append(i)
            paragraphs.append(P1)

class AllProcessor:
    def __init__(self, pdf):
        self.inout = InOut(pdf)
        self.processors = [TitleProcessor(self.inout),CommentsProcessor(self.inout),
                           AbstractProcessor(self.inout),KeywordsProcessor(self.inout),
                           ImageProcessor(self.inout)]

    def extract(self):
        for proc in self.processors:
            proc.process()

    def showOnWindow(self, parserWindow):
        for proc in self.processors:
            proc.showOnWindow(parserWindow)

    def updateFromView(self, parserWindow):
        for proc in self.processors:
            proc.updateFromView(parserWindow)

    def drawToPdf(self):
        doc = SimpleDocTemplate(self.inout.dir_pdf)
        paragraphs = []
        Story = []
        for proc in self.processors:
            proc.drawToPdf(paragraphs)
        for para in paragraphs:
            Story.append(para)
        doc.build(Story)