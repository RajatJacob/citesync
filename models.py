from neomodel import (
    config, StructuredNode, StringProperty, RelationshipFrom,
    RelationshipTo, StructuredRel, IntegerProperty, ZeroOrOne
)
config.DATABASE_URL = 'bolt://neo4j:password@10.0.0.10:7687'


class Author(StructuredNode):
    given_name = StringProperty()
    family_name = StringProperty()
    papers = RelationshipTo('Paper', 'WROTE')


class Publisher(StructuredNode):
    name = StringProperty(unique_index=True)
    papers = RelationshipTo('Paper', 'PUBLISHED')


class Paper(StructuredNode):
    doi = StringProperty(unique_index=True)
    title = StringProperty()
    authors = RelationshipFrom('Author', 'WROTE')
    cites = RelationshipTo('Paper', 'CITES')
    publisher = RelationshipFrom('Publisher', 'PUBLISHED')
    year = IntegerProperty()
    month = IntegerProperty()
    subject = StringProperty()

    def pre_save(self):
        self.doi = str(self.doi).upper()
