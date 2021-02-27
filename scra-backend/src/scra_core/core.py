class SemanticManager(object):
    def __init__(self, onto):
        self.onto = onto

    def get_directives_for_region(self, region: str) -> set:
        """

        :param region:
        :return:
        """

        qq = f"""
        PREFIX P: <{self.onto.iri}>
        SELECT ?x WHERE {{
        P:{region} P:hasDirective ?x.}}
        """

        return self.onto.make_query(qq)
