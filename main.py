from PDF import PDFFile
from models import Paper, Author, Publisher


def get_or_create_paper(doi: str, **kwargs) -> Paper:
    doi = str(doi).upper()
    paper = Paper.nodes.get_or_none(doi=doi)
    if paper is None:
        paper = Paper(doi=doi, **kwargs).save()
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
            paper.cites.connect(ref_paper)


def get_paper_details(file_path: str):
    pdf = PDFFile(file_path=file_path)
    doi = pdf.get_doi()
    title = pdf.get_paper_title()
    doi = pdf.get_doi()
    publisher = pdf.get_publisher()
    published = pdf.get_publish_date()
    if doi is None:
        return
    authors = pdf.get_paper_authors()
    paper = get_or_create_paper(doi=doi, title=title)
    if publisher:
        publisher_node = Publisher.nodes.get_or_none(name=publisher)
        if publisher_node is None:
            publisher_node = Publisher(name=publisher).save()
        paper.publisher.connect(
            publisher_node,
            dict(published)
        )
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
    for i in range(1, 15):
        file_path = f'papers/paper{i}.pdf'
        try:
            print(file_path)
            paper = get_paper_details(file_path)
        except ValueError as e:
            print(f"Paper {file_path} failed.", e)
        # print(paper)
        # print(paper.authors.all())
