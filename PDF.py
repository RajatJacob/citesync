import fitz
import pandas as pd
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import requests
from functools import lru_cache
from pydantic import BaseModel


@lru_cache(maxsize=128)
def fetch_crossref(query: str):
    url = ('http://api.crossref.org/works?query.bibliographic="' +
           query + '"&rows=1')
    response = requests.get(url)
    data = response.json()
    return data


class PDFFile(BaseModel):
    file_path: str

    def scrape(self):
        results = []
        pdf = fitz.open(self.file_path)
        for page in pdf:
            text = page.get_text("dict")
            blocks = text["blocks"]
            for block in blocks:
                if "lines" in block.keys():
                    spans = block['lines']
                    for span in spans:
                        data = span['spans']
                        for lines in data:
                            results.append(
                                (lines['text'], lines['size'], lines['font']))
        pdf.close()
        out = pd.DataFrame(results, columns=["text", "size", "font"])
        out['text'] = out['text'].str.strip()
        return out.dropna()

    def get_paper_text_by_size(self):
        df = self.scrape()
        return df.groupby("size")\
            .apply(lambda x: x['text'].str.strip().str.cat(sep=" "))

    # def get_paper_title(self):
    #     return self.get_paper_text_by_size()\
    #         .sort_index(ascending=False).iloc[0]

    # def get_paper_author(self):
    #     return self.get_paper_text_by_size()\
    #         .sort_index(ascending=False).iloc[1]

    def get_metadata(self):
        fp = open(self.file_path, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        info = doc.info
        if len(info) > 0:
            return info[0]

    def get_crossref(self):
        metadata = self.get_metadata()
        if not metadata:
            return None
        title = metadata.get("Title")
        author = metadata.get("Author")
        if not title:
            return None
        query = ', '.join(map(str, [title, author]))
        data = fetch_crossref(query)
        return data

    def get_crossref_item(self):
        crossref = self.get_crossref()
        if not crossref:
            raise ValueError('No Crossref found!')
        return crossref['message']['items'][0]

    def get_doi(self):
        return str(self.get_crossref_item()['DOI'])

    def get_paper_title(self):
        return str(self.get_crossref_item()['title'][0])

    def get_paper_authors(self):
        out = []
        authors = self.get_crossref_item()['author']
        for author in authors:
            out.append({'given': author.get('given'),
                       'family': author.get('family')})
        return out

    def get_references(self):
        try:
            return self.get_crossref_item()['reference']
        except ValueError:
            return []

    def get_publisher(self):
        return self.get_crossref_item()['publisher']

    def get_publish_date(self):
        year, month = self.get_crossref_item()['published']['date-parts'][0]
        return {'year': year, 'month': month}

    def get_subject(self):
        return self.get_crossref_item()['container-title'][0]
