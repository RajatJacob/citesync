from PDF import PDFFile
from models import Paper, Author


def get_or_create_paper(doi: str, title=None) -> Paper:
    doi = str(doi).upper()
    paper = Paper.nodes.get_or_none(doi=doi)
    if paper is None:
        paper = Paper(doi=doi, title=title).save()
    return paper


def add_citations(paper: Paper, file_path: str):
    pdf = PDFFile(file_path=file_path)
    references = pdf.get_references()
    for reference in references:
        assert type(reference) is dict
        if 'DOI' in reference:
            ref_paper = get_or_create_paper(
                doi=reference['DOI'],
                title=reference.get('title')
            )
            ref_paper.cites.connect(paper)


def get_paper_details(file_path: str):
    pdf = PDFFile(file_path=file_path)
    doi = pdf.get_doi()
    title = pdf.get_paper_title()
    doi = pdf.get_doi()
    if doi is None:
        return
    authors = pdf.get_paper_authors()
    paper = get_or_create_paper(doi=doi, title=title)
    for author_details in authors:
        m = {
            'given_name': author_details.get("given"),
            'family_name': author_details.get("family")
        }
        author = Author.nodes.get_or_none(**m)
        if author is None:
            author = Author(**m).save()
        paper.authors.connect(author)
    add_citations(paper, file_path)
    return paper


if __name__ == '__main__':
    for i in range(1, 13):
        file_path = f'/tmp/paper{i}.pdf'
        print(file_path)
        paper = get_paper_details(file_path)
        # print(paper)
        # print(paper.authors.all())
