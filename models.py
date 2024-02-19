from neomodel import (
    config, StructuredNode, StringProperty, RelationshipFrom,
    RelationshipTo, UniqueIdProperty
)
config.DATABASE_URL = 'bolt://neo4j:password@10.0.0.10:7687'


class Author(StructuredNode):
    given_name = StringProperty()
    family_name = StringProperty()
    papers = RelationshipTo('Paper', 'WROTE')


class Paper(StructuredNode):
    doi = StringProperty(unique_index=True)
    title = StringProperty()
    authors = RelationshipFrom('Author', 'WROTE')
    cites = RelationshipTo('Paper', 'CITES')

    def pre_save(self):
        self.doi = str(self.doi).upper()
